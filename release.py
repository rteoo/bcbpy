"""Release an already merged bcbpy version; never bumps or commits main."""
from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
REPO = 'rteoo/bcbpy'
ROOT = Path(__file__).resolve().parent
GATES = [(sys.executable, '-m', 'pytest', '-m', 'not integration', '-v'), (sys.executable, '-m', 'build')]

def command(*args: str, capture=True):
    r = subprocess.run(args, text=True, capture_output=capture, check=False)
    if r.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}")
    return r.stdout.strip() if capture else ''

def repo_name(url):
    from urllib.parse import urlparse
    value = url.strip()
    if value.startswith('git@github.com:'):
        path = value[len('git@github.com:'):]
    else:
        parsed = urlparse(value)
        if parsed.hostname != 'github.com' or parsed.scheme not in ('https', 'ssh'):
            raise RuntimeError('origin must use the pinned GitHub host')
        path = parsed.path.lstrip('/')
    return path.removesuffix('.git').rstrip('/')

def tag_state(tag, head):
    remote = command('git', 'ls-remote', '--tags', 'origin', f'refs/tags/{tag}', f'refs/tags/{tag}^{{}}', **GIT_CWD)
    refs = {}
    for line in remote.splitlines():
        sha, ref = line.split()
        refs[ref] = sha
    target = refs.get(f'refs/tags/{tag}^{{}}') or refs.get(f'refs/tags/{tag}')
    if target and target != head:
        raise RuntimeError(f'existing {tag} does not point at {head}')
    local = command('git', 'for-each-ref', '--format=%(objectname)', f'refs/tags/{tag}', **GIT_CWD)
    if local and command('git', 'rev-parse', f'{tag}^{{commit}}', **GIT_CWD) != head:
        raise RuntimeError(f'local {tag} points at a different commit')
    return (bool(target), bool(local))
RELEASE_ROOT = ROOT
GIT_CWD = {}

def tag_version(tag):
    if not re.fullmatch(r'v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)', tag):
        raise ValueError('tag must match vX.Y.Z')
    return tag[1:]

def manifest_version():
    m = re.search('^__version__\\s*=\\s*["\\\']([^"\\\']+)', (ROOT / 'bcbpy/__init__.py').read_text(encoding='utf-8'), re.M)
    if not m:
        raise RuntimeError('bcbpy/__init__.py has no __version__')
    return m.group(1)

def guard():
    os.chdir(ROOT)
    if repo_name(command('git', 'remote', 'get-url', 'origin')) != REPO:
        raise RuntimeError('origin does not match the pinned GitHub repository')
    if command('git', 'branch', '--show-current') != 'main':
        raise RuntimeError('release must run on main')
    if command('git', 'status', '--porcelain'):
        raise RuntimeError('checkout changes, including untracked files, must be resolved first')
    command('git', 'fetch', '--quiet', '--tags', 'origin', 'main', capture=False)
    head = command('git', 'rev-parse', 'HEAD')
    if head != command('git', 'rev-parse', 'origin/main'):
        raise RuntimeError('HEAD must equal freshly fetched origin/main')
    return head

def gh_command(tag, head):
    return ['gh', 'release', 'create', tag, '--repo', REPO, '--target', head, '--verify-tag', '--generate-notes', '--title', tag]

def check_release_absent(tag):
    accessible = command('gh', 'api', f'repos/{REPO}', '--jq', '.full_name', **GIT_CWD)
    if accessible.lower() != REPO.lower():
        raise RuntimeError('could not verify access to the release repository')
    result = subprocess.run(('gh', 'release', 'view', tag, '--repo', REPO), text=True, capture_output=True, check=False, cwd=RELEASE_ROOT)
    if result.returncode == 0:
        raise RuntimeError(f'GitHub release {tag} already exists')
    error = (result.stderr or '').lower()
    if '404' not in error and 'release not found' not in error:
        raise RuntimeError('could not determine GitHub release state')

def verify_remote_tag(tag, head):
    remote_exists, _ = tag_state(tag, head)
    if not remote_exists:
        raise RuntimeError(f'remote {tag} is not visible at {head} after push')

def main(argv=None):
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    tag_version(args.tag)
    os.chdir(RELEASE_ROOT)
    if manifest_version() != tag_version(args.tag):
        raise RuntimeError('manifest version must already match --tag; bump it through a PR')
    head = guard()
    tag_state(args.tag, head)
    check_release_absent(args.tag)
    for gate in GATES:
        command(*gate, capture=False)
    if guard() != head or manifest_version() != tag_version(args.tag):
        raise RuntimeError('checkout or version moved while gates were running')
    tag_state(args.tag, head)
    if args.dry_run:
        print(f'Dry run: local gates passed for {args.tag} at {head}.')
        print('Would push only this tag and create a GitHub release; deployment remains separate.')
        return 0
    if input(f'Type {args.tag} to release {head}: ').strip() != args.tag:
        raise RuntimeError('release not confirmed')
    if guard() != head or manifest_version() != tag_version(args.tag):
        raise RuntimeError('checkout or version moved after confirmation')
    remote_exists, local_exists = tag_state(args.tag, head)
    check_release_absent(args.tag)
    if not remote_exists:
        if not local_exists:
            command('git', 'tag', '--annotate', args.tag, '--message', f'Release {args.tag}', head, capture=False, **GIT_CWD)
        command('git', 'push', 'origin', f'refs/tags/{args.tag}:refs/tags/{args.tag}', capture=False, **GIT_CWD)
    verify_remote_tag(args.tag, head)
    # ceiling: GitHub cannot atomically reserve a tag SHA for release creation; protect release tags.
    command('gh', 'release', 'create', args.tag, '--repo', REPO, '--target', head, '--verify-tag', '--generate-notes', '--title', args.tag, capture=False, **GIT_CWD)
    return 0
if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, OSError, EOFError) as e:
        print(f'release: {e}', file=sys.stderr)
        raise SystemExit(1)
