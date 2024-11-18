import board
import neopixel
import time 
import sys
from api import TrainGetter
import requests
from datetime import datetime
from datetime import time as time_of_day


pixels = neopixel.NeoPixel(board.D18, 144, auto_write=False)

NORTHBOUND_START = 75
SOUTHBOUND_START = 0

STATION_COUNT = 23

# Dim the lights between 11PM and 6AM to 30% brightness
DIM_AT = time_of_day(23)
DONE_DIM_AT = time_of_day(6)

DIM_FACTOR = .30

API_KEY = sys.argv[1]

# Using capitol hill has a you are here mark
CAPTIOL_HILL_IDX = 14


northbound_station_leds = [x * 3 + NORTHBOUND_START for x in range(STATION_COUNT)]
southbound_station_leds = [x * 3 + SOUTHBOUND_START  for x in range(STATION_COUNT)]
northbound_station_leds.reverse()


def time_in_between(now, start, end):
    if start <= end:
        return start <= now < end
    else: # over midnight e.g., 23:30-04:15
        return start <= now or now < end

def update():
    for x in range(len(pixels)):
        pixels[x] = (0,0,0)

    # Color capitol hill blue in both directions
    for i, pin in enumerate(northbound_station_leds):
        pixels[pin] = (25,0,0)
        if i == CAPTIOL_HILL_IDX:
            pixels[pin] = (10,0,100)

    for i, pin in enumerate(southbound_station_leds):
        pixels[pin] = (25,0,0)
        if i == CAPTIOL_HILL_IDX:
            pixels[pin] = (10,0,100)


    p = TrainGetter()
    json_str = requests.get(f"https://api.pugetsound.onebusaway.org/api/where/trips-for-route/40_100479.json?key={API_KEY}").text
    trains = p.get_trains(json_str)
    train_leds = []
    train_and_station_leds = []
    for train in trains:
        if train.direction == "N":
            # If train is going north, pull from the northbound set, else pull from the southbound set
            station_leds = northbound_station_leds
        else:
            station_leds = southbound_station_leds


        if train.time_until == 0 or train.leg_total == 0:
            train_and_station_leds.append(station_leds[train.next_station_index])
        else: 
            if train.time_until / train.leg_total < .5:
                train_leds.append(station_leds[train.next_station_index] + 1)
            else:
                train_leds.append(station_leds[train.next_station_index] + 2)

    for led in train_leds:
        # draw trains as green
        pixels[led] = (0, 55, 1)

    for led in train_and_station_leds:
        # draw trains in the station as yellow
        pixels[led] = (35, 25, 0)

    current_time = datetime.now().time()
    if time_in_between(current_time, DIM_AT, DONE_DIM_AT):
        pixels.brightness = DIM_FACTOR
    else:
        pixels.brightness = 1

    pixels.show()



while (True):
    try:
        update()
    except Exception as e:
        print("ERROR")
        print(e)

    time.sleep(15)
