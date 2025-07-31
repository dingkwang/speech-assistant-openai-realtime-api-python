#!/usr/bin/env python3
"""
Simple script to test the handle_incoming_call endpoint
Run this while your FastAPI server is running on localhost:5050
"""

import requests
import json

BASE_URL = "http://localhost:5050"

def test_get_request():
    """Test GET request to /incoming-call"""
    print("=== Testing GET Request ===")
    response = requests.get(f"{BASE_URL}/incoming-call")
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response Length: {len(response.text)} characters")
    print("Response Preview:")
    print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
    
    # Check for expected TwiML elements
    expected_elements = ["<Response>", "<Say>", "<Connect>", "<Stream", "wss://"]
    missing_elements = [elem for elem in expected_elements if elem not in response.text]
    
    if missing_elements:
        print(f"⚠️  Missing elements: {missing_elements}")
    else:
        print("✅ All expected TwiML elements found")
    
    print()

def test_post_request_form_data():
    """Test POST request with form data (typical Twilio webhook)"""
    print("=== Testing POST Request with Form Data ===")
    
    # Simulate typical Twilio webhook payload
    data = {
        "CallSid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "AccountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "From": "+1234567890",
        "To": "+0987654321",
        "CallStatus": "ringing",
        "ApiVersion": "2010-04-01",
        "Direction": "inbound",
        "ForwardedFrom": "",
        "CallerName": "Test Caller"
    }
    
    response = requests.post(
        f"{BASE_URL}/incoming-call",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print("Response contains TwiML:", "<Response>" in response.text)
    print()

def test_post_request_json():
    """Test POST request with JSON data"""
    print("=== Testing POST Request with JSON ===")
    
    data = {
        "CallSid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "From": "+1234567890",
        "To": "+0987654321"
    }
    
    response = requests.post(
        f"{BASE_URL}/incoming-call",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print("Response contains TwiML:", "<Response>" in response.text)
    print()

def test_error_scenarios():
    """Test various error scenarios"""
    print("=== Testing Error Scenarios ===")
    
    # Test with malformed data
    response = requests.post(
        f"{BASE_URL}/incoming-call",
        data="invalid-data-format"
    )
    print(f"Malformed data - Status: {response.status_code}")
    
    # Test with empty POST
    response = requests.post(f"{BASE_URL}/incoming-call")
    print(f"Empty POST - Status: {response.status_code}")
    
    print()

def test_response_details():
    """Examine the TwiML response in detail"""
    print("=== Detailed Response Analysis ===")
    
    response = requests.get(f"{BASE_URL}/incoming-call")
    
    if response.status_code == 200:
        # Parse and display TwiML structure
        content = response.text
        print("TwiML Structure:")
        print(f"- Contains <Response>: {'<Response>' in content}")
        print(f"- Contains <Say>: {'<Say>' in content}")
        print(f"- Contains <Pause>: {'<Pause' in content}")
        print(f"- Contains <Connect>: {'<Connect>' in content}")
        print(f"- Contains <Stream>: {'<Stream' in content}")
        
        # Extract WebSocket URL
        if 'wss://' in content:
            start = content.find('wss://')
            end = content.find('\'', start)
            if end == -1:
                end = content.find('"', start)
            if end != -1:
                ws_url = content[start:end]
                print(f"- WebSocket URL: {ws_url}")
        
        print("\nFull TwiML Response:")
        print("-" * 50)
        print(content)
        print("-" * 50)
    
    print()

def main():
    """Run all tests"""
    print("Testing handle_incoming_call endpoint")
    print("Make sure your FastAPI server is running on localhost:5050\n")
    
    # Check if server is running
    health_response = requests.get(f"{BASE_URL}/")
    if health_response.status_code != 200:
        print("❌ Server not responding. Start your FastAPI server first:")
        print("python main.py")
        return
    
    print("✅ Server is running\n")
    
    # Run tests
    test_get_request()
    test_post_request_form_data()
    test_post_request_json()
    test_error_scenarios()
    test_response_details()
    
    print("Testing complete!")

if __name__ == "__main__":
    main() 