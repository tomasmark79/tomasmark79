import unittest

from update_downloads import update_readme


class DownloadLabelsTest(unittest.TestCase):
    def test_numeric_labels_preserve_surrounding_text(self):
        label = "[10](https://extensions.gnome.org/extension/8500/keyboard-informer/)"
        for line in (
            f"- [**Keyboard Informer**](https://example.com) {label} — description.\n",
            f"- [Keyboard Informer](https://example.com) — description {label}\n",
        ):
            with self.subTest(line=line):
                seen = []

                def fetch(extension_id):
                    seen.append(extension_id)
                    return 5729

                self.assertEqual(
                    update_readme(line, fetch),
                    line.replace("[10]", "[5729]"),
                )
                self.assertEqual(seen, ["8500"])

    def test_missing_labels_fail_instead_of_silently_skipping(self):
        with self.assertRaises(ValueError):
            update_readme("README without download labels", lambda _: 1)

    def test_api_failure_is_reported(self):
        def fail(_):
            raise OSError("GNOME unavailable")

        with self.assertRaises(OSError):
            update_readme(
                "[10](https://extensions.gnome.org/extension/8500/example/)",
                fail,
            )


if __name__ == "__main__":
    unittest.main()
