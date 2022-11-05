#!/usr/bin/python3

import re
import sys
import argparse
import urllib.parse
from lazr.restfulclient.errors import NotFound
from launchpadlib.launchpad import Launchpad


def _lp_get_changelog_url(sources):
    return sources.changelogUrl()


def _lp_get_sources(args, lp):
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
            source_package_name = binaries[0].source_package_name
            sources = _get_published_sources(archive,
                                             source_package_name,
                                             lp_series,
                                             pocket)
    return sources


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
    parser.add_argument('--highlight-cves',
                        help='Highlight the CVEs referenced in each individual changelog entry'
                             '. Default: %(default)s',
                        action='store_true')
    parser.add_argument('--highlight-cves-only',
                        help='Highlight the CVEs referenced in each individual changelog entry '
                             'but do NOT show the rest of the content of the changelog entry'
                             '. Default: %(default)s',
                        action='store_true')
    parser.add_argument('--highlight-cves-show-cve-description',
                        help='When highlighting CVEs, show the CVE description. '
                             '`--highlight-cves` or `--highlight-cve-only` '
                             'must also be used for this to take affect. Default: %(default)s',
                        action='store_true')
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

    sources = _lp_get_sources(args, lp)

    if len(sources) != 1:
        print('no changelog found')
        sys.exit(0)

    changelog_url = _lp_get_changelog_url(sources[0])
    source_package_name = sources[0].source_package_name

    url = lp._root_uri.append(urllib.parse.urlparse(changelog_url).path.lstrip('/'))
    resp = lp._browser.get(url).decode('utf-8')
    entry_count = 0
    changelog_entry_lines = []
    for line in resp.splitlines():
        line = line.rstrip()

        # this is the first line of a changelog entry. Find the version and reset lists for
        # changelog entry lines and changelog entry cves
        if source_package_name in line and line.startswith(source_package_name) and ' (' in line and ')' in line:
            individual_changelog_entry_lines = []
            individual_changelog_entry_cves = []
            individual_changelog_entry_source_package_version = line[line.index('(') + 1: line.index(')')]

        if (args.highlight_cves or args.highlight_cves_only) and 'CVE' in line:
            cve_pos = [(m.start(), m.end()) for m in re.finditer(r'CVE-\d+-\d+', line)]
            for start, end in cve_pos:
                cve = line[start:end].strip()
                if cve not in [individual_changelog_entry_cve['cve']
                               for individual_changelog_entry_cve in individual_changelog_entry_cves]:
                    cve_details = {}
                    cve_details['cve'] = cve
                    cve_details_lines = _get_cve_details(cve, lp)
                    cve_ubuntu_description = ''
                    cve_description = ''
                    for cve_details_line in cve_details_lines:
                        # only get the CVE description if the user has requested it
                        if args.highlight_cves_show_cve_description and not cve_ubuntu_description \
                                and cve_details_line.startswith('Ubuntu-Description:'):
                            # get the string in the line after the Ubuntu-Description: line
                            # while the next line is not 'Notes' keep appending to cve_description
                            while True:
                                next_line = next(cve_details_lines)
                                if next_line.startswith('Notes'):
                                    break
                                cve_ubuntu_description += next_line
                        if args.highlight_cves_show_cve_description and not cve_description \
                                and cve_details_line.startswith('Description:'):
                            # get the string in the line after the Description: line
                            # while the next line is not 'Notes' keep appending to cve_description
                            while True:
                                next_line = next(cve_details_lines)
                                if next_line.startswith('Ubuntu-Description:'):
                                    break
                                cve_description += next_line
                        if 'Priority:' in cve_details_line:
                            cve_details['cve_priority'] = cve_details_line.split('Priority:')[1].strip()
                    cve_details['cve_description'] = cve_ubuntu_description \
                        if cve_ubuntu_description else cve_description
                    individual_changelog_entry_cves.append(cve_details)

        individual_changelog_entry_lines.append(line)

        # the '--' string is used to separate entries in the changelog as it is the last line of a changelog entry
        # example "-- Maintainer Name <maintainer@email.com>  Mon, 17 Oct 2022 10:32:58 -0300"
        if line.startswith(' -- '):
            entry_count += 1
            if (args.highlight_cves or args.highlight_cves_only) and individual_changelog_entry_cves:
                individual_changelog_entry_lines.insert(1, '\n  CVEs addressed/mitigated in {} version {}:'.format(
                    source_package_name, individual_changelog_entry_source_package_version))
                cve_details_insertion_index_start = 2
                for individual_changelog_entry_cve in individual_changelog_entry_cves:
                    individual_changelog_entry_lines.insert(
                        cve_details_insertion_index_start,
                        '    {} ({} priority){}'.format(
                            individual_changelog_entry_cve['cve'],
                            individual_changelog_entry_cve['cve_priority'],
                            ': {}'.format(individual_changelog_entry_cve['cve_description'])
                            if args.highlight_cves_show_cve_description else ''))
                    cve_details_insertion_index_start += 1

            if args.highlight_cves_only:
                changelog_entry_lines.extend(individual_changelog_entry_lines[0:cve_details_insertion_index_start])
                changelog_entry_lines.extend(individual_changelog_entry_lines[-2:])
                changelog_entry_lines.append('\n')
            else:
                changelog_entry_lines.extend(individual_changelog_entry_lines)

        # If we have parsed all the entries we want, then we can stop parsing the changelog
        if args.entries > 0 and entry_count >= args.entries:
            break

    # print the lines in changlog_entry_lines
    print('\n'.join(changelog_entry_lines))


def _get_cve_details(cve, lp):
    # download the cve details and parse so we can get the CVE description and the CVE priority
    cve_details_lines = []
    possible_cve_detail_locations = ['active', 'retired', 'ignored']
    for possible_cve_detail_location in possible_cve_detail_locations:
        try:
            cve_details_url = 'https://git.launchpad.net/ubuntu-cve-tracker/plain/{}/{}'.format(
                possible_cve_detail_location, cve)
            cve_details_resp = lp._browser.get(cve_details_url).decode('utf-8')
            cve_details_lines = iter(cve_details_resp.splitlines())
            return cve_details_lines
        except NotFound:
            pass  # Keep trying until we find the cve details
    return cve_details_lines


if __name__ == '__main__':
    main()
