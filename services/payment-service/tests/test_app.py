import unittest
import json
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_checkout(self):
        response = self.app.post('/api/checkout', 
                                   data=json.dumps({"project_id": "test_project"}),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn('checkout_url', data)

    def test_stripe_webhook(self):
        response = self.app.post('/webhooks/stripe', 
                                   data=json.dumps({"event": "test_event"}),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

if __name__ == '__main__':
    unittest.main()
