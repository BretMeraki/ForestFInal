#!/usr/bin/env python
"""
Remote Connection Test Script for Forest App Debug Suite

This script tests the connection to your cloud-deployed Forest app
and verifies that the error logs API is accessible.
"""
import requests
import sys
from pathlib import Path
import os

# Add the parent directory to the Python path
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(SCRIPT_DIR))

# Import configuration
from dashboard_config import CLOUD_ERROR_LOGS_API, API_KEY

def test_connection():
    """Test connection to the cloud-deployed Forest app."""
    print(f"Testing connection to: {CLOUD_ERROR_LOGS_API}")
    
    # Prepare headers if API key is provided
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        # First test the base URL
        base_url = CLOUD_ERROR_LOGS_API.split("/error_logs")[0]
        print(f"Testing base URL: {base_url}")
        
        base_response = requests.get(base_url, headers=headers, timeout=10)
        print(f"Base URL Status: {base_response.status_code}")
        
        # Now test the error logs API
        print(f"Testing error logs API: {CLOUD_ERROR_LOGS_API}")
        
        response = requests.get(
            CLOUD_ERROR_LOGS_API, 
            headers=headers,
            params={"limit": 5},
            timeout=10
        )
        
        print(f"Error Logs API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Retrieved {len(data)} error logs.")
            print("\nAPI Response Sample:")
            if data:
                for i, log in enumerate(data[:2]):  # Show first 2 logs
                    print(f"Log {i+1}:")
                    for key, value in log.items():
                        print(f"  {key}: {value}")
            else:
                print("No error logs found (empty array returned)")
                
            return True
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n✅ Connection test successful! Your debug suite is ready for remote monitoring.")
        print("\nTo start the debug dashboard in remote mode, run:")
        print("  python run_dashboard.py")
    else:
        print("\n❌ Connection test failed!")
        print("\nPossible reasons:")
        print("1. Your cloud deployment is not running")
        print("2. The error_logs endpoint is not exposed or protected")
        print("3. Your API key is incorrect (if authentication is required)")
        print("4. Your cloud URL is incorrect in dashboard_config.py")
