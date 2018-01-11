#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import logging
import jodel_api
import json
import time
import argparse
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s    %(message)s', filename="jodel_wetterfrosch.log")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="A script to create weather posts for Jodel.\nTo create a Jodel, supply an account.")
parser.add_argument("-a", "--account", metavar="ACCOUNT_FILE.json")
args = parser.parse_args()


class DataRead(object):
    def __init__(self, lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY,
                 CITY, legacy, pollen_region, pollen_partregion):
        self.expiration_date = expiration_date
        self.distinct_id = distinct_id
        self.refresh_token = refresh_token
        self.device_uid = device_uid
        self.access_token = access_token
        self.lat = lat
        self.lng = lng
        self.city = city
        self.API_KEY = API_KEY
        self.CITY = CITY
        self.legacy = legacy
        self.pollen_region = pollen_region
        self.pollen_partregion = pollen_partregion


def create_data(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY, CITY,
                legacy, pollen_region, pollen_partregion):
    file_data = {
        "lat": lat,
        "lng": lng,
        "city": city,
        "API_KEY": API_KEY,
        "CITY": CITY,
        "expiration_date": expiration_date,
        "distinct_id": distinct_id,
        "refresh_token": refresh_token,
        "device_uid": device_uid,
        "access_token": access_token,
        "legacy": legacy,
        "pollen_region": pollen_region,
        "pollen_partregion": pollen_partregion
    }
    return file_data


def refresh_access(account, lat, lng, city, API_KEY, CITY, legacy, pollen_region, pollen_partregion, filename):
    account.refresh_access_token()
    refreshed_account = account.get_account_data()
    expiration_date = refreshed_account["expiration_date"]
    distinct_id = refreshed_account["distinct_id"]
    refresh_token = refreshed_account["refresh_token"]
    device_uid = refreshed_account["device_uid"]
    access_token = refreshed_account["access_token"]
    write_data(
        create_data(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY,
                    CITY, legacy, pollen_region, pollen_partregion), filename)


def write_data(file_data, filename):
    with open(filename, 'w') as outfile:
        json.dump(file_data, outfile, indent=4)


def read_data(filename):
    with open(filename, 'r') as infile:
        file_data = json.load(infile)

    expiration_date = file_data["expiration_date"]
    distinct_id = file_data["distinct_id"]
    refresh_token = file_data["refresh_token"]
    device_uid = file_data["device_uid"]
    access_token = file_data["access_token"]
    lat = file_data["lat"]
    lng = file_data["lng"]
    city = file_data["city"]
    API_KEY = file_data["API_KEY"]
    CITY = file_data["CITY"]
    legacy = file_data["legacy"]
    pollen_region = file_data["pollen_region"]
    pollen_partregion = file_data["pollen_partregion"]
    return DataRead(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY,
                    CITY, legacy, pollen_region, pollen_partregion)


def replaceEast(string):
    test = list(string)
    for x in range(len(test)):
        if test[x] == "E":
            test[x] = "O"
    return "".join(test)


def sift_pollen_data(region, partregion):
    pollen_data = json.loads(
        requests.get('https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json').content)

    for x in range(len(pollen_data["content"])):
        if pollen_data["content"][x]["region_id"] == region and pollen_data["content"][x]["partregion_id"] == partregion:
            return pollen_data["content"][x]["Pollen"]


def splitdict(orig):
    dict1 = {}
    dict2 = {}
    if "Ambrosia" in orig:
        dict1["Ambrosia"] = orig["Ambrosia"]
    if "Beifuss" in orig:
        dict1["Beifuss"] = orig["Beifuss"]
    if "Birke" in orig:
        dict1["Birke"] = orig["Birke"]
    if "Erle" in orig:
        dict1["Erle"] = orig["Erle"]
    if "Esche" in orig:
        dict1["Esche"] = orig["Esche"]
    if "Gräser" in orig:
        dict2["Gräser"] = orig["Gräser"]
    if "Hasel" in orig:
        dict2["Hasel"] = orig["Hasel"]
    if "Roggen" in orig:
        dict2["Roggen"] = orig["Roggen"]
    return dict1, dict2


data = read_data(args.account)

emojis = {}
emojis["clear"] = "🌞"
emojis["sunny"] = "🌞"
emojis["hazy"] = "🌫🌞"
emojis["fog"] = "🌫"
emojis["cloudy"] = "☁"
emojis["partlycloudy"] = "⛅"
emojis["partlysunny"] = "⛅"
emojis["mostlysunny"] = "🌤"
emojis["mostlycloudy"] = "🌥"
emojis["chancerain"] = "🌦"
emojis["rain"] = "🌧"
emojis["flurries"] = "🌨"
emojis["snow"] = "🌨"
emojis["chancesnow"] = "vielleicht 🌨"
emojis["chanceflurries"] = "vielleicht 🌨"
emojis["tstorms"] = "⛈"
emojis["chancetstorms"] = "vielleicht ⛈"
emojis["sleet"] = "❄🌧"
emojis["chancesleet"] = "vielleicht ❄🌧"

