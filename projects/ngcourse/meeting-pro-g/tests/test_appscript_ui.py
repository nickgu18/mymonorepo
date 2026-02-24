import os
from bs4 import BeautifulSoup
import unittest

class TestAppScriptUI(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.join(os.path.dirname(__file__), '../appscript/index.html')
        with open(self.index_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
            self.soup = BeautifulSoup(self.html_content, 'html.parser')

    def test_cloud_run_url_input_exists(self):
        """Verify Cloud Run URL input exists."""
        input_el = self.soup.find('input', {'id': 'cloudRunUrl'})
        self.assertIsNotNone(input_el, "Cloud Run URL input missing")

    def test_manual_trigger_button_exists(self):
        """Verify 'Check Emails Now' button exists."""
        # Find button with specific text or onclick handler
        buttons = self.soup.find_all('button')
        check_button = None
        for btn in buttons:
            if 'Check Emails Now' in btn.get_text() or 'manualTrigger()' in btn.get('onclick', ''):
                check_button = btn
                break
        self.assertIsNotNone(check_button, "'Check Emails Now' button missing")

    def test_save_config_button_exists(self):
        """Verify 'Save Settings' button exists."""
        buttons = self.soup.find_all('button')
        save_button = None
        for btn in buttons:
            if 'Save Settings' in btn.get_text() or 'saveConfig()' in btn.get('onclick', ''):
                save_button = btn
                break
        self.assertIsNotNone(save_button, "'Save Settings' button missing")

if __name__ == '__main__':
    unittest.main()
