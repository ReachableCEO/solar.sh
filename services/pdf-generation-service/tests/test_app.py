import unittest
import json
from unittest.mock import patch, MagicMock
from app import app, limiter
from datetime import datetime

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Disable rate limiting for tests
        limiter.enabled = False

    def tearDown(self):
        # Re-enable rate limiting after tests if necessary (though not strictly needed for test client)
        limiter.enabled = True

    def test_health_check_success(self):
        """Test health check endpoint when database is available"""
        with patch('app.get_db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            response = self.app.get('/health')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'healthy')
            self.assertEqual(data['service'], 'pdf-generation-service')

    def test_health_check_failure(self):
        """Test health check endpoint when database is unavailable"""
        with patch('app.get_db_connection', side_effect=Exception('DB Error')):
            response = self.app.get('/health')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'unhealthy')

    def test_download_pdf_invalid_uuid(self):
        """Test PDF download with invalid project ID format"""
        response = self.app.get('/api/download/invalid-id')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Invalid project ID format', data['error'])

    def test_download_pdf_project_not_found(self):
        """Test PDF download when project doesn't exist"""
        with patch('app.get_db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            response = self.app.get('/api/download/12345678-1234-5678-9012-123456789012')
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('Project not found', data['error'])

    def test_download_pdf_unpaid_project(self):
        """Test PDF download for unpaid project"""
        with patch('app.get_db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            # Mock project exists but status is 'pending'
            mock_cursor.fetchone.side_effect = [('Test Project', 35.79, -78.78, 10000.0, 'pending', '{}', None), None]
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            response = self.app.get('/api/download/12345678-1234-5678-9012-123456789012')
            self.assertEqual(response.status_code, 403)
            data = json.loads(response.data)
            self.assertIn('must be paid', data['error'])

    def test_download_pdf_no_calculation(self):
        """Test PDF download when calculation results don't exist"""
        with patch('app.get_db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            # Mock project exists and is paid, but no calculation
            mock_cursor.fetchone.side_effect = [
                ('Test Project', 35.79, -78.78, 10000.0, 'paid', '{}', None),
                None  # No calculation data
            ]
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            response = self.app.get('/api/download/12345678-1234-5678-9012-123456789012')
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('Calculation results not found', data['error'])

    def test_check_pdf_available_success(self):
        """Test HEAD request for PDF availability when everything is ready"""
        with patch('app.get_db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            # Mock project data: (status,) and calculation data: (1,)
            mock_cursor.fetchone.side_effect = [('paid',), (1,)]
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            response = self.app.head('/api/download/12345678-1234-5678-9012-123456789012')
            self.assertEqual(response.status_code, 200)

    def test_check_pdf_available_unpaid(self):
        """Test HEAD request for PDF availability when project is unpaid"""
        with patch('app.get_db_connection') as mock_conn:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            # Mock only project data: (status,) - no calculation check needed for unpaid
            mock_cursor.fetchone.return_value = ('pending',)
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            response = self.app.head('/api/download/12345678-1234-5678-9012-123456789012')
            self.assertEqual(response.status_code, 403)

    @patch('app.cache.set')
    @patch('app.HTML')
    @patch('app.get_db_connection')
    def test_download_pdf_success(self, mock_get_db_connection, mock_html, mock_cache_set):
        """Test successful PDF download"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Mock project and calculation data
        mock_cursor.fetchone.side_effect = [
            # Project data: project_name, lat, lon, cost, status, metadata, created_at
            ('Test Project', 35.79, -78.78, 10000.0, 'paid', '{}', datetime(2023, 1, 1, 10, 0, 0)),
            # Calculation data: annual_kwh, shading_loss_pct, financial_data, created_at
            (10000.0, 0.05, '{}', datetime(2023, 1, 1, 11, 0, 0))
        ]

        # Mock WeasyPrint HTML().write_pdf
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance
        mock_html_instance.write_pdf.return_value = b"dummy pdf content"

        response = self.app.get('/api/download/12345678-1234-5678-9012-123456789012')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertEqual(response.data, b"dummy pdf content")
        mock_cache_set.assert_called_once() # Ensure caching is called

    @patch('app.cache.delete')
    @patch('app.get_db_connection')
    def test_delete_project_data_success(self, mock_get_db_connection, mock_cache_delete):
        """Test successful GDPR data deletion"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ('some_id',) # Project exists

        response = self.app.delete('/api/data/privacy/12345678-1234-5678-9012-123456789012')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Project data deleted successfully', data['message'])
        mock_cursor.execute.assert_any_call("DELETE FROM calculations WHERE project_id = %s", ('12345678-1234-5678-9012-123456789012',))
        mock_cursor.execute.assert_any_call("DELETE FROM projects WHERE id = %s", ('12345678-1234-5678-9012-123456789012',))
        mock_connection.commit.assert_called_once()
        mock_cache_delete.assert_called_once_with('pdf_12345678-1234-5678-9012-123456789012')

    @patch('app.get_db_connection')
    def test_delete_project_data_not_found(self, mock_get_db_connection):
        """Test GDPR data deletion for non-existent project"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None # Project does not exist

        response = self.app.delete('/api/data/privacy/12345678-1234-5678-9012-123456789012')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Project not found', data['error'])

    @patch('app.get_db_connection')
    def test_export_project_data_success(self, mock_get_db_connection):
        """Test successful GDPR data export"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Mock project and calculation data for export
        mock_cursor.fetchone.return_value = (
            '12345678-1234-5678-9012-123456789012', # id
            datetime(2023, 1, 1, 10, 0, 0), # created_at
            'paid', # status
            10000.0, # cost_usd
            'Test Project', # project_name
            35.79, # location_lat
            -78.78, # location_lon
            json.dumps({'key': 'value'}), # metadata (JSONB)
            10000.0, # annual_kwh
            0.05, # shading_loss_pct
            json.dumps({'financial_key': 'financial_value'}), # financial_data (JSONB)
            datetime(2023, 1, 1, 11, 0, 0) # calc_created_at
        )

        response = self.app.get('/api/data/export/12345678-1234-5678-9012-123456789012')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['project_id'], '12345678-1234-5678-9012-123456789012')
        self.assertIn('calculation_data', data)
        self.assertIn('export_timestamp', data)

    @patch('app.get_db_connection')
    def test_export_project_data_not_found(self, mock_get_db_connection):
        """Test GDPR data export for non-existent project"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None # Project does not exist

        response = self.app.get('/api/data/export/12345678-1234-5678-9012-123456789012')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('Project not found', data['error'])

    @patch('app.cache.delete')
    def test_clear_pdf_cache_success(self, mock_cache_delete):
        """Test successful clearing of specific PDF cache"""
        response = self.app.post('/api/cache/clear/12345678-1234-5678-9012-123456789012')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Cache cleared', data['message'])
        mock_cache_delete.assert_called_once_with('pdf_12345678-1234-5678-9012-123456789012')

    @patch('app.cache.clear')
    def test_clear_all_cache_success(self, mock_cache_clear):
        """Test successful clearing of all PDF caches"""
        response = self.app.post('/api/cache/clear-all')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('All PDF caches cleared', data['message'])
        mock_cache_clear.assert_called_once()

if __name__ == '__main__':
    unittest.main()
