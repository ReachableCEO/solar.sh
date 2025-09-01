import unittest
import json
from unittest import mock
import os
import base64
import sys # Import sys

# Create global mocks for laspy and pvlib before app is imported
# This ensures app.py sees these mocked versions
mock_laspy = mock.Mock()
mock_pvlib = mock.Mock()
mock_pvlib.data = mock.Mock()
mock_pvlib.solar = mock.Mock()
mock_pvlib.irradiance = mock.Mock()
mock_pvlib.temperature = mock.Mock()
mock_pvlib.pvsystem = mock.Mock()
mock_pvlib.inverter = mock.Mock()

# Mock specific error classes if they are directly used
mock_laspy.errors = mock.Mock()
mock_laspy.errors.LaspyError = Exception # Use generic Exception for now if specific is problematic

sys.modules['laspy'] = mock_laspy
sys.modules['pvlib'] = mock_pvlib

# Mock environment variables before importing app
with mock.patch.dict(os.environ, {
    'DATABASE_URL': 'postgresql://user:password@host:5432/testdb',
}):
    from app import app, get_db_connection

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        app.testing = True
        # Reset mocks for each test
        mock_laspy.reset_mock()
        mock_pvlib.reset_mock()
        mock_pvlib.data.reset_mock()
        mock_pvlib.solar.reset_mock()
        mock_pvlib.irradiance.reset_mock()
        mock_pvlib.temperature.reset_mock()
        mock_pvlib.pvsystem.reset_mock()
        mock_pvlib.inverter.reset_mock()
        mock_laspy.errors.reset_mock()


    @mock.patch('app.get_db_connection')
    def test_calculate_success(self, mock_get_db_connection):
        # Set up mocks for laspy and pvlib functions
        mock_las_header = mock.Mock()
        mock_las_header.mins = [0, 0, 0]
        mock_las_header.maxs = [10, 10, 10]
        mock_laspy.read.return_value = mock.Mock(header=mock_las_header)

        mock_pvlib.data.get_tmy.return_value = mock.Mock(index=[0], ghi=[100], dni=[100], dhi=[0], temp_air=[25], wind_speed=[5])
        mock_pvlib.solar.get_solarposition.return_value = mock.Mock(apparent_zenith=[30], azimuth=[180])
        mock_pvlib.irradiance.get_total_irradiance.return_value = mock.Mock(poa_global=[500], poa_direct=[400], poa_diffuse=[100])
        mock_pvlib.temperature.sapm.return_value = mock.Mock(cell_temperature=[40])
        mock_pvlib.pvsystem.sapm.return_value = mock.Mock(p_mp=[300])
        mock_pvlib.inverter.sandia.return_value = mock.Mock(ac=[250])

        # Mock DB connection and cursor
        mock_conn = mock.Mock()
        mock_cur = mock.Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = ('test_project_id',)
        mock_get_db_connection.return_value = mock_conn

        test_data = {
            "project_name": "Test Project",
            "location": {"lat": 35.0, "lon": -78.0},
            "lidar_data": base64.b64encode(b"dummy_las_data").decode('utf-8'),
            "panel_specs": {"type": "mono"},
            "ground_mount_config": {"tilt": 30}
        }

        response = self.app.post('/api/calculate',
                                   data=json.dumps(test_data),
                                   content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIn('project_id', data)
        self.assertEqual(data['status'], 'completed')
        self.assertIn('annual_kwh', data)

        mock_laspy.read.assert_called_once()
        mock_get_db_connection.assert_called_once()
        mock_cur.execute.assert_any_call(
            mock.ANY, # INSERT INTO projects
            ('Test Project', 35.0, -78.0, mock.ANY)
        )
        mock_cur.execute.assert_any_call(
            mock.ANY, # INSERT INTO calculations
            ('test_project_id', mock.ANY, mock.ANY, mock.ANY)
        )
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_calculate_missing_fields(self):
        test_data = {
            "project_name": "Test Project",
            "location": {"lat": 35.0, "lon": -78.0},
            # Missing lidar_data_b64
            "panel_specs": {"type": "mono"}
        }
        response = self.app.post('/api/calculate',
                                   data=json.dumps(test_data),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Missing required fields')

    @mock.patch('app.get_db_connection')
    def test_calculate_lidar_error(self, mock_get_db_connection):
        mock_laspy.read.side_effect = mock_laspy.errors.LaspyError("Bad LAS file") # Use the mocked error class

        test_data = {
            "project_name": "Test Project",
            "location": {"lat": 35.0, "lon": -78.0},
            "lidar_data": base64.b64encode(b"corrupt_data").decode('utf-8'),
            "panel_specs": {"type": "mono"}
        }
        response = self.app.post('/api/calculate',
                                   data=json.dumps(test_data),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('LIDAR data processing failed', data['error'])

    @mock.patch('app.get_db_connection')
    def test_calculate_db_error(self, mock_get_db_connection):
        # Set up mocks for laspy and pvlib functions
        mock_las_header = mock.Mock()
        mock_las_header.mins = [0, 0, 0]
        mock_las_header.maxs = [10, 10, 10]
        mock_laspy.read.return_value = mock.Mock(header=mock_las_header)
        mock_pvlib.data.get_tmy.return_value = mock.Mock(index=[0], ghi=[100], dni=[100], dhi=[0], temp_air=[25], wind_speed=[5])

        mock_get_db_connection.side_effect = psycopg2.Error("DB connection failed")

        test_data = {
            "project_name": "Test Project",
            "location": {"lat": 35.0, "lon": -78.0},
            "lidar_data": base64.b64encode(b"dummy_las_data").decode('utf-8'),
            "panel_specs": {"type": "mono"},
            "ground_mount_config": {"tilt": 30}
        }
        response = self.app.post('/api/calculate',
                                   data=json.dumps(test_data),
                                   content_type='application/json')
        data = json.loads(response.get_data())
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)
        self.assertIn('Database operation failed', data['error'])

    @mock.patch('app.get_db_connection')
    def test_health_check_db_success(self, mock_get_db_connection):
        mock_conn = mock.Mock()
        mock_get_db_connection.return_value = mock_conn

        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'OK')
        mock_get_db_connection.assert_called_once()
        mock_conn.close.assert_called_once()

    @mock.patch('app.get_db_connection')
    def test_health_check_db_failure(self, mock_get_db_connection):
        mock_get_db_connection.side_effect = Exception("DB connection error")

        response = self.app.get('/health')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_data(as_text=True), 'Database connection failed')
        mock_get_db_connection.assert_called_once()

if __name__ == '__main__':
    unittest.main()
