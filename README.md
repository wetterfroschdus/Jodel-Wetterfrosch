# Jodel-Wetterfrosch 🐸
[![forthebadge](http://forthebadge.com/images/badges/fuck-it-ship-it.svg)](https://forthebadge.com) [![Code Health](https://landscape.io/github/wetterfroschdus/Jodel-Wetterfrosch/master/landscape.svg?style=flat-square)](https://landscape.io/github/wetterfroschdus/Jodel-Wetterfrosch/master)


## Installation
- Clone the repository.
```
git clone https://github.com/wetterfroschdus/Jodel-Wetterfrosch.git
```
- Install the requirement: [jodel_api](https://github.com/nborrmann/jodel_api/)!
```
pip install jodel_api
```
## Setup
- Get an [API Key](https://www.wunderground.com/weather/api/d/pricing.html) from Weather Underground
- Get [login credentials](https://kunden.dwd.de/gdsRegistration/gdsRegistrationStart.do) for the DWD GDS FTP Server
- Use create_account.py to generate the necessary data:
```
python create_account.py
```
 Just follow the instructions 😉

## Usage
Use jodel_wetterfrosch.py to create a weather Jodel:
```
python jodel_wetterfrosch.py -a account_file.json
```








### Weather Data Provider
<a href="https://www.wunderground.com/" target="_blank"><img src="https://icons.wxug.com/logos/PNG/wundergroundLogo_4c_horz.png" 
alt="Weather Underground Logo" height="60" border="0" /></a>

### Pollen Data Provider
<a href="https://www.dwd.de"><img src="https://upload.wikimedia.org/wikipedia/de/thumb/7/7b/DWD-Logo_2013.svg/800px-DWD-Logo_2013.svg.png" 
alt="DWD Logo" height="70" border="0" /></a>
