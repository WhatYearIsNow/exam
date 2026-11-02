import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AndroidUpdateManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (ROOT / "web/app-update.json").read_text(encoding="utf-8")
        )

    def test_channels_are_same_origin_apks_with_distinct_packages(self):
        channels = self.manifest["channels"]
        self.assertEqual(set(channels), {"stable", "preview"})
        self.assertEqual(channels["stable"]["packageName"], "com.tju.quizhub")
        self.assertEqual(
            channels["preview"]["packageName"], "com.tju.quizhub.preview"
        )
        for item in channels.values():
            with self.subTest(item=item["versionName"]):
                self.assertIsInstance(item["versionCode"], int)
                self.assertGreater(item["versionCode"], 0)
                self.assertTrue(item["versionName"])
                self.assertTrue(item["apkUrl"].startswith("/"))
                self.assertTrue(item["apkUrl"].endswith(".apk"))
                self.assertNotIn("//", item["apkUrl"])

    def test_preview_version_code_matches_build_number_scheme(self):
        preview = self.manifest["channels"]["preview"]
        base, build = preview["versionName"].split("-preview.")
        major, minor = (int(part) for part in base.split("."))
        self.assertEqual(preview["versionCode"], (major * 10 + minor) * 1000 + int(build))


if __name__ == "__main__":
    unittest.main()
