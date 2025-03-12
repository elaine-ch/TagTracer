import RPi.GPIO as GPIO
import asyncio
import time
import math
import threading
from uuid import UUID

from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

LED_PIN = 37
BUZZER_PIN = 32
BLU_PIN = 8
GRN_PIN = 10
RED_PIN = 12
BUTTON = 40
DUAL_RED = 19
DUAL_GRN = 21
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(BLU_PIN, GPIO.OUT)
GPIO.setup(GRN_PIN, GPIO.OUT)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(DUAL_RED, GPIO.OUT)
GPIO.setup(DUAL_GRN, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)

segments = {
    'a': 11,
    'b': 13,
    'c': 15,
    'd': 29,
    'e': 31,
    'f': 33,
    'g': 35
}

numbers = {
    0: ['a', 'b', 'c', 'd', 'e', 'f'],
    1: ['b', 'c'],
    2: ['a', 'b', 'g', 'e', 'd'],
    3: ['a', 'b', 'g', 'c', 'd'],
    4: ['f', 'g', 'b', 'c'],
    5: ['a', 'f', 'g', 'c', 'd'],
    6: ['a', 'f', 'g', 'c', 'd', 'e'],
    7: ['a', 'b', 'c'],
    8: ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    9: ['a', 'b', 'c', 'd', 'f', 'g']
}

# Format of advertisment data
ibeacon_format = Struct(
    "type_length" / Const(b"\x12\x19"),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "power" / Int8sl,
)

devices = {}
change = {}
ret = {}
first_detected = {}
distinct_ids = []

def flash_led(duration):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LED_PIN, GPIO.LOW)
    
def button():
    global silence_mode
    while True:
        if stop:
            break
        if(GPIO.input(BUTTON)):
            silence_mode = not silence_mode
            print("button pressed")
        if silence_mode:
            GPIO.output(DUAL_GRN, GPIO.LOW)
            GPIO.output(DUAL_RED, GPIO.HIGH)
        else:
            GPIO.output(DUAL_GRN, GPIO.HIGH)
            GPIO.output(DUAL_RED, GPIO.LOW)

def display_num(num):
    for segment in segments.values():
        GPIO.output(segment, GPIO.LOW)

    for segment in numbers[num]:
        GPIO.output(segments[segment], GPIO.HIGH)

def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
    #time out detected devices after 15 min
    for device in first_detected:
        if time.time() - first_detected[device] > 900:
            del first_detected[device]
                
        #time out ndistinct ids after 5 min
    if time.time() - distinct_ids[0] > 300:
        distinct_ids.clear()
        distinct_ids.insert(0, time.time())
    
    try:
        # 0x004c Apple Manufacturer Tag
        apple_data = advertisement_data.manufacturer_data[0x004C]
        # (x12,x19) bytes for FindMy
        if apple_data.hex()[0:4] == "1219": 
            ibeacon = ibeacon_format.parse(apple_data)
            uuid = UUID(bytes=bytes(ibeacon.uuid))
            
            # Track first detection time
            if str(uuid) not in first_detected:
                first_detected[str(uuid)] = time.time()
            
            if uuid not in distinct_ids:
                distinct_ids.append(uuid)
            
            # devices is a dict that stores uuid, rssi key,value pairings
            if str(uuid) in devices:
                if abs(devices[str(uuid)] - advertisement_data.rssi) > 2:
                    # change is a dict that stores uuid, times changed from last scan key,value pairings
                    if str(uuid) in change:
                        change[str(uuid)] += 1
                    else:
                        change[str(uuid)] = 1
                    # When we reach our change threshold, 1 in this case, we set our return value to that devices uuid 
                    if change[str(uuid)] == 1:
                        ret[0] = uuid
                # else:
                #     if str(uuid) in change:
                #         change[str(uuid)] = max(change[str(uuid)] - 1, 0)
                #     else:
                #         change[str(uuid)] = 0
            devices[str(uuid)] = advertisement_data.rssi            
    except KeyError:
        pass
    except ConstError:
        pass

async def main():
    global stop
    global silence_mode
    GPIO.output(LED_PIN, GPIO.LOW)
    # GPIO.output(DUAL_GRN, GPIO.HIGH)
    # GPIO.output(DUAL_RED, GPIO.LOW)
    buzzer_pwm = GPIO.PWM(BUZZER_PIN, 500)
    distinct_ids.insert(0, time.time())
    silence_mode = False
    scanner = BleakScanner(device_found)
    # Checking that the RSSI of a device we have measured before has changed since we last detected it.
    # If the RSSI has changed at least 1 time, we return the device uuid. We can make this greater if we want to make sure the RSSI is not constant.
    
    while True:
        stop = False
        button_thread = threading.Thread(target=button, args=())
        button_thread.start()
            
        while not(1 in change.values()):
            await scanner.start()
            await asyncio.sleep(2.0)
            await scanner.stop()
        
        # return uuid of scanned AirTag
        print(f"time: {time.time()}\n")
        print(f"uuid: {ret[0]}\n")
        print(f"rssi: {devices[str(ret[0])]}\n")
        flash = threading.Thread(target=flash_led, args=(5,))
        flash.start()
        
        if (time.time() - first_detected[str(ret[0])] >= 120) and not silence_mode:
            del first_detected[str(ret[0])]
            buzzer_pwm.start(50)
            await asyncio.sleep(3)
            buzzer_pwm.stop()
            
        #find number of airtags nearby
        #1-2: green (first index of list is always the last time list was cleared)
        print(distinct_ids)
        if len(distinct_ids) < 4:
            GPIO.output(RED_PIN, GPIO.LOW)
            GPIO.output(BLU_PIN, GPIO.LOW)
            GPIO.output(GRN_PIN, GPIO.HIGH)
        elif len(distinct_ids) < 6:
            GPIO.output(RED_PIN, GPIO.LOW)
            GPIO.output(BLU_PIN, GPIO.HIGH)
            GPIO.output(GRN_PIN, GPIO.LOW)
        else:
            GPIO.output(RED_PIN, GPIO.HIGH)
            GPIO.output(BLU_PIN, GPIO.LOW)
            GPIO.output(GRN_PIN, GPIO.LOW)
            
        #calculate distance
        meters = 10 ** ((-69 - devices[str(ret[0])]) / (10 * 2))
        display_num(math.ceil(meters))

        change.clear()
        flash.join()
        stop = True
        button_thread.join()
        # return ret[0]
    


asyncio.run(main())
