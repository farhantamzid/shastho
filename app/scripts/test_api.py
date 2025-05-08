#!/usr/bin/env python3
"""
Test script to directly test API endpoints for department and doctor retrieval.
This runs outside the Flask app to test the actual API endpoints.
"""
import sys
import requests
import json
from pprint import pprint

def test_departments(hospital_id, base_url):
    """Test the get_departments endpoint."""
    print("\n===== Testing get_departments endpoint =====")
    url = f"{base_url}/patient/get_departments/{hospital_id}"
    print(f"Making request to: {url}")

    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('departments', []))} departments")

            if data.get('departments'):
                print("\nDepartments:")
                for dept in data['departments']:
                    print(f"  - {dept['name']} (ID: {dept['id']})")

                return data['departments'][0]['id']  # Return first department ID for next test
            else:
                print("No departments found")
                return None
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def test_doctors(department_id, base_url):
    """Test the get_doctors endpoint."""
    print("\n===== Testing get_doctors endpoint =====")
    url = f"{base_url}/patient/get_doctors/{department_id}"
    print(f"Making request to: {url}")

    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('doctors', []))} doctors")

            if data.get('doctors'):
                print("\nDoctors:")
                for doctor in data['doctors']:
                    print(f"  - {doctor['name']} ({doctor['specialization']})")
                    print(f"    ID: {doctor['id']}")
            else:
                print("No doctors found")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

def main():
    """Main function to run the tests."""
    # Get base URL from command line or use default
    base_url = "http://localhost:5000" if len(sys.argv) < 2 else sys.argv[1]

    # Get hospital ID from command line or use default
    hospital_id = "2fcc2821-31b6-4742-aad6-b9605232fba6" if len(sys.argv) < 3 else sys.argv[2]

    print(f"Using base URL: {base_url}")
    print(f"Using hospital ID: {hospital_id}")

    # Test departments endpoint
    department_id = test_departments(hospital_id, base_url)

    # If we got a department ID, test doctors endpoint
    if department_id:
        test_doctors(department_id, base_url)
    else:
        print("\nSkipping doctors test since no department ID was returned")

if __name__ == "__main__":
    main()