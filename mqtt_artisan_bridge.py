#!/usr/bin/python3
"""
MQTT to Artisan WebSocket Bridge
Connects to MQTT broker, subscribes to artisan topic, and forwards ET/BT values to Artisan via WebSocket.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import websockets
import paho.mqtt.client as mqtt
from threading import Thread
from queue import Queue, Empty
import time
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MQTT Configuration
MQTT_HOST = "bombadil"
MQTT_PORT = 1883
MQTT_TOPIC = "artisan"
MQTT_USER = "artisan"
MQTT_PASSWORD = "cafe"

# WebSocket Configuration
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8765

class MQTTArtisanBridge:
    def __init__(self):
        # Store latest ET/BT values
        self.latest_values = {"ET": None, "BT": None}
        self.message_queue = Queue()
        
        # WebSocket clients
        self.clients = set()
        
        # Setup MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        
        # Start MQTT in a separate thread
        self.mqtt_thread = Thread(target=self.run_mqtt, daemon=True)
        self.mqtt_thread.start()
        
    def run_mqtt(self):
        """Run MQTT client in a separate thread"""
        try:
            logger.info(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
            self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
            self.mqtt_client.loop_forever()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
            
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            client.subscribe(MQTT_TOPIC)
            logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
            
    def on_mqtt_message(self, client, userdata, msg):
        """Callback when MQTT message is received"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.debug(f"Received MQTT message: {payload}")
            
            # Parse JSON payload
            data = json.loads(payload)
            
            # Extract ET and BT values if present
            if "ET" in data:
                self.latest_values["ET"] = data["ET"]
                logger.debug(f"Updated ET value: {data['ET']}")
                
            if "BT" in data:
                self.latest_values["BT"] = data["BT"]
                logger.debug(f"Updated BT value: {data['BT']}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON payload: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
            
    def on_mqtt_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.info("Disconnected from MQTT broker")
        
    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        logger.info(f"New client connected. Total clients: {len(self.clients)}")
        
    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def handle_websocket_request(self, websocket, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WebSocket request from Artisan"""
        try:
            # Extract message ID and command
            message_id = request_data.get("id") or request_data.get("message_id") or int(time.time() * 1000) % 100000
            
            # Prepare response with latest ET/BT values
            response = {
                "id": message_id,
                "data": {}
            }
            
            # Add available values to response
            for key in ["ET", "BT"]:
                if self.latest_values[key] is not None:
                    response["data"][key] = self.latest_values[key]
                    
            logger.debug(f"Sending response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error handling WebSocket request: {e}")
            return {"error": str(e)}
            
    async def handle_client(self, websocket):
        """Handle individual WebSocket client connection"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    # Parse incoming request
                    request_data = json.loads(message)
                    logger.debug(f"Received WebSocket request: {request_data}")
                    
                    # Handle the request and send response
                    response = await self.handle_websocket_request(websocket, request_data)
                    await websocket.send(json.dumps(response))
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    await websocket.send(json.dumps({"error": str(e)}))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.unregister_client(websocket)
            
    async def start_websocket_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        server = await websockets.serve(self.handle_client, WEBSOCKET_HOST, WEBSOCKET_PORT)
        logger.info("WebSocket server started")
        return server

async def main(debug=False):
    """Main function to start the bridge"""
    # Set logging level based on debug flag
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    bridge = MQTTArtisanBridge()
    
    # Start WebSocket server
    server = await bridge.start_websocket_server()
    
    logger.info("MQTT to Artisan WebSocket Bridge is running...")
    logger.info(f"WebSocket endpoint: ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}/")
    logger.info("Waiting for connections...")
    
    # Keep the server running
    await server.wait_closed()

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MQTT to Artisan WebSocket Bridge')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    asyncio.run(main(args.debug))
