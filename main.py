import time
import os
import shutil
import random
from picamera import PiCamera
from datetime import datetime, timedelta
from time import sleep
from pathlib import Path
from orbit import ISS

"""
#Convert a `skyfield` Angle to an EXIF-appropriate
#representation (rationals)
#e.g. 98° 34' 58.7 to "98/1,34/1,587/10"
#Return a tuple containing a boolean and the converted angle,
#with the boolean indicating if the angle is negative.
"""


def convert(angle):
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds * 10:.0f}/10'
    return sign < 0, exif_angle


"""
#Use `camera` to capture an `image` file with lat/long EXIF data.
"""


def capture(camera, image):
    point = ISS.coordinates()
    # Convert the latitude and longitude to EXIF-appropriate representations
    south, exif_latitude = convert(point.latitude)
    west, exif_longitude = convert(point.longitude)
    # Set the EXIF tags specifying the current location
    camera.exif_tags['GPS.GPSLatitude'] = exif_latitude
    camera.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
    camera.exif_tags['GPS.GPSLongitude'] = exif_longitude
    camera.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"
    # Capture the image
    camera.capture(image)


# We need to initialize camera and set resolution
cam = PiCamera()
cam.resolution = (1296, 972)
# Camera warm-up time
sleep(2)

# Determine working directory - JPG files will be saved here
base_folder = Path(__file__).parent.resolve()
print(base_folder)

# Delete all JPG files from working directory.
# This way we ensure that only current sessions will be saved
# All previously recorded photos need to be manualy moved
# before executing this script again
files_in_directory = os.listdir(base_folder)
filtered_files = [file for file in files_in_directory if file.endswith(".jpg")]
for file in filtered_files:
    path_to_file = os.path.join(base_folder, file)
    os.remove(path_to_file)

# Check if there is enough space on disk to run this script
# exit this script if not
total, used, free = shutil.disk_usage(base_folder)
print("Total: %d GiB" % (total // (2 ** 30)))
print("Used: %d GiB" % (used // (2 ** 30)))
print("Free: %d GiB" % (free // (2 ** 30)))
if (free // (2 ** 30)) < 3:
    print("Not enough disk space")
    quit()

# Create a start_time variable to store the start time
start_time = datetime.now()
# Create a now_time variable to store the current time
now_time = datetime.now()

# Run a loop for 174 minutes
while (now_time < start_time + timedelta(minutes=174)):
    print("Taking photo")
    capture(cam, f"{base_folder}/gps{time.time()}.jpg")

    # Do nothing for half a second
    sleep(0.5)
    # Update the current time
    now_time = datetime.now()