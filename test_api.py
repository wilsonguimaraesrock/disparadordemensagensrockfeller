#!/usr/bin/env python3
import requests
import json

def test_waha_api():
    base_url = "http://localhost:3000/api"
    headers = {"X-API-KEY": "waha-key-2025"}
    
    print("Testing WAHA API...")
    
    # Test sessions endpoint
    try:
        response = requests.get(f"{base_url}/sessions", headers=headers)
        print(f"Sessions endpoint - Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("---")
    except Exception as e:
        print(f"Error testing sessions: {e}")
    
    # Test default session status
    try:
        response = requests.get(f"{base_url}/sessions/default/status", headers=headers)
        print(f"Default session status - Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("---")
    except Exception as e:
        print(f"Error testing default session status: {e}")
    
    # Test starting a session
    try:
        data = {"name": "default"}
        response = requests.post(f"{base_url}/sessions/start", headers=headers, json=data)
        print(f"Start session - Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("---")
    except Exception as e:
        print(f"Error starting session: {e}")

if __name__ == "__main__":
    test_waha_api()