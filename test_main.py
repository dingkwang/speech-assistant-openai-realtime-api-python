import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json
from main import app

client = TestClient(app)

class TestHandleIncomingCall:
    """Test suite for the handle_incoming_call endpoint"""
    
    def test_incoming_call_get_request(self):
        """Test GET request to /incoming-call endpoint"""
        response = client.get("/incoming-call")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"
        
        # Check that the response contains expected TwiML elements
        content = response.text
        assert "<Response>" in content
        assert "<Say>" in content
        assert "connect your call to the A. I. voice assistant" in content
        assert "<Connect>" in content
        assert "<Stream " in content
        assert "wss://" in content
        assert "/media-stream" in content

    def test_incoming_call_post_request(self):
        """Test POST request to /incoming-call endpoint"""
        # Simulate typical Twilio webhook data
        twilio_data = {
            "CallSid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "From": "+1234567890",
            "To": "+0987654321",
            "CallStatus": "ringing"
        }
        
        response = client.post("/incoming-call", data=twilio_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/xml"
        
        # Check TwiML structure
        content = response.text
        assert "<Response>" in content
        assert "<Say>" in content
        assert "<Connect>" in content
        assert "<Stream " in content

    def test_incoming_call_post_with_json(self):
        """Test POST request with JSON data"""
        twilio_data = {
            "CallSid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "From": "+1234567890",
            "To": "+0987654321"
        }
        
        response = client.post("/incoming-call", json=twilio_data)
        
        assert response.status_code == 200
        assert "<Response>" in response.text

    def test_twiml_response_structure(self):
        """Test that the TwiML response has correct structure and content"""
        response = client.get("/incoming-call")
        content = response.text
        
        # Check for required TwiML elements in order
        assert content.find("<Response>") < content.find("<Say>")
        assert content.find("</Say>") < content.find("<Pause")
        # The Pause element is self-closing: <Pause length="1" />
        assert content.find("<Pause") < content.find("<Say>", content.find("<Pause"))
        assert content.find("<Connect>") > content.find("</Say>")
        assert content.find("</Connect>") < content.find("</Response>")
        
        # Check WebSocket URL format
        assert "wss://testserver/media-stream" in content

    def test_websocket_url_generation(self):
        """Test that WebSocket URL is generated correctly based on host"""
        # Test with custom host header
        headers = {"host": "example.com"}
        response = client.get("/incoming-call", headers=headers)
        
        assert "wss://example.com/media-stream" in response.text

    @patch('main.logger')
    def test_logging_behavior(self, mock_logger):
        """Test that appropriate logging occurs"""
        response = client.post("/incoming-call", data={"test": "data"})
        
        # Verify logging calls were made
        assert mock_logger.info.called
        assert response.status_code == 200

    def test_error_handling(self):
        """Test error handling in the endpoint"""
        # Test with malformed request that might cause issues
        response = client.post("/incoming-call", data="invalid-data")
        
        # Should still return a valid TwiML response even with bad data
        assert response.status_code == 200
        assert "<Response>" in response.text

    def test_response_content_type(self):
        """Test that response has correct content type for TwiML"""
        response = client.get("/incoming-call")
        
        assert response.headers["content-type"] == "application/xml"
        assert response.status_code == 200

    def test_multiple_requests(self):
        """Test that multiple requests work consistently"""
        for i in range(3):
            response = client.get("/incoming-call")
            assert response.status_code == 200
            assert "<Response>" in response.text
            assert "<Connect>" in response.text

    def test_twiml_xml_structure(self):
        """Test the XML structure of the TwiML response"""
        response = client.get("/incoming-call")
        content = response.text
        
        # Should start with XML declaration
        assert content.startswith('<?xml version="1.0"')
        
        # Should have proper XML structure
        assert content.count("<Response>") == 1
        assert content.count("</Response>") == 1
        assert content.count("<Say>") >= 2  # At least two Say elements
        assert content.count("<Connect>") == 1
        assert content.count("<Stream") == 1

class TestManualTesting:
    """Manual testing examples and utilities"""
    
    @staticmethod
    def print_sample_curl_commands():
        """Print sample curl commands for manual testing"""
        print("\n=== Manual Testing Commands ===")
        print("\n1. Test GET request:")
        print("curl -X GET http://localhost:5050/incoming-call")
        
        print("\n2. Test POST request with form data:")
        print('curl -X POST http://localhost:5050/incoming-call \\')
        print('  -H "Content-Type: application/x-www-form-urlencoded" \\')
        print('  -d "CallSid=CAxxxxxxxx&From=%2B1234567890&To=%2B0987654321"')
        
        print("\n3. Test POST request with JSON:")
        print('curl -X POST http://localhost:5050/incoming-call \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"CallSid":"CAxxxxxxxx","From":"+1234567890"}\'')
        
        print("\n4. Test with verbose output:")
        print("curl -v http://localhost:5050/incoming-call")

if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    # Test GET request
    response = client.get("/incoming-call")
    print(f"GET /incoming-call: {response.status_code}")
    print(f"Response content type: {response.headers.get('content-type')}")
    print(f"Response contains TwiML: {'<Response>' in response.text}")
    
    # Test POST request
    response = client.post("/incoming-call", data={"test": "data"})
    print(f"POST /incoming-call: {response.status_code}")
    
    # Print manual testing commands
    TestManualTesting.print_sample_curl_commands()
    
    print("\nTo run full test suite:")
    print("pip install pytest pytest-asyncio")
    print("pytest test_main.py -v") 