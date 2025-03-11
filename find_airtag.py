import asyncio
from uuid import UUID

from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

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

def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
    try:
        # 0x004c Apple Manufacturer Tag
        apple_data = advertisement_data.manufacturer_data[0x004C]
        # (x12,x19) bytes for FindMy
        if apple_data.hex()[0:4] == "1219": 
            ibeacon = ibeacon_format.parse(apple_data)
            uuid = UUID(bytes=bytes(ibeacon.uuid))
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
    scanner = BleakScanner(device_found)
    # Checking that the RSSI of a device we have measured before has changed since we last detected it.
    # If the RSSI has changed at least 1 time, we return the device uuid. We can make this greater if we want to make sure the RSSI is not constant.
    while not(1 in change.values()):
        await scanner.start()
        await asyncio.sleep(2.0)
        await scanner.stop()
    # return uuid of scanned AirTag
    return ret[0]
    


asyncio.run(main())
