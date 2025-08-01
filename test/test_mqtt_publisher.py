#!/usr/bin/python3
"""
Test script to publish MQTT messages for the MQTT to Artisan WebSocket Bridge
"""

import json
import time
import paho.mqtt.client as mqtt
import argparse

# MQTT Configuration
MQTT_HOST = "bombadil"
MQTT_PORT = 1883
MQTT_TOPIC = "artisan"
MQTT_USER = "artisan"
MQTT_PASSWORD = "cafe"

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print("Connected to MQTT broker successfully")
    else:
        print(f"Failed to connect to MQTT broker with code: {rc}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test MQTT publisher for Artisan bridge')
    parser.add_argument('--debug', action='store_true', help='Print debug information about MQTT messages being sent')
    args = parser.parse_args()
    
    # Setup MQTT client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    
    try:
        # Connect to broker
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        
        # Start the network loop in a separate thread
        client.loop_start()
        
        # Wait a moment for connection
        time.sleep(1)
        
        # Publish test messages
        print("Publishing test messages...")
        
        # Test message 1
        data1 = {
            "ET": 300,
            "BT": 240,
            "timestamp": time.time()
        }
        if args.debug:
            print(f"Sending MQTT message: {data1}")
        client.publish(MQTT_TOPIC, json.dumps(data1))
        print(f"Published: {data1}")
        
        time.sleep(4)
        
        # Test message 2 - order swapped
        data2 = {
            "BT": 241,
            "ET": 301,
            "timestamp": time.time()
        }
        if args.debug:
            print(f"Sending MQTT message: {data2}")
        client.publish(MQTT_TOPIC, json.dumps(data2))
        print(f"Published: {data2}")
        
        time.sleep(4)
        
        # Test message 3 - only BT
        data3 = {
            "BT": 201.3,
            "timestamp": time.time()
        }
        if args.debug:
            print(f"Sending MQTT message: {data3}")
        client.publish(MQTT_TOPIC, json.dumps(data3))
        print(f"Published: {data3}")
        
        time.sleep(1)
        
        # Stop the network loop
        client.loop_stop()
        client.disconnect()
        
        print("Test messages published successfully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
