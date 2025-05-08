import unittest
from unittest.mock import patch
from app import create_app
from app.utils.db import db
from app.models.database import UserRole
import json

class TestPatientRoutes(unittest.TestCase):
    """Tests for patient routes."""

    def setUp(self):
        """Set up test app and client."""
        # Create patches for the authentication decorators
        self.login_patcher = patch('app.utils.auth.login_required')
        self.role_patcher = patch('app.utils.auth.role_required')

        # Start the patches
        self.mock_login = self.login_patcher.start()
        self.mock_role = self.role_patcher.start()

        # Configure the mocks to do nothing (pass through)
        self.mock_login.return_value = lambda f: f
        self.mock_role.return_value = lambda f: f

        # Create the test app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        print("Test setup complete")

    def tearDown(self):
        """Clean up after test."""
        # Stop the patches
        self.login_patcher.stop()
        self.role_patcher.stop()

        self.app_context.pop()
        print("Test teardown complete")

    def test_get_departments(self):
        """Test retrieving departments for a hospital."""
        print("\nRunning test_get_departments")

        # Get a hospital ID from Supabase for testing
        hospitals = db.get_all(db.Hospital)
        if not hospitals:
            self.skipTest("No hospitals found for testing")

        hospital_id = str(hospitals[0].id)
        print(f"Using hospital_id: {hospital_id}")

        # Make request to get departments
        with self.app.test_request_context():
            response = self.client.get(f'/patient/get_departments/{hospital_id}')

            # Check response
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('departments', data)
            print(f"Found {len(data['departments'])} departments for hospital {hospital_id}")

            # Return a department ID for the next test
            if data['departments']:
                return data['departments'][0]['id']
            return None

    def test_get_doctors(self):
        """Test retrieving doctors for a department."""
        print("\nRunning test_get_doctors")

        # For testing independently, let's directly query the departments
        department_id = None
        departments = db.get_all(db.Department)
        if departments:
            department_id = str(departments[0].id)
            print(f"Using department_id: {department_id}")
        else:
            self.skipTest("No departments found for testing")

        # Make request to get doctors
        with self.app.test_request_context():
            response = self.client.get(f'/patient/get_doctors/{department_id}')

            # Check response
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('doctors', data)
            print(f"Found {len(data['doctors'])} doctors for department {department_id}")

            # Verify doctor data structure
            if data['doctors']:
                doctor = data['doctors'][0]
                self.assertIn('id', doctor)
                self.assertIn('name', doctor)
                self.assertIn('specialization', doctor)
                print(f"Sample doctor: {doctor['name']} ({doctor['specialization']})")

if __name__ == '__main__':
    unittest.main()