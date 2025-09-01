import unittest
import json
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_calculate(self):
        response = self.app.post('/api/calculate', 
                                   data=json.dumps({"project_name": "Test Project"}),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn('project_id', data)
        self.assertEqual(data['status'], 'processing')

if __name__ == '__main__':
    unittest.main()
