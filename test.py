from rpi_ws281x import PixelStrip, Color

if PixelStrip:
  exit(0)
else:
  exit(1)