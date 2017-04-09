import requests
import logging
from multi_key_dict import multi_key_dict
import jodel_api
import json
import hashlib
import time
import os

logging.basicConfig(level=logging.INFO, filename="jodel_wetterfrosch.log")
logger = logging.getLogger(__name__)

def write_data(file_data):
    with open('account.json', 'w') as outfile:
        json.dump(file_data, outfile, indent=4)

def create_data(lat,lng,city,access_token,expiration_date,refresh_token,distinct_id,device_uid,API_KEY,CITY):
    file_data = {"lat":lat,"lng":lng,"city":city,"API_KEY":API_KEY,"CITY":CITY,"expiration_date":expiration_date,"distinct_id":distinct_id,"refresh_token":refresh_token,"device_uid":device_uid,"access_token":access_token}
    chksm = hashlib.md5(str(file_data).encode("utf-8")).hexdigest()
    file_data = {"lat":lat,"lng":lng,"city":city,"API_KEY":API_KEY,"CITY":CITY,"expiration_date":expiration_date,"distinct_id":distinct_id,"refresh_token":refresh_token,"device_uid":device_uid,"access_token":access_token,"chksm":chksm}
    return file_data

def refresh_access(account, lat, lng, city, API_KEY, CITY):
    account.refresh_access_token()
    refreshed_account = account.get_account_data()
    expiration_date = refreshed_account["expiration_date"]
    distinct_id = refreshed_account["distinct_id"]
    refresh_token = refreshed_account["refresh_token"]
    device_uid = refreshed_account["device_uid"]
    access_token = refreshed_account["access_token"]
    write_data(create_data(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY, CITY))

def conditions_simplify(weather):
    if "Fog" in weather:
        if weather == "Freezing Fog":
            return weather
        else:
            return "Fog"
    elif "Dust" in weather:
        return "Dust"
    elif "Sand" in weather:
        return "Sand"
    elif "Unknown" in weather:
        return "Unknown"
    elif "Light" in weather or "Heavy" in weather:
        return weather[5:]
    elif weather:
        return weather

with open('account.json', 'r') as infile:
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
chksm = file_data["chksm"]

data_read = {"lat":lat,"lng":lng,"city":city,"API_KEY":API_KEY,"CITY":CITY,"expiration_date":expiration_date,"distinct_id":distinct_id,"refresh_token":refresh_token,"device_uid":device_uid,"access_token":access_token}

emojis = multi_key_dict()
emojis["Clear"] = "🌞"
emojis["Squalls"] = "💨"
emojis["Mist","Fog","Smoke","Volcanic Ash","Dust","Sand","Haze"] = "🌫"
emojis["Overcast"] = "☁"
emojis["Funnel Cloud"] = "🌪"
emojis["Partly Cloudy"] = "⛅"
emojis["Scattered Clouds"] = "🌤"
emojis["Mostly Cloudy"] = "🌥"
emojis["Rain Showers"] = "🌦"
emojis["Rain","Drizzle","Rain Mist","Spray"] = "🌧"
emojis["Snow","Snow Grains","Low Drifting Snow","Blowing Snow","Snow Blowing Snow Mist","Snow Showers"] = "🌨"
emojis["Thunderstorm"] = "🌩"
emojis["Thunderstorms and Rain","Thunderstorms and Snow","Thunderstorms and Ice Pellets","Thunderstorms with Hail","Thunderstorms with Small Hail"] = "⛈"
emojis["Freezing Drizzle","Freezing Rain","Small Hail","Ice Pellet Showers","Hail Showers","Small Hail Showers","Hail","Ice Crystals","Ice Pellets"] = "❄🌧"
emojis["Freezing Fog"] = "❄🌫"
emojis["Unknown"] = "NOPE"

response = requests.get('https://api.wunderground.com/api/%s/forecast/q/zmw:%s.json' % (API_KEY, CITY))
response_json = response.json()
response = requests.get('https://api.wunderground.com/api/%s/astronomy/q/zmw:%s.json' % (API_KEY, CITY))
dayl_response_json = response.json()

weekdays_short = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
days = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]

for x in range(0,7):
    if response_json['forecast']['simpleforecast']['forecastday'][0]['date']['weekday_short'] == weekdays_short[x]:
        day = days[x]
        break

d = response_json['forecast']['simpleforecast']['forecastday'][0]['date']['day']
m = response_json['forecast']['simpleforecast']['forecastday'][0]['date']['month']
y = response_json['forecast']['simpleforecast']['forecastday'][0]['date']['year']
date = "%s.%s.%s" % (d, m , y)

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

for x in range(0,5):
    if maxWindDir == dirs[x]:
        maxWindDir = dirs_s[x]
        break
for x in range(0,5):
    if aveWindDir == dirs[x]:
        aveWindDir = dirs_s[x]
        break

aveHumidity = response_json['forecast']['simpleforecast']['forecastday'][0]['avehumidity']
chanceofrain = response_json['forecast']['simpleforecast']['forecastday'][0]['pop']

conditions = response_json['forecast']['simpleforecast']['forecastday'][0]['conditions']

WeatherEmoji = emojis[conditions_simplify(conditions)]
logger.info('Weather is "%s". Simplified Weather is %s. Weather emoji is: %s' % (conditions,conditions_simplify(conditions),WeatherEmoji))

if WeatherEmoji == "NOPE":
    raise Exception("Response for 'condition' from Weather Provider was '{0}'.\nNo Emoji specified for {1}.".format(conditions, conditions))

PostData = "++++Wetterjodel++++\nGuten Morgen! Am heutigen {0}, den {1} wirds {2}!\n📈 {3}°C     📉 {4}°C\n🌄 {5}     🌅 {6}\n☔ {7}%     💦 {8}%\n🌬 {9} {10} km/h\n💨 {11} {12} km/h\nEuer #Wetter🐸".format(day, date, WeatherEmoji, highTemp, lowTemp, sunrise, sunset, chanceofrain, aveHumidity, aveWindDir, aveWind, maxWindDir, maxWind)
logger.info("PostData is:\n%s" % PostData)

account = jodel_api.JodelAccount(lat=lat, lng=lng, city=city, access_token=access_token, expiration_date=expiration_date,refresh_token=refresh_token, distinct_id=distinct_id, device_uid=device_uid)
refresh_access(account, lat, lng, city, API_KEY, CITY)

Post = account.create_post(message=PostData, color="9EC41C")
if not "post_id" in Post[1]:
    time.sleep(10)
    Post = account.create_post(message=PostData, color="9EC41C")
    if not "post_id" in Post[1]:
        Exception("Weather post could not be sent!")
logger.info("Post return data is: %s" % Post)
time.sleep(2)

Post2 = account.create_post(message="Quaaaaak!\nIch bin ein digitaler 🐸!\n\nWeitere Infos unter:\nWetterfroschdus.tk", ancestor=Post[1]["post_id"])
if not "post_id" in Post2[1] :
    time.sleep(10)
    Post2 = account.create_post(message="Quaaaaak!\nIch bin ein digitaler 🐸!\n\nWeitere Infos unter:\nWetterfroschdus.tk", ancestor="{0}".format(Post[1]["post_id"]))
    if not "post_id" in Post2[1] :
        raise Exception("Bot comment could not be sent!")

logger.info("Post2 return data is: %s" % Post)
logger.info("Posts sent. Post ID's are:\nWeather post: %s\nBot comment: %s" % (Post[1]["post_id"],Post2[1]["post_id"]))
