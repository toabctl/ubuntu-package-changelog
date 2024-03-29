#!/usr/bin/python3

import sys
import argparse
import urllib.parse
from launchpadlib.launchpad import Launchpad


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
    sources = _get_published_sources(archive,
                                     args.package,
                                     lp_series,
                                     pocket)
    if len(sources) == 0:
        print(f'INFO: No published sources found for {args.package} in {args.series} {args.pocket}')
        print('INFO: \tTrying to find a binary package with that name ...')
        # unable to find published sources for args.package.
        # Perhaps this is a binary package name so we can
        # do a lookup to see if there exists a source package for
        # args.package binary package.
        binaries = _get_binary_packages(archive,
                                        args.package,
                                        pocket)
        if len(binaries):
            # there were published binaries with this name.
            # now get the source package name so we can get the changelog
            for binary in binaries:
                source_package_name = binary.source_package_name
                sources = _get_published_sources(archive,
                                                 source_package_name,
                                                 lp_series,
                                                 pocket)
                if len(sources) > 0:
                    print(f'INFO: \tFound source package {source_package_name} for binary package '
                          f'{args.package} with published sources.')
                    print(f'INFO: \tChangelog for source package {source_package_name} will be parsed\n\n')
                    break
        else:
            print(f'INFO: \tNo published binaries found for {args.package} in {args.series} {args.pocket}\n\n')

    if len(sources) == 1:
        return sources[0].changelogUrl()
    else:
        return None


def _get_binary_packages(archive, binary_package_name, pocket):
    binaries = archive.getPublishedBinaries(
        exact_match=True,
        binary_name=binary_package_name,
        pocket=pocket,
        status="Published",
        order_by_date=True,
    )
    return binaries


def _get_published_sources(archive, source_package_name, lp_series, pocket):
    sources = archive.getPublishedSources(
        exact_match=True,
        source_name=source_package_name,
        pocket=pocket,
        distro_series=lp_series,
        status="Published",
        order_by_date=True)
    return sources


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
    parser.add_argument('series', help='the Ubuntu series eg. "20.04" or "focal"')
    parser.add_argument('pocket',
                        choices=['Release', 'Security', 'Updates', 'Proposed', 'Backports'],
                        help='The pocket to search for. Default: %(default)s')
    parser.add_argument('package', help='the source or binary package name')
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()
    if args.lp_user:
        lp = Launchpad.login_with(
            args.lp_user,
            'production', version='devel')
    else:
        lp = Launchpad.login_anonymously(
            'ubuntu-package-changelog',
            'production', version='devel')

    changelog_url = _lp_get_changelog_url(args, lp)
    if not changelog_url:
        print('No changelog found for binary or source package "{}" in {} {}'.format(
            args.package, args.series, args.pocket))
        sys.exit(0)

    url = lp._root_uri.append(urllib.parse.urlparse(changelog_url).path.lstrip('/'))
    resp = lp._browser.get(url).decode('utf-8')
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