response = requests.get('https://api.wunderground.com/api/%s/forecast/q/zmw:%s.json' % (data.API_KEY, data.CITY))
response_json = response.json()
response = requests.get('https://api.wunderground.com/api/%s/astronomy/q/zmw:%s.json' % (data.API_KEY, data.CITY))
dayl_response_json = response.json()

weekdays_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

for x in range(0, 7):
    if response_json['forecast']['simpleforecast']['forecastday'][0]['date']['weekday_short'] == weekdays_short[x]:
        day = days[x]
        break

d = response_json['forecast']['simpleforecast']['forecastday'][0]['date']['day']
m = response_json['forecast']['simpleforecast']['forecastday'][0]['date']['month']
y = response_json['forecast']['simpleforecast']['forecastday'][0]['date']['year']
date = "%s.%s.%s" % (d, m, y)

h = dayl_response_json['sun_phase']['sunrise']['hour']
m = dayl_response_json['sun_phase']['sunrise']['minute']
sunrise = "%s:%s" % (h, m)

h = dayl_response_json['sun_phase']['sunset']['hour']
m = dayl_response_json['sun_phase']['sunset']['minute']
sunset = "%s:%s" % (h, m)

highTemp = response_json['forecast']['simpleforecast']['forecastday'][0]['high']['celsius']
lowTemp = response_json['forecast']['simpleforecast']['forecastday'][0]['low']['celsius']

maxWind = response_json['forecast']['simpleforecast']['forecastday'][0]['maxwind']['kph']
maxWindDir = response_json['forecast']['simpleforecast']['forecastday'][0]['maxwind']['dir']
aveWind = response_json['forecast']['simpleforecast']['forecastday'][0]['avewind']['kph']
aveWindDir = response_json['forecast']['simpleforecast']['forecastday'][0]['avewind']['dir']

dirs = ["North", "South", "West", "East", "Variable"]
dirs_s = ["N", "S", "W", "E", " "]

for x in range(len(dirs)):
    if maxWindDir == dirs[x]:
        maxWindDir = dirs_s[x]
        break

for x in range(len(dirs)):
    if aveWindDir == dirs[x]:
        aveWindDir = dirs_s[x]
        break

maxWindDir = replaceEast(maxWindDir)
aveWindDir = replaceEast(aveWindDir)

aveHumidity = response_json['forecast']['simpleforecast']['forecastday'][0]['avehumidity']
chanceofrain = response_json['forecast']['simpleforecast']['forecastday'][0]['pop']

conditions = response_json['forecast']['simpleforecast']['forecastday'][0]['icon']

WeatherEmoji = emojis[conditions]

PostData = "++++Wetterjodel++++\nGuten Morgen! Am heutigen {0}, den {1} gibts {2}!\n📈 {3}°C     📉 {4}°C\n🌄 {5}     🌅 {6}\n☔ {7}%     💦 {8}%\n🌬 {9} {10} km/h\n💨 {11} {12} km/h\nEuer #Wetter🐸".format(
    day, date, WeatherEmoji, highTemp, lowTemp, sunrise, sunset, chanceofrain, aveHumidity, aveWindDir, aveWind,
    maxWindDir, maxWind)
logger.info("PostData is: %s", PostData.encode(encoding='utf_8', errors='replace'))

# POLLEN
pollen_for_region = sift_pollen_data(data.pollen_region, data.pollen_partregion)

pollen = {}
if not pollen_for_region["Ambrosia"]["tomorrow"] == "0" and not pollen_for_region["Ambrosia"]["tomorrow"] == "-1":
    pollen["Ambrosia"] = pollen_for_region["Ambrosia"]["tomorrow"]
if not pollen_for_region["Beifuss"]["tomorrow"] == "0" and not pollen_for_region["Beifuss"]["tomorrow"] == "-1":
    pollen["Beifuss"] = pollen_for_region["Beifuss"]["tomorrow"]
if not pollen_for_region["Birke"]["tomorrow"] == "0" and not pollen_for_region["Birke"]["tomorrow"] == "-1":
    pollen["Birke"] = pollen_for_region["Birke"]["tomorrow"]
if not pollen_for_region["Erle"]["tomorrow"] == "0" and not pollen_for_region["Erle"]["tomorrow"] == "-1":
    pollen["Erle"] = pollen_for_region["Erle"]["tomorrow"]
if not pollen_for_region["Esche"]["tomorrow"] == "0" and not pollen_for_region["Esche"]["tomorrow"] == "-1":
    pollen["Esche"] = pollen_for_region["Esche"]["tomorrow"]
if not pollen_for_region["Graeser"]["tomorrow"] == "0" and not pollen_for_region["Graeser"]["tomorrow"] == "-1":
    pollen["Gräser"] = pollen_for_region["Graeser"]["tomorrow"]
