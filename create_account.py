import json
import jodel_api
import requests
from operator import itemgetter
from builtins import input


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
    def __init__(self, API_KEY, CITY_code):
        self.API_KEY = API_KEY
        self.CITY = CITY_code


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
        "CITY": weatherdata.CITY
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
        except:
            if y_n("Something went wrong. Retry?"):
                pass
            else:
                raise Exception("User abort on Jodel Account creation.")

    # Try to verify account
    print("Verifying account...")
    if y_n("Do you have an android account? (android_id and security_token)?\nThis will increase the success chance of the verification."):
        android_id = int(input("android_id:\n"))
        security_token = int(input("security_token:\n"))
        a = jodel_api.AndroidAccount(android_id, security_token)
    else:
        a = jodel_api.AndroidAccount()

    response = account.verify(a)
    while not response[0] == 200:
        if y_n("Couldn't verify account.\nServer response was: {0}\nRetry?".format(response)):
            response = account.verify(a)
        else:
            raise Exception("User abort on Jodel Account verification.")
    print("Done.")
    return JodelAcc(lat, lng, city, account.access_token, account.expiration_date, account.refresh_token,
                    account.distinct_id, account.device_uid, account.is_legacy)


def get_data_Weather():
    while True:
        print("Input the data for the Wunderground weather API.\n")
        API_KEY = input("API Key:\n")
        COUNTRY = input("Country:\n")
        CITY = input("City:\n")
        CITY_code = check_weather(API_KEY, COUNTRY, CITY)
        if CITY_code == False:
            if y_n("Retry?") == False:
                raise Exception("User abort on Weather Data select.")
        else:
            break
    return WeatherData(API_KEY=API_KEY, CITY_code=CITY_code)


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


def check_weather(API_KEY, COUNTRY, CITY):
    response = requests.get("https://api.wunderground.com/api/%s/geolookup/q/%s/%s.json" % (API_KEY, COUNTRY, CITY))
    response_json = response.json()
    if "location" in response_json:
        CITY_code = response_json["location"]["l"]
        CITY_code = CITY_code[7:]
        return CITY_code

    if "error" in response_json["response"]:
        if response_json["response"]["error"]["type"] == "keynotfound":
            print("Invalid API Key!")
            return False
        elif response_json["response"]["error"]["type"] == "querynotfound":
            print("City not found!")
            return False

    results_sorted = sorted(response_json["response"]["results"], key=itemgetter('country_name'))
    if "results" in response_json["response"]:
        results_num = 0
        for item in results_sorted:
            print("{0}. {1}, {2}, {3}".format(results_num, item["name"], item["state"], item["country_name"]))
            results_num = results_num + 1
        CITY_code = (results_sorted[int(input("Choose a city by typing it's number:\n"))])["zmw"]
        return CITY_code

    raise Exception("Got invalid data from Weather Provider.\nData:%s" % response_json)

# Get account file name
filename = input("Choose an account file name:\n")

# Get Jodel, Weather and Pollen data
JodelAccount = create_account()
Weather = get_data_Weather()
Pollen = get_data_Pollen()

# Write Data to file
filedata = create_data(JodelAccount, Weather, Pollen)
write_data(filedata, filename)

print('Data has been successfully written. You can now use "jodel_wetterfrosch.py"')