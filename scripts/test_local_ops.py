import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import local_ops


class SnapshotValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root / "snapshot"
        self.folder.mkdir()
        for name in ("database.dump", "media.tar.gz"):
            (self.folder / name).write_bytes(b"fixture-not-production")
        self.manifest = {"format": 1, "scope": "local-development-only", "hashes": {
            name: local_ops.digest(self.folder / name) for name in ("database.dump", "media.tar.gz")}}
        (self.folder / "manifest.json").write_text(json.dumps(self.manifest))
        self.backup = patch.object(local_ops, "backup_root", return_value=self.root)
        self.backup.start()

    def tearDown(self):
        self.backup.stop()
        self.temp.cleanup()

    def test_accepts_complete_untampered_snapshot(self):
        folder, _ = local_ops.verified_snapshot(self.folder)
        self.assertEqual(folder, self.folder)

    def test_refuses_modified_dump(self):
        (self.folder / "database.dump").write_bytes(b"corrupted")
        with self.assertRaises(RuntimeError):
            local_ops.verified_snapshot(self.folder)

    def test_refuses_failed_snapshot(self):
        (self.folder / "FAILED.txt").touch()
        with self.assertRaises(RuntimeError):
            local_ops.verified_snapshot(self.folder)

    def test_refuses_caller_selected_path_outside_backup_root(self):
        with self.assertRaises(RuntimeError):
            local_ops.verified_snapshot(self.root.parent)


if __name__ == "__main__":
    unittest.main()
