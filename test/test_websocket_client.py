#!/usr/bin/python3
"""
Test script to connect to the MQTT to Artisan WebSocket Bridge and send requests
"""

import asyncio
import json
import websockets
import argparse

# WebSocket Configuration
WEBSOCKET_URI = "ws://localhost:8765/"

async def test_websocket_client(debug=False):
    """Test WebSocket client to verify the bridge"""
    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print(f"Connected to WebSocket server at {WEBSOCKET_URI}")
            
            # Send a test request
            request = {
                "id": 12345,
                "command": "getData",
                "machine": 0
            }
            
            if debug:
                print(f"Sending WebSocket request: {request}")
            else:
                print(f"Sending request: {request}")
                
            await websocket.send(json.dumps(request))
            
            # Receive response
            response = await websocket.recv()
            if debug:
                print(f"Received WebSocket response: {response}")
            else:
                print(f"Received response: {response}")
            
            # Parse and display the response
            try:
                data = json.loads(response)
                print(f"Parsed response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response is not valid JSON: {response}")
                
    except Exception as e:
        print(f"Error connecting to WebSocket server: {e}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test WebSocket client for Artisan bridge')
    parser.add_argument('--debug', action='store_true', help='Print debug information about WebSocket messages being sent/received')
    args = parser.parse_args()
    
    print("Testing WebSocket connection to MQTT to Artisan Bridge...")
    asyncio.run(test_websocket_client(args.debug))
