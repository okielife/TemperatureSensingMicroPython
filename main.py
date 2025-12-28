from binascii import b2a_base64
from ds18x20 import DS18X20
from machine import Pin, SPI
from network import WLAN, STA_IF
from ntptime import settime
from onewire import OneWire 
from time import sleep, sleep_ms, ticks_ms, ticks_diff, localtime
from urequests import put

from st7735 import TFT, FONT, TFTColor

from config import WIFI_NETWORKS, GITHUB_PUSH_INTERVAL_MS, CONNECTED_SENSORS, GITHUB_TOKEN


class Sensor:
    def __init__(self, ds: DS18X20, rom: bytes, name: str, label: str):
        self.ds = ds
        self.rom = rom
        self.name = name
        self.label = label
        self.temperature_f = None
        self.temperature_c = None


class Display(TFT):
    WIDTH = 128
    HEIGHT = 160
    PIN_DC = 16
    PIN_CS = 17
    PIN_SCI_SCK = 18
    PIN_SDA_MOSI = 19
    PIN_RESET = 20
    PIN_LED = 21
    
    def __init__(self):
        spi = SPI(0, baudrate=20_000_000, polarity=0, phase=0, sck=Pin(self.PIN_SCI_SCK), mosi=Pin(self.PIN_SDA_MOSI))
        super().__init__(spi, aDC=self.PIN_DC, aReset=self.PIN_RESET, aCS=self.PIN_CS, ScreenSize=(self.WIDTH, self.HEIGHT))
        self.initr()
        Pin(self.PIN_LED, Pin.OUT).on()
        self.rgb(False)
        self.fill(TFT.BLACK)

    def text(self, point: tuple[int, int], text: str, color: TFTColor, size: int):
        super().text(point, text, color, FONT, size, nowrap=True)

    def regular_update(self, runner):
        self.fill(TFT.BLACK)
        # SENSOR INFORMATION
        self.hline((0, 5), 24, TFT.GRAY)
        self.hline((0, 10), 24, TFT.GRAY)
        self.hline((106, 5), 24, TFT.GRAY)
        self.hline((106, 10), 24, TFT.GRAY)
        self.text((27, 0), "Sensors", TFT.WHITE, 2)
        # Need to alert here on the screen if the sensor data is bad
        y = 20
        for sensor in runner.sensors:
            self.text((0, y), sensor.name, TFT.WHITE, 1)
            y += 10
            if sensor.temperature_f:
                self.text((0, y), f"({sensor.label}) Temp: {sensor.temperature_f:5.2f} F", TFT.WHITE, 1)
            else:
                self.text((0, y), f"({sensor.label}) Temp: NULL", TFT.YELLOW, 1)
            y += 10
        # WIFI INFORMATION
        self.hline((0, 71), 40, TFT.GRAY)
        self.hline((0, 76), 40, TFT.GRAY)
        self.hline((88, 71), 40, TFT.GRAY)
        self.hline((88, 76), 40, TFT.GRAY)
        self.text((44, 66), "WiFi", TFT.WHITE, 2)
        if runner.wlan.isconnected():
            self.text((0, 85), f"Connected!", TFT.GREEN, 1)
            self.text((0, 95), f"SSID: {runner.wlan.ssid}", TFT.WHITE, 1)
            self.text((0, 105), f"IP: {runner.wlan.ip}", TFT.WHITE, 1)
        else:
            self.text((0, 85), "****DISCONNECTED****", TFT.RED, 1)
        # UPDATE INFORMATION
        self.hline((0, 125), 24, TFT.GRAY)
        self.hline((0, 130), 24, TFT.GRAY)
        self.hline((106, 125), 24, TFT.GRAY)
        self.hline((106, 130), 24, TFT.GRAY)
        self.text((27, 120), "Updates", TFT.WHITE, 2)
        if runner.last_temp_stamp:
            temp_time_text = "Read: {:02d}:{:02d}:{:02d} (UTC)".format(runner.last_temp_stamp[3], runner.last_temp_stamp[4], runner.last_temp_stamp[5])
            self.text((0, 140), temp_time_text, TFT.WHITE, 1)
        else:
            self.text((0, 140), "Read: NEVER", TFT.YELLOW, 1)
        if runner.last_push_had_errors:
            self.text((0, 150), "Last Push Had Errors", TFT.RED, 1)
        elif runner.last_push_stamp:
            github_time_text = "Push: {:02d}:{:02d}:{:02d} (UTC)".format(runner.last_push_stamp[3], runner.last_push_stamp[4], runner.last_push_stamp[5])
            self.text((0, 150), github_time_text, TFT.WHITE, 1)
        else:
            self.text((0, 150), "Push: NEVER", TFT.YELLOW, 1)

    def show_exception(self, exc):
        self.fill(TFT.BLACK)
        self.text((0, 5), "*EXCEPTION*", TFT.RED, 2)
        y = 25
        # from sys import print_exception
        # from io import StringIO
        # buf = StringIO()
        # print_exception(exc, buf)
        # msg = buf.getvalue()
        msg = str(exc)
        for i in range(0, len(msg), 20):
            self.text((0, y), (msg[i:i+20]), TFT.RED, 1)
            y += 10
        print(msg)


