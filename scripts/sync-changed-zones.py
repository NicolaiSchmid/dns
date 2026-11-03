#!/usr/bin/env python3
"""Limit automatic DNS sync to changed zones; manual dispatch reconciles all."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def changed_zones(files):
    if 'production.yaml' in files:
        raise ValueError('Provider/zone configuration changed: review and use manual DNS Sync')
    zones = set()
    for name in files:
        if not name.startswith('zones/'):
            continue
        match = re.fullmatch(r'zones/[^/]+/([a-zA-Z0-9.-]+)\.yaml', name)
        if not match:
            raise ValueError('Unrecognized zone path: ' + name)
        zones.add(match[1] + '.')
    return sorted(zones)


def main():
    event_name = os.environ['GITHUB_EVENT_NAME']
    args = ['octodns-sync', '--config-file', 'production.yaml'] + sys.argv[1:]
    if event_name != 'workflow_dispatch':
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        if event_name == 'pull_request':
            base, head = event['pull_request']['base']['sha'], event['pull_request']['head']['sha']
        elif event_name == 'push':
            base, head = event['before'], event['after']
        else:
            raise ValueError('Unsupported event')
        workspace = os.environ['GITHUB_WORKSPACE']
        git = ['git', '-c', 'safe.directory=' + workspace, '-C', workspace]
        subprocess.run([*git, 'rev-parse', '--show-toplevel'], check=True)
        for ref in [base, head]:
            if not re.fullmatch(r'[0-9a-f]{40}', ref):
                raise ValueError('Invalid event commit')
            present = subprocess.run([*git, 'cat-file', '-e', ref + '^{commit}'], capture_output=True)
            if present.returncode:
                subprocess.run([*git, 'fetch', '--no-tags', 'origin', ref], check=True)
                subprocess.run([*git, 'cat-file', '-e', ref + '^{commit}'], check=True)
        files = subprocess.check_output([*git, 'diff', '--name-only', base, head, '--'], text=True).splitlines()
        zones = changed_zones(files)
        if not zones:
            print('No zone changes; nothing to synchronize')
            return
        args.extend(zones)
    subprocess.run(args, check=True)


if __name__ == '__main__':
    main()
