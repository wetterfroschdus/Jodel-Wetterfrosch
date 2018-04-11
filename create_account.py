import json
import sys
from builtins import input
import jodel_api
import requests

class JodelAcc(object):
    def __init__(self, lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, legacy):
        self.access_token = access_token
        self.expiration_date = expiration_date
        self.refresh_token = refresh_token
        self.distinct_id = distinct_id
        self.device_uid = device_uid
        self.lat = lat
        self.lng = lng
        self.city = city
        self.legacy = legacy


class WeatherData(object):
    def __init__(self, API_KEY, LOCATION_code):
        self.API_KEY = API_KEY
        self.LOCATION = LOCATION_code


class PollenData(object):
    def __init__(self, pollen_region, pollen_partregion):
        self.region = pollen_region
        self.partregion = pollen_partregion


def y_n(question):
    answer = ""
    x = 0
    while not answer == "y" and not answer == "n":
        if x == 0:
            answer = input("%s (y/n)\n" % question)
            x = 1
        else:
            print("Invalid Input")
            answer = input("%s (y/n)\n" % question)
    if answer == "y":
        return True
    if answer == "n":
        return False


def write_data(file_data, file_name):
    if ".json" not in file_name:
        file_name = "%s.json" % file_name

    with open(file_name, 'w') as outfile:
        json.dump(file_data, outfile, indent=4)


def create_data(account, weatherdata, pollendata):
    file_data = {
        "lat": account.lat,
        "lng": account.lng,
        "city": account.city,
        "expiration_date": account.expiration_date,
        "distinct_id": account.distinct_id,
        "refresh_token": account.refresh_token,
        "device_uid": account.device_uid,
        "access_token": account.access_token,
        "legacy": account.legacy,
        "pollen_region": pollendata.region,
        "pollen_partregion": pollendata.partregion,
        "API_KEY": weatherdata.API_KEY,
        "LOCATION": weatherdata.LOCATION
    }
    return file_data


def create_account():
    # Get location from user.
    print("Input the location your Jodels should be posted at:\n")
    lat = input("Latitude:\n")
    lng = input("Longitude:\n")
    city = input("City:\n")

    # Try for jodel account
    print("Setting up Jodel account...")
    while True:
        try:
            account = jodel_api.JodelAccount(lat=lat, lng=lng, city=city)
            print("Done.")
            break
        except Exception as ex:
            print(ex)
            if y_n("Something went wrong. Retry?"):
                pass
            else:
                sys.exit()

    # Try to verify account
    print("Verifying account...")
    a = jodel_api.AndroidAccount()
    response = account.verify(a)
    while not response[0] == 200:
        if y_n("Couldn't verify account.\nServer response was: {0}\nRetry?".format(response)):
            response = account.verify(a)
        else:
            sys.exit()
    print("Done.")
    return JodelAcc(lat, lng, city, account.access_token, account.expiration_date, account.refresh_token,
                    account.distinct_id, account.device_uid, account.is_legacy)


def get_data_Weather(lat, lng):
    while True:
        print("Input the data for the Accuweather weather API.\n")
        api_key = input("API Key:\n")
        location_code = check_weather(api_key, lat, lng)
        if location_code == False:
            if y_n("Retry?") == False:
                sys.exit()
        else:
            break
    return WeatherData(API_KEY=api_key, LOCATION_code=location_code)

def check_weather(api_key, lat, lng):
    response = requests.get(
        "https://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=%s&q=%s%%2C%s&details=false&toplevel=true" % (
        api_key, lat, lng))
    if response.status_code == 200:
        response_json = response.json()
    elif response.status_code == 401 or response.status_code == 403:
        print("Invalid API Key, or the API Key doesn't have the necessary permissions.")
        return False
    else:
        if y_n("Something went wrong. Retry?"):
            return False
        else:
            sys.exit()

    try:
        if "Key" in response_json:
            LOCATION_code = response_json["Key"]
            print("Using %s (%s), %s as weather forecast location." % (response_json["EnglishName"], response_json["AdministrativeArea"]["EnglishName"], response_json["Country"]["EnglishName"]))
            return LOCATION_code
    except TypeError:
        print("Got invalid data form weather provider.")
        return False


def get_data_Pollen():
    pollen_data = json.loads(
        requests.get('https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json').content.decode())

    while True:
        print("Pollen regions (Helpful map: https://www.dwd.de/DE/leistungen/gefahrenindizespollen/Gebiete.html")
        for x in range(len(pollen_data["content"])):
            print("{0}.\tRegion:\t\t{1}\n\tPartregion:\t{2}".format(x+1, pollen_data["content"][x]["region_name"],
                                                                pollen_data["content"][x]["partregion_name"]))

        x = int(input("Choose a region by typing it's number:\n"))-1

        try:
            region = pollen_data["content"][x]["region_id"]
            partregion = pollen_data["content"][x]["partregion_id"]
            return PollenData(region, partregion)
        except IndexError:
            print("Not a valid number!")
            if y_n("Retry?"):
                pass
            else:
                raise Exception("User abort on Pollen Data select.")

# Get account file name
filename = input("Choose an account file name:\n")

# Get Jodel, Weather and Pollen data
JodelAccount = create_account()
Weather = get_data_Weather(JodelAccount.lat, JodelAcc.lng)
Pollen = get_data_Pollen()

# Write Data to file
filedata = create_data(JodelAccount, Weather, Pollen)
write_data(filedata, filename)

print('Data has been successfully written. You can now use "jodel_wetterfrosch.py"')