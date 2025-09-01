import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_download_pdf(self):
        response = self.app.get('/api/download/test_project')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'This would be a PDF for project test_project')

if __name__ == '__main__':
    unittest.main()
