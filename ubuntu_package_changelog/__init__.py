#!/usr/bin/python3

import sys
import argparse
import urllib.request
from launchpadlib.launchpad import Launchpad


def _lp_get_changelog_url(args):
    launchpad = Launchpad.login_anonymously(
        'ubuntu-package-changelog',
        'production', version='devel')

    ubuntu = launchpad.distributions["ubuntu"]
    pocket = args.pocket
    if args.ppa:
        ppa_owner, ppa_name = args.ppa.split('/')
        archive = launchpad.people[ppa_owner].getPPAByName(name=ppa_name)
        if args.pocket != 'Release':
            print('using pocket "Release" when using a PPA ...')
            pocket = 'Release'
    else:
        archive = ubuntu.main_archive

    lp_series = ubuntu.getSeries(name_or_version=args.series)
    sources = archive.getPublishedSources(
        exact_match=True,
        source_name=args.package,
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
    parser.add_argument('package', help='the source package name')
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()
    changelog_url = _lp_get_changelog_url(args)
    if not changelog_url:
        print('no changelog found')
        sys.exit(0)

    with urllib.request.urlopen(changelog_url) as response:
        entry_count = 0
        for line in response.readlines():
            line = line.rstrip().decode('utf-8')
            if line.startswith(' -- '):
                entry_count += 1
            if args.entries > 0 and entry_count >= args.entries:
                print(line)
                break
            print(line)


if __name__ == '__main__':
    main()
