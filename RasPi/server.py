from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from typing import Literal
from sensor import ultrasonic, rgb, light
import paho.mqtt.client as mqtt
import base64, json, struct, threading, time

PREFIX = "67070164"

DASH_HOST = "mqtt-dashboard.com"
LORA_HOST = "lora.kmitl.ac.th"

TUNNEL_URL = "" # Tunnel URL without https://

APP_ID = "" # Application ID
DEV_EUI = "" # Device EUI

TOPIC_RGB_SET = f"{PREFIX}/rgb/set"
TOPIC_RGB_STATE = f"{PREFIX}/rgb/state"
TOPIC_DISTANCE = f"{PREFIX}/distance"
TOPIC_LIGHT = f"{PREFIX}/light"
TOPIC_TEMP = f"{PREFIX}/temp"
TOPIC_HUMID = f"{PREFIX}/humid"
TOPIC_LORA = f"application/{APP_ID}/device/{DEV_EUI}/event/up"

colors = Literal["red", "yellow", "green", "cyan", "blue", "magenta", "white", "off"]

state = {"distance": None, "temperature": None, "humidity": None, "lora_time": None}
state_lock = threading.Lock()

dash = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{PREFIX}-dash")
lora = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{PREFIX}-lora")

def apply_rgb(color):
    rgb.set_rgb(color)
    dash.publish(TOPIC_RGB_STATE, color, qos=1, retain=True)

def on_dash_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"[ERROR] Dashboard broker connection failed: {reason_code}")
        return
    print("[CONNECTED] Dashboard broker connected")
    client.subscribe(TOPIC_RGB_SET, qos=1)
    client.publish(TOPIC_RGB_STATE, rgb.get_rgb(), qos=1, retain=True)

def on_dash_message(client, userdata, msg):
    color = msg.payload.decode("utf-8").strip().lower()
    if color in rgb.RGB_COLORS:
        apply_rgb(color)
        return
    print(f"[ERROR] Unknown rgb color: {color}")

def on_lora_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"[ERROR] LoRa broker connection failed: {reason_code}")
        return
    print("[CONNECTED] LoRa broker connected")
    client.subscribe(TOPIC_LORA)

def on_lora_message(client, userdata, msg):
    try:
        raw = base64.b64decode(json.loads(msg.payload).get("data", ""))
        temp, humid = struct.unpack(">hH", raw)
    except (ValueError, struct.error):
        print("[ERROR] Invalid LoRa uplink")
        return
    temperature = round(temp / 100, 1)
    humidity = round(humid / 100, 1)
    with state_lock:
        state["temperature"] = temperature
        state["humidity"] = humidity
        state["lora_time"] = time.time()
    dash.publish(TOPIC_TEMP, str(temperature), qos=1, retain=True)
    dash.publish(TOPIC_HUMID, str(humidity), qos=1, retain=True)
    print(f"[RECEIVED] LoRa uplink: {temperature} °C, {humidity} %RH")

def sensor_loop():
    while True:
        distance = ultrasonic.read_distance()
        with state_lock:
            state["distance"] = distance
        if distance is not None:
            dash.publish(TOPIC_DISTANCE, str(distance))
        dash.publish(TOPIC_LIGHT, light.read_light(), retain=True)
        time.sleep(1)

dash.on_connect = on_dash_connect
dash.on_message = on_dash_message
lora.on_connect = on_lora_connect
lora.on_message = on_lora_message

mcp = MCPServer("RaspberryPi-IoT")

def lora_age():
    return int(time.time() - state["lora_time"])

@mcp.tool()
def set_rgb_color(color: colors) -> str:
    apply_rgb(color)
    if color == "off":
        return "RGB is now off"
    return f"RGB is now {color}"

@mcp.tool()
def get_rgb_status() -> str:
    color = rgb.get_rgb()
    if color == "off":
        return "RGB is off"
    return f"RGB color is {color}"

@mcp.tool()
def get_light_status() -> str:
    return f"It is {light.read_light()}"

@mcp.tool()
def get_distance() -> str:
    with state_lock:
        distance = state["distance"]
        if distance is None:
            return "No valid distance reading"
        return f"Distance is {distance} cm"

@mcp.tool()
def get_temperature() -> str:
    with state_lock:
        temperature = state["temperature"]
        if temperature is None:
            return "No temperature received yet"
        return f"Temperature is {temperature} °C (updated {lora_age()} s ago)"

@mcp.tool()
def get_humidity() -> str:
    with state_lock:
        humidity = state["humidity"]
        if humidity is None:
            return "No humidity received yet"
        return f"Humidity is {humidity} %RH (updated {lora_age()} s ago)"

if __name__ == "__main__":
    ultrasonic.setup()
    rgb.setup()
    light.setup()
    dash.connect_async(DASH_HOST, 1883, 60)
    lora.connect_async(LORA_HOST, 1883, 60)
    dash.loop_start()
    lora.loop_start()
    threading.Thread(target=sensor_loop, daemon=True).start()
    try:
        security = TransportSecuritySettings(
            allowed_hosts=[
                TUNNEL_URL,
                f"{TUNNEL_URL}:*",
                "localhost:8000",
                "127.0.0.1:8000"
            ],
            allowed_origins=[f"https://{TUNNEL_URL}"]
        )
        mcp.run(
            transport="streamable-http",
            transport_security=security,
            host="0.0.0.0"
        )
    except KeyboardInterrupt:
        print("\n[QUIT] Stopping program...")
    finally:
        dash.disconnect()
        dash.loop_stop()
        lora.disconnect()
        lora.loop_stop()
        ultrasonic.cleanup()
        rgb.cleanup()
        light.cleanup()
