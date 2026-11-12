import unittest
from bot_utils import validate_public_url, safe_zip_name

class URLValidationTests(unittest.TestCase):
    def test_accepts_public_https_url(self):
        self.assertEqual(validate_public_url("https://example.com/video"), "https://example.com/video")

    def test_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            validate_public_url("file:///etc/passwd")

    def test_rejects_localhost(self):
        with self.assertRaises(ValueError):
            validate_public_url("http://localhost/private")

    def test_rejects_private_ip(self):
        with self.assertRaises(ValueError):
            validate_public_url("http://127.0.0.1/private")

class ArchiveNameTests(unittest.TestCase):
    def test_sanitizes_archive_name(self):
        self.assertEqual(safe_zip_name("../../my gallery"), "my_gallery")

if __name__ == "__main__":
    unittest.main()
