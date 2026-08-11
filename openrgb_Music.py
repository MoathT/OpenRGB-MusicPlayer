import asyncio
import io
import colorsys
import logging
import sys
import time
from PIL import Image

# Windows Media session imports
from winrt.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager
)
from winrt.windows.storage.streams import DataReader

# OpenRGB SDK Client
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor


# ==========================================
# LOGGING SETUP
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("openrgb.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logging.info("==========================================")
logging.info("Starting Spotify OpenRGB Sync Controller")
logging.info("==========================================")


# ==========================================
# OPENRGB CONTROLLER WITH SAFE CLAMPING
# ==========================================
class OpenRGBController:
    def __init__(self, host='127.0.0.1', port=6742):
        logging.info(f"Connecting to OpenRGB Server at {host}:{port}...")
        try:
            self.client = OpenRGBClient(host, port, "Spotify RGB")
            logging.info(f"Connected to OpenRGB! Devices found: {len(self.client.devices)}")
        except Exception as e:
            logging.error(f"Failed to connect to OpenRGB Server: {e}")
            raise e
        
        for device in self.client.devices:
            logging.info(f"Detected Device: {device.name} | Type: {device.type} | LEDs: {len(device.leds)}")
            try:
                device.set_mode('direct')
            except Exception as e:
                logging.warning(f"Could not force direct mode on {device.name}: {e}")

        self.current_c1 = [16.0, 16.0, 16.0]
        self.current_c2 = [32.0, 32.0, 32.0]
        self.target_c1 = [16.0, 16.0, 16.0]
        self.target_c2 = [32.0, 32.0, 32.0]
        
        self.transition_speed = 0.05
        self.running = True

    def set_target_colors(self, hex1, hex2):
        rgb1 = self.hex_to_rgb(hex1)
        rgb2 = self.hex_to_rgb(hex2)
        self.target_c1 = [float(x) for x in rgb1]
        self.target_c2 = [float(x) for x in rgb2]
        logging.info(f"Updated Target RGB: C1={rgb1}, C2={rgb2}")

    @staticmethod
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def clamp(val):
        """Ensures RGB integer values are strictly bounded between 0 and 255."""
        return max(0, min(255, int(round(val))))

    @staticmethod
    def lerp(current, target, factor):
        return current + (target - current) * factor

    def update_transition(self):
        for i in range(3):
            self.current_c1[i] = self.lerp(self.current_c1[i], self.target_c1[i], self.transition_speed)
            self.current_c2[i] = self.lerp(self.current_c2[i], self.target_c2[i], self.transition_speed)

    def apply_to_devices(self):
        r1, g1, b1 = [self.clamp(x) for x in self.current_c1]
        r2, g2, b2 = [self.clamp(x) for x in self.current_c2]

        c1_obj = RGBColor(r1, g1, b1)

        for device in self.client.devices:
            led_count = len(device.leds)
            if led_count == 0:
                continue

            if led_count == 1:
                device.set_color(c1_obj)
            else:
                colors = []
                for i in range(led_count):
                    ratio = i / max(1, (led_count - 1))
                    r = self.clamp(r1 + ratio * (r2 - r1))
                    g = self.clamp(g1 + ratio * (g2 - g1))
                    b = self.clamp(b1 + ratio * (b2 - b1))
                    colors.append(RGBColor(r, g, b))
                
                device.set_colors(colors)

    async def render_loop(self):
        while self.running:
            self.update_transition()
            try:
                self.apply_to_devices()
            except Exception as e:
                logging.error(f"Error applying colors: {e}")
                # Brief pause on error to allow socket buffer recovery
                await asyncio.sleep(0.5)
            await asyncio.sleep(0.05)  # Safe ~20 FPS refresh rate for motherboard controllers


# ==========================================
# MEDIA SESSION HELPERS
# ==========================================
async def get_spotify_session():
    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        return manager.get_current_session()
    except Exception:
        return None

async def get_track(session):
    try:
        return await session.try_get_media_properties_async()
    except Exception:
        return None

async def get_album_art(info):
    try:
        if not info or not info.thumbnail:
            return None
        stream = await info.thumbnail.open_read_async()
        reader = DataReader(stream)
        await reader.load_async(stream.size)
        data = bytearray(stream.size)
        reader.read_bytes(data)
        reader.close()
        return bytes(data)
    except Exception:
        return None

def get_colors(image_data):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image.thumbnail((120, 120))
    
    pixels = [image.getpixel((x, y)) for y in range(image.height) for x in range(image.width)]

    colorful = []
    for r, g, b in pixels:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s >= 0.35 and v >= 0.08:
            colorful.append((r, g, b, h, s, v))

    if not colorful:
        return "#202020", "#050505"

    bins = 36
    histogram = [0.0] * bins
    for r, g, b, h, s, v in colorful:
        index = int(h * bins) % bins
        histogram[index] += s * (0.4 + v)

    dominant_bin = max(range(bins), key=lambda i: histogram[i])
    dominant_hue = (dominant_bin + 0.5) / bins

    dominant = []
    for r, g, b, h, s, v in colorful:
        distance = abs(h - dominant_hue)
        distance = min(distance, 1 - distance)
        if distance < 0.10:
            dominant.append((r, g, b, h, s, v))

    if not dominant:
        dominant = colorful

    strongest = max(dominant, key=lambda p: p[4] * 0.75 + p[5] * 0.25)
    r, g, b = strongest[:3]

    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    s = min(1.0, s * 1.25)
    v = min(0.82, max(0.35, v))

    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    color1 = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    dark_v = 0.035
    r2, g2, b2 = colorsys.hsv_to_rgb(h, min(1.0, s * 1.2), dark_v)
    color2 = "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))

    return color1, color2


# ==========================================
# MAIN EXECUTION
# ==========================================
async def main():
    try:
        rgb_controller = OpenRGBController()
    except Exception:
        logging.critical("Could not initialize OpenRGB. Is OpenRGB running with SDK Server started?")
        return

    asyncio.create_task(rgb_controller.render_loop())

    last_title, last_artist, last_album = None, None, None

    while True:
        try:
            session = await get_spotify_session()

            if not session:
                if last_title is not None:
                    logging.info("Spotify closed or inactive. Waiting for media...")
                    last_title, last_artist, last_album = None, None, None
                await asyncio.sleep(3)
                continue

            info = await get_track(session)
            if not info or not info.title:
                await asyncio.sleep(2)
                continue

            title, artist, album = info.title, info.artist, info.album_title

            if title != last_title or artist != last_artist or album != last_album:
                last_title, last_artist, last_album = title, artist, album

                logging.info(f"Now Playing: {artist} - {title} (Album: {album})")

                image_data = await get_album_art(info)
                if image_data:
                    color1, color2 = get_colors(image_data)
                    logging.info(f"Extracted Hex Colors: {color1} | {color2}")
                    rgb_controller.set_target_colors(color1, color2)
                else:
                    logging.warning("No album art available.")

            await asyncio.sleep(1)

        except Exception as error:
            logging.warning(f"Media handle disconnected ({error}). Auto-reconnecting...")
            last_title, last_artist, last_album = None, None, None
            await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())