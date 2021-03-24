#!/usr/bin/python3

import argparse
import urllib.request
from launchpadlib.launchpad import Launchpad


def _lp_get_changelog_url(args):
    launchpad = Launchpad.login_anonymously(
        'ubuntu-package-changelog',
        'production', version='devel')
    ubuntu = launchpad.distributions["ubuntu"]
    ubuntu_archive = ubuntu.main_archive

    lp_series = ubuntu.getSeries(name_or_version=args.series)
    package_published_sources = ubuntu_archive.getPublishedSources(
        exact_match=True,
        source_name=args.package,
        pocket=args.pocket,
        distro_series=lp_series,
        status="Published",
        order_by_date=True)
    return package_published_sources[0].changelogUrl()


def _parser():
    parser = argparse.ArgumentParser(
        description='Ubuntu package changelog finder')
    parser.add_argument('--lines', help='number of lines to get from the changelog. '
                        '0 mean all. Default: %(default)s', type=int, default=0)
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
    with urllib.request.urlopen(changelog_url) as response:
        for count, line in enumerate(response.readlines()):
            if args.lines > 0 and count > args.lines:
                break
            print(line.rstrip().decode('utf-8'))


if __name__ == '__main__':
    main()
