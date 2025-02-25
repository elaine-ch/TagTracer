import simplepyble
import time
from datetime import datetime

APPLE_MANU_ID = '0x4c'
APPLE_FINDMY = bytes([0x12, 0x19])

adapter = simplepyble.Adapter.get_adapters()[0]
while True:
    adapter.scan_for(2000)
    for peripheral in adapter.scan_get_results():
        manufacturer_data = peripheral.manufacturer_data()
        for manufacturer_id, value in manufacturer_data.items():
            if manufacturer_id == int(APPLE_MANU_ID, 16) and value.startswith(APPLE_FINDMY):
                print(f"{datetime.now().strftime('%H:%M')} - Found AirTag")
                print(f"Man Data: {value.hex()}\n")
                print(f"RSSI: {peripheral.rssi()}\n")

# 1219005c9704d9ad6b716f73cca1e4a802fd75eb520c194c2f0100
# 121900001d798599068e3eafba462bb979603990316bae22a00000
# 121900c43be09e9148ee480880b96276d43b036a36d8bb13b10200