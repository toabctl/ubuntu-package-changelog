#!/usr/bin/python3

import re
import sys
import argparse
import urllib.parse
import requests
from launchpadlib.launchpad import Launchpad

def _get_changelogs_ubuntu_com_changelog(package_name):
    """
    Return changelog for sourc package

    :param str package_name: Source package name
    :param list ppas: List of possible ppas package installed from
    :raises Exception: If changelog file could not be downloaded
    :return: changelog
    :rtype: str
    """

    package_prefix = package_name[0:1]
    # packages starting with 'lib' are special
    if package_name.startswith("lib"):
        package_prefix = package_name[0:4]

    # packages ending with ':amd64' are special
    if package_name.endswith(":amd64"):
        package_name = package_name[:-6]

    changelog_base_url = "http://changelogs.ubuntu.com/changelogs/pool/main"
    package_versions_url = "{}/{}/{}/?C=M;O=D".format(
        changelog_base_url,
        package_prefix,
        package_name,
        )

    versions_response = requests.get(package_versions_url)
    versions_html_raw = versions_response.text

    # Match "<a href="20181120/">20181120/</a> 20-Nov-2018 16:33"
    regex = re.compile(r"""<a\s+href="{}_(?P<version>.*?)/">{}_.*?/</a>""".format(package_name, package_name),
                       re.VERBOSE)

    latest_version = None

    for m in regex.finditer(versions_html_raw):
        latest_version = m.group("version")
        break


    # Changelog URL example http://changelogs.ubuntu.com/changelogs/pool/main/l/linux-gkeop/linux-gkeop_5.4.0-1048.51/changelog
    changelog_url = "{}/{}/{}/{}_{}/changelog".format(
        changelog_base_url,
        package_prefix,
        package_name,
        package_name,
        latest_version,
        )


    changelog_reponse = requests.get(changelog_url)
    changelog = changelog_reponse.text
    return changelog



def _lp_get_changelog_url(args, lp):
    ubuntu = lp.distributions["ubuntu"]
    pocket = args.pocket
    if args.ppa:
        ppa_owner, ppa_name = args.ppa.split('/')
        archive = lp.people[ppa_owner].getPPAByName(name=ppa_name)
        if args.pocket != 'Release':
            print('using pocket "Release" when using a PPA ...')
            pocket = 'Release'
    else:
        archive = ubuntu.main_archive

    lp_series = ubuntu.getSeries(name_or_version=args.series)
    if args.binary_package and args.binary_package_architecture:
        # a binary package name was specified - find the source package name
        # before getting changelog.
        lp_arch_series = lp_series.getDistroArchSeries(
            archtag=args.binary_package_architecture)
        binaries = archive.getPublishedBinaries(
            exact_match=True,
            binary_name=args.package,
            pocket=pocket,
            distro_arch_series=lp_arch_series,
            status="Published",
            order_by_date=True,
        )
        if len(binaries):
            for binary in binaries:
                print(binary.source_package_version)
                print(binary.binary_package_version)
            # now get the source package name so we can get the changelog
            source_package_name = binaries[0].source_package_name
    else:
        source_package_name = args.package
    sources = archive.getPublishedSources(
        exact_match=True,
        source_name=source_package_name,
        pocket=pocket,
        distro_series=lp_series,
        status="Published",
        order_by_date=True)
    if len(sources) == 1:
        return sources[0].changelogUrl()
    else:
        return None


def _args_validate_ppa_name(value):
    if value.count('/') != 1:
        raise argparse.ArgumentTypeError('ppa must have the format "owner/ppa-name"')
    return value


def _parser():
    parser = argparse.ArgumentParser(
        description='Ubuntu package changelog finder')
    parser.add_argument('--lp-user', help='Launchpad username', default=None)
    parser.add_argument('--ppa', help='Search for a package in the given PPA instead'
                        'of the Ubuntu archive. Given PPA must have the '
                        'format "owner/ppa-name". Eg. "toabctl/testing"',
                        type=_args_validate_ppa_name)
    parser.add_argument('--entries', help='number of changelog entries to get from the '
                        'changelog. 0 mean all. Default: %(default)s', type=int, default=1)
    parser.add_argument('--binary-package',
                        help='Set this option if you wish to get the changelog for the '
                        'source package of the specified binary package name. '
                        'Default: %(default)s',
                        action='store_true', default=False)
    parser.add_argument('--binary-package-architecture',
                        help='The architecture of the binary package you wish '
                             'to retrieve changelog for. '
                        'Default: %(default)s',
                        default='amd64')
    parser.add_argument('--use-changelogs-ubuntu-com',
                        help='Use changelog.ubuntu.com to get latest changelog '
                             'for the source package. This is useful if it is '
                             'a kernel that was copied from a private PPA, '
                             'for example during an embargoed CVE. This option '
                             'assumes that the package is in the main Ubuntu '
                             'archive',
                        action='store_true', default=False)
    parser.add_argument('series', help='the Ubuntu series eg. "20.04" or "focal"')
    parser.add_argument('pocket',
                        choices=['Release', 'Security', 'Updates', 'Proposed', 'Backports'],
                        help='The pocket to search for. Default: %(default)s')
    parser.add_argument('package', help='the source package name')
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()
    if not args.use_changelogs_ubuntu_com:
        if args.lp_user:
            lp = Launchpad.login_with(
                args.lp_user,
                'production', version='devel')
        else:
            lp = Launchpad.login_anonymously(
                'production', version='devel')

        changelog_url = _lp_get_changelog_url(args, lp)
        if not changelog_url:
            print('no changelog found')
            sys.exit(0)

        url = lp._root_uri.append(urllib.parse.urlparse(changelog_url).path.lstrip('/'))
        resp = lp._browser.get(url).decode('utf-8')
    else:
        resp = _get_changelogs_ubuntu_com_changelog(args.package)

    entry_count = 0
    for line in resp.splitlines():
        line = line.rstrip()
        if line.startswith(' -- '):
            entry_count += 1
        if args.entries > 0 and entry_count >= args.entries:
            print(line)
            break
        print(line)


if __name__ == '__main__':
    main()