class WiFi(WLAN):
    def __init__(self):
        super().__init__(STA_IF)
        self.active(True)
        self.ip = ""
        self.ssid = ""
        self.time_synced = False
        if self.isconnected():
            self.ip, _, _, _ = self.ifconfig()
            self.ssid = self.config('ssid')
            
    def try_to_connect(self) -> bool:
        self.ssid = ""
        self.ip = ""
        self.time_synced = False
        wifi_connect_timeout_ms = 10_000
        available = {net[0].decode() for net in self.scan()}
        for ssid, pw in WIFI_NETWORKS:
            if ssid not in available:
                continue
            super().connect(ssid, pw)
            start = ticks_ms()
            while not self.isconnected():
                if ticks_diff(ticks_ms(), start) > wifi_connect_timeout_ms:
                    break
                sleep_ms(200)
            if self.isconnected():
                self.ip, _, _, _ = self.ifconfig()
                self.ssid = self.config('ssid')


class Runner:
    def __init__(self):
        self.led = Pin("LED", machine.Pin.OUT)
        try:
            self.tft = Display()
        except Exception as e:
            print(f"Could not initialize display: {e}")
            while True:  # just hang here forever, we can't go on without a screen
                self.flash_led(3)
                sleep(2)
        self.tft.text((15, 0), "STARTING", TFT.GREEN, 2)
        self.tft.text((0, 20), "Screen:  OK", TFT.WHITE, 2)
        self.wlan = WiFi()
        if self.wlan.isconnected():
            self.tft.text((0, 40), "Wi-Fi:   OK", TFT.WHITE, 2)
        else:
            self.tft.text((0, 40), "Wi-Fi:  ERR", TFT.RED, 2)
        ow = OneWire(Pin(28))
        ds = DS18X20(ow)
        scanned_roms = ds.scan()
        print(f"{scanned_roms=}")
        self.sensors = []
        for search_id, search_hex, search_name in CONNECTED_SENSORS:
            print(f"Searching for rom with hex {search_hex}")
            try:
                for rom in scanned_roms:
                    sensor_hex = rom.hex()
                    print(f"inspecting scanned rom with hex: {sensor_hex}")
                    if sensor_hex == search_hex:
                        self.sensors.append(Sensor(ds, rom, search_name, search_id))
                        break
                else: # we made it through the search loop and didn't break out, so we ended up here, meaning we couldn't find the one
                    pass
            except Exception as e:
                raise RuntimeError(f"Could not initialize sensor {search_name} with label {search_id}") from e
        # TODO: Throw exception if size of self.sensors != size of CONNECTED_SENSORS
        self.tft.text((0, 60), "Sensors: OK", TFT.WHITE, 2)
        try:
            self.sync_time()  # do this once each boot for sure
            self.tft.text((0, 80), "Clock:   OK", TFT.WHITE, 2)
            t = localtime()
            self.tft.text((0, 100), "Date: {:02d}/{:02d}".format(t[1], t[2]), TFT.WHITE, 2)
            self.tft.text((0, 120), "UTC:  {:02d}:{:02d}".format(t[3], t[4]), TFT.WHITE, 2)
        except Exception as e:
            self.tft.text((0, 80), "CLOCK ERROR", TFT.RED, 2)
        
        sleep(2)
        self.last_temp_stamp = None
        self.last_push_stamp = None
        self.last_push_had_errors = False
        self.last_push_ms = 0
        
    def run(self):
        self.tft.regular_update(self)
        while True:
            try:
                if not self.wlan.isconnected():
                    # try to connect, but if we can't after 10 seconds, just continue to updating temps and looping
                    self.wlan.try_to_connect()
                if not self.wlan.time_synced:
                    self.sync_time()
                self.update_temperatures()
                self.last_temp_stamp = localtime()
                if self.wlan.isconnected() and ticks_diff(ticks_ms(), self.last_push_ms) > GITHUB_PUSH_INTERVAL_MS:
                    all_successful = self.push_to_github()
                    if all_successful:
                        self.last_push_ms = ticks_ms()
                        self.last_push_stamp = localtime()
                        self.last_push_had_errors = False
                    else:
                        self.last_push_had_errors = True
                self.tft.regular_update(self)
                sleep(5)
            except KeyboardInterrupt:  # pragma: no cover
                self.print("Encountered keyboard interrupt, exiting")
                return
            except Exception as e:
                print(e)
                self.tft.show_exception(e)
                sleep(30)

    def update_temperatures(self):
        for sensor in self.sensors:
            try:
                sensor.ds.convert_temp()
                sleep_ms(750)  # wait 750ms after calling convert_temp and before sampling temps
                sensor.temperature_c = sensor.ds.read_temp(sensor.rom)
                sensor.temperature_f = (sensor.temperature_c * 9.0 / 5.0) + 32.0
            except Exception as e:
                raise Exception(f"Could not get temperature from sensor named {sensor.name}") from e

    def sync_time(self):
        try:
            #settime()  # will be in UTC always, fine for now
            self.wlan.time_synced = True
        except Exception as e:
            raise Exception(f"Error syncing time: {e}") from e

    def push_to_github(self) -> bool:
        # we will return true if all were successful, but if any fail, it's fine, the unresponsive sensor check will alert us
        all_success = True
        t = localtime()
        current = f"{t[0]}-{t[1]:02d}-{t[2]:02d}-{t[3]:02d}-{t[4]:02d}-{t[5]:02d}"
        any_errors = False
        for sensor in self.sensors:
            file_content = f"""---
sensor_id: {sensor.name}
temperature: {sensor.temperature_c}
measurement_time: {current}
---
{{}}
"""
            file_name = f"{current}_{sensor.name}.html"
            file_path = f"_posts/{sensor.name}/{file_name}"
            url = f"https://api.github.com/repos/okielife/TempSensors/contents/{file_path}"
            headers = {'Accept': 'application/vnd.github + json', 'User-Agent': 'Temp Sensor', 'Authorization': f'Token {GITHUB_TOKEN}'}
            encoded_content = b2a_base64(file_content.encode()).decode()
            data = {'message': f"Updating {file_path}", 'content': encoded_content}
            try:
                response = put(url, headers=headers, json=data)
            except (RuntimeError, OSError) as e:
                print(f"Could not send request, reason={e}, skipping this report, checks will continue")
                all_success = False
            if response.status_code not in (200, 201):
                print(f"PUT Error: {response.text}")
                all_success = False
        return all_success
    
    def flash_led(self, num_times: int) -> None:
        self.led.off()
        for i in range(num_times * 2):
            sleep(0.2)
            self.led.toggle()
        self.led.off()


if __name__ == "__main__":
    usb_connected = Pin(24, Pin.IN).value()
    if usb_connected:
        print("USB detected – skipping auto start")
        sleep(2)  # give Thonny time to connect
    else:
        Runner().run()


