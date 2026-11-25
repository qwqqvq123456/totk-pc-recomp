#!/usr/bin/env python3
"""Write the fork's changelog and the release notes of a sync tag: one section per upstream sync.

`add` runs at the end of .github/workflows/sync-upstream.yml, after valentderah/totk-pc-recomp has been merged into the
fork's main. `notes` runs in .github/workflows/release.yml and turns the section of that tag into the release body, so the
release, the changelog and the tag always say the same thing.

    python .github/scripts/changelog.py add --from <sha> --to <sha> --version 0.3.1 --tag v0.3.1-sync.1
    python .github/scripts/changelog.py notes --tag v0.3.1-sync.1 [--out release-notes.md]

Upstream has no changelog and writes plain-sentence commit subjects (AGENTS.md), so there is nothing to group: the section
is the list of commits the sync brought in, oldest first, each with its upstream link. Standard library only: the
workflows run it before any Python environment is set up.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / 'CHANGELOG.md'
UPSTREAM = os.environ.get('UPSTREAM_REPO', 'valentderah/totk-pc-recomp')
UPSTREAM_URL = 'https://github.com/' + UPSTREAM

HEADER = """# Changelog

This fork follows [`%(upstream)s`](%(url)s) and adds nothing of its own to the code.
Whenever the upstream branch moves, [`.github/workflows/sync-upstream.yml`](.github/workflows/sync-upstream.yml) merges it,
writes the section below and pushes the tag `v<version>-sync.<n>`, where `<version>` is upstream's `VERSION` file at that
commit and `<n>` counts the syncs since that version changed. The tag's release notes are the section itself, published by
[`.github/workflows/release.yml`](.github/workflows/release.yml).

Upstream writes plain-sentence commit subjects, so a section is the list of commits the sync brought in, oldest first, with
the pull requests they came from. Upstream's own releases are on
[its releases page](%(url)s/releases).

""" % {'upstream': UPSTREAM, 'url': UPSTREAM_URL}


def git(*args, check=True):
    """Run git in the repository, returning its stdout."""
    done = subprocess.run(('git',) + args, cwd=ROOT, capture_output=True, text=True)
    if check and done.returncode != 0:
        sys.exit('git %s failed:\n%s' % (' '.join(args), done.stderr.strip()))
    return done.stdout


def short(sha):
    return sha[:7] if sha else ''


def commit_link(sha):
    return '[`%s`](%s/commit/%s)' % (short(sha), UPSTREAM_URL, sha)


def entry(sha):
    """One bullet: the subject, then the upstream commit it came from."""
    subject = git('show', '-s', '--format=%s', sha).strip().splitlines()[0]
    subject = re.sub(r'\s+', ' ', subject)[:200].rstrip()
    return '- %s ([%s](%s/commit/%s))' % (subject, short(sha), UPSTREAM_URL, sha)


def imported_commits(start, end):
    """The non-merge commits in start..end, oldest first; upstream's history is linear enough for --reverse."""
    if not start or not end or start == end:
        return []
    out = git('log', '--no-merges', '--reverse', '--format=%H', '%s..%s' % (start, end))
    return [line.strip() for line in out.splitlines() if line.strip()]


def merged_pull_requests(start, end):
    """The pull request numbers in the merge commits of start..end, without repeats, oldest first."""
    numbers = []
    if not start or not end or start == end:
        return numbers
    out = git('log', '--merges', '--reverse', '--format=%s', '%s..%s' % (start, end))
    for line in out.splitlines():
        found = re.match(r'Merge pull request #(\d+)', line.strip())
        if found and found.group(1) not in numbers:
            numbers.append(found.group(1))
    return numbers


def section(start, end, version, tag, date):
    """The markdown of one sync: what upstream moved to, the commits it brought in, the pull requests they came from."""
    commits = imported_commits(start, end)
    pulls = merged_pull_requests(start, end)
    lines = ['## %s (%s)' % (tag.lstrip('v') or version, date), '']

    if commits:
        lines.append('Upstream `%s` moved from %s to %s: %d commit%s.' %
                     (UPSTREAM, commit_link(start), commit_link(end), len(commits), '' if len(commits) == 1 else 's'))
    else:
        lines.append('Upstream `%s` was re-synced at %s; no new commits.' % (UPSTREAM, commit_link(end)))
    lines.append('')

    lines.extend(entry(sha) for sha in commits)
    if commits:
        lines.append('')
    if pulls:
        links = ', '.join('[#%s](%s/pull/%s)' % (n, UPSTREAM_URL, n) for n in pulls)
        lines.append('Pull requests merged: %s' % links)
        lines.append('')

    if start and end and start != end:
        lines.append('[Compare %s...%s](%s/compare/%s...%s)' % (short(start), short(end), UPSTREAM_URL, start, end))
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def read_changelog():
    return CHANGELOG.read_text(encoding='utf-8') if CHANGELOG.is_file() else ''


