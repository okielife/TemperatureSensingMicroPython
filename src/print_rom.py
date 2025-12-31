# this is a standalone file just to print the hex for the DS18x20 sensor, it doesn't need to be on deployed devices

# noinspection PyPackageRequirements
import machine
# noinspection PyPackageRequirements
import onewire
import ds18x20


print(ds18x20.DS18X20(onewire.OneWire(machine.Pin(28))).scan()[0].hex())
