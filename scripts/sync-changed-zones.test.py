import runpy
import unittest
from pathlib import Path

select = runpy.run_path(str(Path(__file__).with_name('sync-changed-zones.py')))['changed_zones']


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


if __name__ == '__main__':
    unittest.main()
