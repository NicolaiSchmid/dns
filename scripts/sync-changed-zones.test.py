import json
import os
import runpy
import tempfile
import subprocess
from unittest.mock import patch
import unittest
from pathlib import Path

module = runpy.run_path(str(Path(__file__).with_name('sync-changed-zones.py')))
select = module['changed_zones']


class ChangedZones(unittest.TestCase):
    def test_june_change_does_not_select_other_domains(self):
        self.assertEqual(select(['zones/general/modusservice.com.yaml', '.github/workflows/dns.yml']), ['modusservice.com.'])

    def test_sources_share_one_zone_and_deletions_are_selected(self):
        self.assertEqual(select(['zones/general/example.com.yaml', 'zones/private/example.com.yaml', 'zones/general/old.com.yaml']), ['example.com.', 'old.com.'])

    def test_config_changes_require_deliberate_manual_reconciliation(self):
        with self.assertRaises(ValueError):
            select(['production.yaml'])
        with self.assertRaises(ValueError):
            select(['zones/general/invalid/file.yaml'])
        self.assertEqual(select(['AGENTS.md']), [])

    def test_push_merge_and_pr_select_their_actual_diff(self):
        for event_name, event, refs in [
            ('push', {'before': 'a' * 40, 'after': 'b' * 40}, ['a' * 40, 'b' * 40]),
            ('pull_request', {'pull_request': {'base': {'sha': 'c' * 40}, 'head': {'sha': 'd' * 40}}}, ['c' * 40, 'd' * 40]),
        ]:
            with tempfile.TemporaryDirectory(prefix='dns-selection-936258ad-') as directory:
                event_file = Path(directory) / 'event.json'
                event_file.write_text(json.dumps(event))
                with patch.dict(os.environ, {'GITHUB_EVENT_NAME': event_name, 'GITHUB_EVENT_PATH': str(event_file), 'GITHUB_WORKSPACE': directory}), patch('sys.argv', ['sync-changed-zones.py', '--doit']), patch('subprocess.check_output', return_value='zones/general/modusservice.com.yaml\n.github/workflows/dns.yml\n') as diff, patch('subprocess.run') as sync:
                    sync.return_value.returncode = 0
                    module['main']()
                    git = ['git', '-c', 'safe.directory=' + directory, '-C', directory]
                    diff.assert_called_once_with([*git, 'diff', '--name-only', *refs, '--'], text=True)
                    sync.assert_any_call(['octodns-sync', '--config-file', 'production.yaml', '--doit', 'modusservice.com.'], check=True)

    def test_missing_event_commit_fetch_failure_never_syncs(self):
        with tempfile.TemporaryDirectory(prefix='dns-selection-936258ad-') as directory:
            event_file = Path(directory) / 'event.json'
            event_file.write_text(json.dumps({'before': 'a' * 40, 'after': 'b' * 40}))
            calls = []
            def run(args, **kwargs):
                calls.append(args)
                if 'fetch' in args:
                    raise subprocess.CalledProcessError(1, args)
                return subprocess.CompletedProcess(args, 1 if 'cat-file' in args else 0)
            with patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'push', 'GITHUB_EVENT_PATH': str(event_file), 'GITHUB_WORKSPACE': directory}), patch('sys.argv', ['sync-changed-zones.py', '--doit']), patch('subprocess.run', side_effect=run), patch('subprocess.check_output') as diff:
                with self.assertRaises(subprocess.CalledProcessError):
                    module['main']()
                diff.assert_not_called()
                self.assertFalse(any(args[0] == 'octodns-sync' for args in calls))

    def test_manual_dispatch_is_explicit_full_reconciliation(self):
        with patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'workflow_dispatch'}), patch('sys.argv', ['sync-changed-zones.py']), patch('subprocess.check_output') as diff, patch('subprocess.run') as sync:
            module['main']()
            diff.assert_not_called()
            sync.assert_called_once_with(['octodns-sync', '--config-file', 'production.yaml'], check=True)


if __name__ == '__main__':
    unittest.main()
