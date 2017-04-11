import requests
import logging
import jodel_api
import json
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s    %(message)s', filename="jodel_wetterfrosch.log")
logger = logging.getLogger(__name__)

class DataRead(object):
    def __init__(self, lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY, CITY):
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

def write_data(file_data):
    with open('account.json', 'w') as outfile:
        json.dump(file_data, outfile, indent=4)

def create_data(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY, CITY):
    file_data = {
        "lat":lat,
        "lng":lng,
        "city":city,
        "API_KEY":API_KEY,
        "CITY":CITY,
        "expiration_date":expiration_date,
        "distinct_id":distinct_id,
        "refresh_token":refresh_token,
        "device_uid":device_uid,
        "access_token":access_token
        }
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

def read_data():
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
    return DataRead(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY, CITY)

data = read_data()

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

conditions = response_json['forecast']['simpleforecast']['forecastday'][0]['icon']

WeatherEmoji = emojis[conditions]
logger.info('Weather is "%s". Weather emoji is: %s' % (conditions,WeatherEmoji))

PostData = "++++Wetterjodel++++\nGuten Morgen! Am heutigen {0}, den {1} gibts {2}!\n📈 {3}°C     📉 {4}°C\n🌄 {5}     🌅 {6}\n☔ {7}%     💦 {8}%\n🌬 {9} {10} km/h\n💨 {11} {12} km/h\nEuer #Wetter🐸".format(day, date, WeatherEmoji, highTemp, lowTemp, sunrise, sunset, chanceofrain, aveHumidity, aveWindDir, aveWind, maxWindDir, maxWind)
logger.info("PostData is:\n%s" % PostData.encode(encoding='utf_8', errors='replace'))

account = jodel_api.JodelAccount(
    lat = data.lat,
    lng = data.lng,
    city = data.city,
    access_token = data.access_token,
    expiration_date = data.expiration_date,
    refresh_token = data.refresh_token,
    distinct_id = data.distinct_id,
    device_uid = data.device_uid)

refresh_access(account, data.lat, data.lng, data.city, data.API_KEY, data.CITY)

time.sleep(5)

time.sleep(5)

Post = account.create_post(message=PostData, color="9EC41C")
if "post_id" not in Post[1]:
    time.sleep(10)
    Post = account.create_post(message=PostData, color="9EC41C")
    if "post_id" not in Post[1] :
        logger.info("Weather post could not be sent!\nRaising Exception")
        raise Exception("Weather post could not be sent!")

time.sleep(2)

Post2 = account.create_post(message="Quaaaaak!\nIch bin ein digitaler 🐸!\n\nWeitere Infos unter:\njodel-wetterfrosch.tk", ancestor=Post[1]["post_id"])
if "post_id" not  in Post2[1] :
    time.sleep(10)
    Post2 = account.create_post(message="Quaaaaak!\nIch bin ein digitaler 🐸!\n\nWeitere Infos unter:\njodel-wetterfrosch.tk", ancestor=Post[1]["post_id"])
    if "post_id" not  in Post2[1] :
        logger.info("Bot comment could not be sent!\nRaising Exception")
        raise Exception("Bot comment could not be sent!")
        
logger.info("Posts sent. Post ID's are:     Weather post: %s     Bot comment: %s"% (Post[1]["post_id"], Post2[1]["post_id"]))