if not pollen_for_region["Hasel"]["tomorrow"] == "0" and not pollen_for_region["Hasel"]["tomorrow"] == "-1":
    pollen["Hasel"] = pollen_for_region["Hasel"]["tomorrow"]
if not pollen_for_region["Roggen"]["tomorrow"] == "0" and not pollen_for_region["Roggen"]["tomorrow"] == "-1":
    pollen["Roggen"] = pollen_for_region["Roggen"]["tomorrow"]

if len(pollen) == 0:
    PollenPostData_too_long = False
    PollenPostData = "----Pollenwarnungen----\nHeute keine Belastung durch Pollen! 🎉"
    logger.info("PollenPostData is: %s", PollenPostData.encode(encoding='utf_8', errors='replace'))
elif len(pollen) > 5:
    PollenPostData_too_long = True
    pollen = splitdict(pollen)
    PollenPostData = []
    for x in range(len(pollen)):
        l = []
        if x == 0:
            l.append("----Pollenwarnungen----\n")
        for key, value in pollen[x].items():
            if value == "0-1":
                l.append("{0}: keine bis geringe Belastung\n".format(key))
            if value == "1":
                l.append("{0}: geringe Belastung\n".format(key))
            if value == "1-2":
                l.append("{0}: geringe bis mittlere Belastung\n".format(key))
            if value == "2":
                l.append("{0}: mittlere Belastung\n".format(key))
            if value == "2-3":
                l.append("{0}: mittlere bis hohe Belastung\n".format(key))
            if value == "3":
                l.append("{0}: hohe Belastung\n".format(key))
        PollenPostData.append("".join(l)[:-2])
        logger.info("PollenPostData is: (1) %s  (2)  ", PollenPostData[0].encode(encoding='utf_8', errors='replace'), PollenPostData[1].encode(encoding='utf_8', errors='replace'))
else:
    PollenPostData_too_long = False
    l = []
    l.append("----Pollenwarnungen----")
    for key, value in pollen.items():
        if value == "0-1":
            l.append("\n{0}: keine bis geringe Belastung".format(key))
        if value == "1":
            l.append("\n{0}: geringe Belastung".format(key))
        if value == "1-2":
            l.append("\n{0}: geringe bis mittlere Belastung".format(key))
        if value == "2":
            l.append("\n{0}: mittlere Belastung".format(key))
        if value == "2-3":
            l.append("\n{0}: mittlere bis hohe Belastung".format(key))
        if value == "3":
            l.append("\n{0}: hohe Belastung".format(key))
    PollenPostData = "".join(l)
    logger.info("PollenPostData is: %s", PollenPostData.encode(encoding='utf_8', errors='replace'))


account = jodel_api.JodelAccount(
    lat=data.lat,
    lng=data.lng,
    city=data.city,
    access_token=data.access_token,
    expiration_date=data.expiration_date,
    refresh_token=data.refresh_token,
    distinct_id=data.distinct_id,
    device_uid=data.device_uid,
    is_legacy=data.legacy)

refresh_access(account, data.lat, data.lng, data.city, data.API_KEY, data.CITY, data.legacy, data.pollen_region,
               data.pollen_partregion, args.account)

time.sleep(5)

Post = account.create_post(message=PostData, color="9EC41C")
if "post_id" not in Post[1]:
    time.sleep(10)
    Post = account.create_post(message=PostData, color="9EC41C")
    if "post_id" not in Post[1]:
        logger.info("Weather post could not be sent!\nRaising Exception")
        raise Exception("Weather post could not be sent!")

time.sleep(5)

if PollenPostData_too_long:
    Post2 = []
    for x in range(len(PollenPostData)):
        Post2 = account.create_post(message=PollenPostData[x], ancestor=Post[1]["post_id"])
        if "post_id" not in Post2[1]:
            time.sleep(10)
            Post2.append(account.create_post(message=PollenPostData[x], ancestor=Post[1]["post_id"]))
            if "post_id" not in Post2[1]:
                logger.info("Pollen comment(Part %s) could not be sent!\nRaising Exception", x)
                raise Exception("Pollen comment(Part %s) could not be sent!", x)
        time.sleep(4)
    logger.info("Posts sent. Post ID's are:     Weather post: %s     Pollen comment #1: %s     Pollen comment #2: %s",
                Post[1]["post_id"], Post2[0][1]["post_id"], Post2[1][1]["post_id"])
else:
    Post2 = account.create_post(message=PollenPostData, ancestor=Post[1]["post_id"])
    if "post_id" not in Post2[1]:
        time.sleep(10)
        Post2 = account.create_post(message=PollenPostData, ancestor=Post[1]["post_id"])
        if "post_id" not in Post2[1]:
            logger.info("Pollen comment could not be sent!\nRaising Exception")
            raise Exception("Pollen comment could not be sent!")
    logger.info("Posts sent. Post ID's are:     Weather post: %s     Pollen comment: %s", Post[1]["post_id"],
                Post2[1]["post_id"])
