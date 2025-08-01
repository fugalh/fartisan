# MQTT to Artisan WebSocket Bridge

This tool bridges MQTT messages to Artisan roasting software via WebSocket, allowing Artisan to receive temperature data (ET and BT values) from MQTT topics.

## Features

- Connects to MQTT broker with authentication
- Subscribes to specified topic for temperature data
- Parses JSON payloads to extract ET (Environmental Temperature) and BT (Bean Temperature) values
- Provides WebSocket server for Artisan to connect to
- Responds to Artisan's WebSocket requests with latest temperature values

## Prerequisites

- Python 3.7 or higher
- MQTT broker (configured at host "bombadil")
- Artisan roasting software

## Installation

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The script is pre-configured with the following settings:
- MQTT Host: `bombadil`
- MQTT Port: `1883`
- MQTT Topic: `artisan`
- MQTT User: `artisan`
- MQTT Password: `cafe`
- WebSocket Host: `localhost`
- WebSocket Port: `8765`

To modify these settings, edit the configuration section at the top of `mqtt_artisan_bridge.py`.

## Usage

1. Run the bridge:
   ```bash
   python3 mqtt_artisan_bridge.py
   ```
   
   For debugging output:
   ```bash
   python3 mqtt_artisan_bridge.py --debug
   ```

2. Configure Artisan to connect to the WebSocket:
   - Open Artisan
   - Go to Config » Port
   - Select the WebSocket tab (7th tab)
   - Set the following parameters:
     - Host: `localhost`
     - Port: `8765`
     - Path: `/` (leave empty or set to `/`)
     - Command Node: `command`
     - Message ID Node: `id`
     - Data Request Tag: `getData`
     - Machine ID Node: `machine`
   - For the input channels:
     - Input 1 (BT): Set Node to `data` and Sub-Node to `BT`
     - Input 2 (ET): Set Node to `data` and Sub-Node to `ET`

3. The bridge will:
   - Connect to the MQTT broker at `bombadil`
   - Subscribe to the `artisan` topic
   - Listen for JSON messages containing ET and BT values
   - Serve a WebSocket endpoint at `ws://localhost:8765/`
   - Respond to Artisan's requests with the latest ET and BT values

## Expected MQTT Message Format

The bridge expects JSON messages with ET and BT values:

```json
{
  "ET": 220.5,
  "BT": 189.2
}
```

Other fields in the JSON will be ignored.

## Artisan Configuration

In Artisan's WebSocket configuration:
- The "Data Request" field should be set to `getData` to request all data in one request
- The expected response format is:
  ```json
  {
    "id": 12345,
    "data": {
      "ET": 220.5,
      "BT": 189.2
    }
  }
  ```

## Logging

The application logs information to the console:
- Connection status to MQTT broker
- Received MQTT messages
- WebSocket client connections
- Sent responses to Artisan

## Troubleshooting

1. If the bridge cannot connect to the MQTT broker:
   - Verify the broker is running at `bombadil:1883`
   - Check the username and password are correct
   - Ensure network connectivity to the broker

2. If Artisan cannot connect to the WebSocket:
   - Verify the bridge is running
   - Check that port 8765 is not blocked by a firewall
   - Confirm the WebSocket settings in Artisan match the bridge configuration

3. If temperature values are not updating:
   - Verify MQTT messages are being published to the `artisan` topic
   - Check that the JSON format includes ET and BT fields
   - Ensure the bridge is receiving and parsing the messages (check logs)
