# Jodel-Wetterfrosch 🐸
[![Code Health](https://landscape.io/github/wetterfroschdus/Jodel-Wetterfrosch/master/landscape.svg?style=flat)](https://landscape.io/github/wetterfroschdus/Jodel-Wetterfrosch/master)                                                                 
![Karma Hamburg](https://rawgit.com/wetterfroschdus/karma-badges/master/hamburg.svg) ![Karma Bremen](https://rawgit.com/wetterfroschdus/karma-badges/master/bremen.svg) ![Karma Düsseldorf](https://rawgit.com/wetterfroschdus/karma-badges/master/dusseldorf.svg) ![Karma Dortmund](https://rawgit.com/wetterfroschdus/karma-badges/master/dortmund.svg) ![Karma Mönchengladbach](https://rawgit.com/wetterfroschdus/karma-badges/master/mgladbach.svg) ![Karma Essen](https://rawgit.com/wetterfroschdus/karma-badges/master/essen.svg)


## How to use
- Clone the repository.
```
git clone https://github.com/wetterfroschdus/Jodel-Wetterfrosch.git
```
- Install the requirement: [jodel_api](https://github.com/nborrmann/jodel_api/)!
```
pip install jodel_api
```
#### [jodel_api](https://github.com/nborrmann/jodel_api/) by [nborrmann](https://github.com/nborrmann) is not updated with new HMAC keys from new Jodel versions anymore, so it won't work. There's still a way to get the keys, just google around a bit. 😉 

- Get an [API Key](https://www.wunderground.com/weather/api/d/pricing.html) from Weather Underground

- Use create_account.py to generate the necessary data:
```
python create_account.py
```
 Just follow the instructions 😉

## Run it!
Use jodel_wetterfrosch.py to create a weather Jodel:
```
python jodel_wetterfrosch.py -a account_file.json
```
If you place the account_file in a different folder as the script, you need to specify the full path to it:
```
python jodel_wetterfrosch.py -a /foo/bar/account_file.json
```








### Weather Data Provider
<a href="https://www.wunderground.com/" target="_blank"><img src="https://icons.wxug.com/logos/PNG/wundergroundLogo_4c_horz.png" 
alt="Weather Underground Logo" height="60" border="0" /></a>

### Pollen Data Provider
<a href="https://www.dwd.de"><img src="https://upload.wikimedia.org/wikipedia/de/thumb/7/7b/DWD-Logo_2013.svg/800px-DWD-Logo_2013.svg.png" 
alt="DWD Logo" height="70" border="0" /></a>