def write_changelog(text):
    CHANGELOG.write_text(text, encoding='utf-8', newline='\n')


def inserted(text, block):
    """`block` at the top of the sections, under the header; the file's header is created when it is missing."""
    if not text.strip():
        return HEADER + block
    head, sep, rest = text.partition('\n## ')
    if not sep:
        return text.rstrip() + '\n\n' + block
    return head.rstrip('\n') + '\n\n' + block + '\n' + sep.lstrip('\n') + rest


def add(args):
    """Prepend the section of this sync and print it, for the job summary."""
    current = read_changelog()
    if re.search(r'^## %s\b' % re.escape(args.tag.lstrip('v')), current, re.MULTILINE):
        print('CHANGELOG.md already has a section for %s; leaving it alone.' % args.tag, file=sys.stderr)
        print(section_text(args.tag, current))
        return 0
    block = section(args.start, args.end, args.version, args.tag, args.date)
    write_changelog(inserted(current, block))
    print(block)
    return 0


def section_text(tag, text):
    """The body of the section whose heading names `tag`, or ''."""
    match = re.search(r'^## %s\b.*?(?=^## |\Z)' % re.escape(tag.lstrip('v')), text, re.MULTILINE | re.DOTALL)
    if not match:
        return ''
    body = match.group(0)[match.group(0).index('\n') + 1:]
    return body.strip() + '\n'


def notes(args):
    """Write the release notes of `tag`: its changelog section, else what git knows about the tag."""
    text = read_changelog()
    body = section_text(args.tag, text)
    if not body:
        previous = git('describe', '--tags', '--abbrev=0', '%s^' % args.tag, check=False).strip()
        end = git('rev-parse', args.tag).strip()
        start = git('rev-parse', previous).strip() if previous else ''
        body = section(start, end, '', args.tag, args.date)
        body = body.split('\n', 1)[1].lstrip('\n')   # drop the heading: GitHub shows the release name above it
    if not body.endswith('\n'):
        body += '\n'
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    blob = 'https://github.com/%s/blob/main/' % repo if repo else '../blob/main/'
    body += ('\n---\n\nThis archive is the source of a fork that follows upstream, tagged at the sync that produced this\n'
             'release; it holds no game files. The setup (`TotK-Setup-*`) is built from these sources on a machine that has\n'
             'your own game files: [docs/installer.md](%s) and [docs/building.md](%s). Upstream\'s ready-made installers\n'
             'are on [its releases page](%s/releases).\n' % (blob + 'docs/installer.md', blob + 'docs/building.md', UPSTREAM_URL))
    if args.out:
        Path(args.out).write_text(body, encoding='utf-8', newline='\n')
        print('wrote %s (%d bytes)' % (args.out, len(body.encode('utf-8'))))
    else:
        sys.stdout.write(body)
    return 0


def main(argv):
    default_date = os.environ.get('SYNC_DATE') or subprocess.run(
        ('date', '-u', '+%Y-%m-%d'), capture_output=True, text=True).stdout.strip()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)

    add_parser = commands.add_parser('add', help='prepend the section of a finished sync to CHANGELOG.md')
    add_parser.add_argument('--from', dest='start', default='', help='upstream commit the fork was at (may be empty)')
    add_parser.add_argument('--to', dest='end', required=True, help='upstream commit the sync merged')
    add_parser.add_argument('--version', default='', help="upstream's VERSION at that commit")
    add_parser.add_argument('--tag', required=True, help='the tag of this sync, v<version>-sync.<n>')
    add_parser.add_argument('--date', default=default_date, help='the date of the section, YYYY-MM-DD')
    add_parser.set_defaults(run=add)

    notes_parser = commands.add_parser('notes', help='write the release notes of a tag')
    notes_parser.add_argument('--tag', required=True)
    notes_parser.add_argument('--out', default='', help='write here instead of stdout')
    notes_parser.add_argument('--date', default=default_date)
    notes_parser.set_defaults(run=notes)

    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
