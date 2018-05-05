import jodel_api
import json
import argparse
import os
import time
import logging

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s\t%(message)s',
                    filename="get_karma.log")
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="A script to get the Karma for a Jodel account..\nTo view Karma, supply an account.")
parser.add_argument("-a", "--account", metavar="ACCOUNT_FILE.json")
args = parser.parse_args()


# Object for storing the json data, which is read from the account file by read_data().
class DataRead(object):
    def __init__(self, lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY,
                 LOCATION, legacy, pollen_region, pollen_partregion):
        self.expiration_date = expiration_date
        self.distinct_id = distinct_id
        self.refresh_token = refresh_token
        self.device_uid = device_uid
        self.access_token = access_token
        self.lat = lat
        self.lng = lng
        self.city = city
        self.API_KEY = API_KEY
        self.LOCATION = LOCATION
        self.legacy = legacy
        self.pollen_region = pollen_region
        self.pollen_partregion = pollen_partregion


# create_data() turns the updated data into json format.
def create_data(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY, LOCATION,
                legacy, pollen_region, pollen_partregion):
    file_data = {
        "lat": lat,
        "lng": lng,
        "city": city,
        "expiration_date": expiration_date,
        "distinct_id": distinct_id,
        "refresh_token": refresh_token,
        "device_uid": device_uid,
        "access_token": access_token,
        "legacy": legacy,
        "pollen_region": pollen_region,
        "pollen_partregion": pollen_partregion,
        "API_KEY": API_KEY,
        "LOCATION": LOCATION
    }
    return file_data


# refresh_access() takes the Jodel account and refreshes the access token.
# It will then write the data back to the account file.
def refresh_access(account, file_data, filename):
    account.refresh_access_token()

    refreshed_account = account.get_account_data()
    expiration_date = refreshed_account["expiration_date"]
    distinct_id = refreshed_account["distinct_id"]
    refresh_token = refreshed_account["refresh_token"]
    device_uid = refreshed_account["device_uid"]
    access_token = refreshed_account["access_token"]

    filedata = create_data(file_data.lat, file_data.lng, file_data.city, access_token, expiration_date, refresh_token,
                            distinct_id, device_uid, file_data.API_KEY, file_data.LOCATION, file_data.legacy,
                             file_data.pollen_region, file_data.pollen_partregion)

    write_data(filedata, filename)


# refresh_all() initializes the Jodel account without remote calls and refreshes all tokens.
# It will then write the data back to the account file and return the Jodel account.
def refresh_all(file_data, filename):
    jodel_account = jodel_api.JodelAccount(
        lat=file_data.lat,
        lng=file_data.lng,
        city=file_data.city,
        access_token=file_data.access_token,
        expiration_date=file_data.expiration_date,
        refresh_token=file_data.refresh_token,
        distinct_id=file_data.distinct_id,
        device_uid=file_data.device_uid,
        is_legacy=file_data.legacy,
        update_location=False)

    jodel_account.refresh_all_tokens()

    refreshed_account = jodel_account.get_account_data()
    expiration_date = refreshed_account["expiration_date"]
    distinct_id = refreshed_account["distinct_id"]
    refresh_token = refreshed_account["refresh_token"]
    device_uid = refreshed_account["device_uid"]
    access_token = refreshed_account["access_token"]

    filedata = create_data(file_data.lat, file_data.lng, file_data.city, access_token, expiration_date, refresh_token,
                distinct_id, device_uid, file_data.API_KEY, file_data.LOCATION, file_data.legacy, file_data.pollen_region,
                 file_data.pollen_partregion)

    write_data(filedata, filename)

    return jodel_account


# write_data() writes the json data to the account file.
def write_data(file_data, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(file_data, outfile, indent=4)


# read_data() reads the json data from the account file and returns it as a DataRead object.
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
    legacy = file_data["legacy"]
    pollen_region = file_data["pollen_region"]
    pollen_partregion = file_data["pollen_partregion"]
    API_KEY = file_data["API_KEY"]
    LOCATION = file_data["LOCATION"]
    return DataRead(lat, lng, city, access_token, expiration_date, refresh_token, distinct_id, device_uid, API_KEY,
                    LOCATION, legacy, pollen_region, pollen_partregion)


if __name__=='__main__':
    # Read the account file into a DataRead Object "data".
    try:
        data = read_data(args.account)
        logger.info("Using account file: %s", args.account)
    except TypeError:
        logger.error("No account file specified!")
        raise Exception("No account file specified!")
    except:
        logger.error("An unknown error occurred while parsing the account file.")
        raise Exception("An unknown error occurred while parsing the account file.")

    if __name__ == '__main__':
        # Read the account file into a DataRead Object "data".
        try:
            data = read_data(args.account)
            logger.info("Using account file: %s", args.account)
        except TypeError:
            logger.error("No account file specified!")
            raise Exception("No account file specified!")
        except:
            logger.error("An unknown error occurred while parsing the account file.")
            raise Exception("An unknown error occurred while parsing the account file.")


        # Initializes the Jodel account.
        try:
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
        except Exception as Ex:
            if Ex.args[0] == "Error updating location: (401, 'Unauthorized')":
                account = refresh_all(data, args.account)
            else:
                raise Ex
        else:
            # Refresh access using refresh_access(), which also writes the new tokens back to the account file.
            # But only if the access_token has expired or will expire within the next 5 minutes.
            epoch_time = int(time.time()) - 300
            if epoch_time > data.expiration_date:
                refresh_access(account, data, args.account)


    daten = account.get_karma()
    karma = daten[1]["karma"]

    print("{0}".format(karma))