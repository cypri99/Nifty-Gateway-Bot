import os
from func.log import log
import random
from datetime import date
import platform
import time
import requests, json
from os.path import expanduser
import subprocess
import string
from pathlib import Path
#from capmonster_python import NoCaptchaTaskProxyless
import csv
import pandas as pd
import sqlite3
from sqlite3 import Error
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from python_anticaptcha import (AnticaptchaClient, AnticaptchaException, NoCaptchaTaskProxylessTask, RecaptchaV3TaskProxyless, ImageToTextTask)



if "Darwin" in platform.platform():
    home = os.getcwd() + '/'
    PATH_HOME = home


elif "Windows" in platform.platform():
    home = os.getcwd() + "\\"
    PATH_HOME = home

def stop_program():
    input("Press ENTER to exit")
    os._exit(0)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

def read_from_txt(path):
    '''
    (None) -> list of str
    Loads up all sites from the sitelist.txt file in the root directory.
    Returns the sites as a list
    '''
    # Initialize variables
    raw_lines = []
    lines = []

    # Load data from the txt file
    try:
        f = open(path, "r")
        raw_lines = f.readlines()
        f.close()

    # Raise an error if the file couldn't be found
    except Exception:
        log('e', "Couldn't locate <" + path + ">.")
        print("File not found")
        stop_program()

    if (len(raw_lines) == 0):
        log('e', "No data in <" + path + ">.")

    # Parse the data
    for line in raw_lines:
        lines.append(line.strip("\n"))

    # Return the data
    return lines

def is_int(string):
    try:
        _ = int(string)
        return True
    except ValueError:
        return False

def getUA():
	ua = [
		"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
		"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2015.1007 Safari/537.36",
		"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
		"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.0.1471.914 Safari/537.36",
		"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2015.1007 Safari/537.36",
		"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2909.1022 Safari/537.36",
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/50.0.2661.102 Chrome/50.0.2661.102 Safari/537.36"
	]
	user_agent = random.choice(ua)

	return user_agent


def get_proxy(proxy_list):
	'''
	(list) -> dict
	Given a proxy list <proxy_list>, a proxy is selected and returned.
	'''
	# Choose a random proxy

	if isinstance(proxy_list, list):
		proxy = random.choice(proxy_list)
	else:
		proxy = proxy_list

	m = proxy.strip().split(':')
	if len(m) == 4:
		base = f"{':'.join(m[:2])}"  # ip:port
		if len(m) == 4:
			proxies = {
				'http': f"http://{':'.join(m[-2:])}@{base}" + '/',
				'https': f"http://{':'.join(m[-2:])}@{base}" + '/'
			}
	else:
		# Set up the proxy to be used
		proxies = {
			"http": str(proxy),
			"https": str(proxy)
		}
	# Return the proxy
	return proxies

def check_csv(path, store):
    tasks_name = path#can load using path
    d = ',' #seperator ("delimiter")
    col_valid_1 = ['STORE','PROFILE','EMAIL','PASSWORD','ITEM_ADDRESS','NIFTY_TYPE','PAYMENT_MODE','RAFFLE','PACK', 'USERNAME','NAME','ADDRESS 1','ADDRESS 2','CITY','ZIPCODE','STATE','COUNTRY','CC_NUMBER','EXP_MONTH','EXP_YEAR','CVC','PROXY']
    col_validation = ['STORE','PROFILE','EMAIL','PASSWORD','ITEM_ADDRESS','NIFTY_TYPE','PAYMENT_MODE','RAFFLE','PACK', 'USERNAME','NAME','ADDRESS 1','ADDRESS 2','CITY','ZIPCODE','STATE','COUNTRY','CC_NUMBER','EXP_MONTH','EXP_YEAR','CVC','PROXY']
    col_list = []
    list_size = []
    try:
        log("i", 'Checking Rows in CSV... ')
        with open(tasks_name,'r') as ry:
            count = 0
            for line in ry:
                xyu = line.count(d)
                count += 1
                if int(xyu) > len(col_valid_1):
                    log('e', 'There is an invalid number of Items in Row: [{}]'.format(count))
                    stop_program()

        ry.close()

        df = pd.read_csv(tasks_name)
        #modifiedDF = df.dropna(subset=col_valid_1)
        #modifiedDF.to_csv(tasks_name,index=False)
        t_row=len(df.axes[0]) #parsing the total amount of rows
        t_col=len(df.axes[1])
        log("i", 'Total Columns : {} | Total Rows : {}'.format(t_col,t_row))
        if int(t_row) <= 0:
            raise Exception('Unfortunately there were no rows in file - please add some rows and retry!')


        log("s", 'Successful Check - Proceeding...')
        #sleep(10)
        try:
            store_name = store
            log("i", '[STORE] Store Loaded: {}'.format(store_name))
            with open(tasks_name,'r') as f:
                reader = csv.reader(f)
                col_no = next(reader)
                if int(len(col_no)) != len(col_validation):
                    raise log('e', '[COLUMNS] CSV has incorrect number of columns...!')
                for ix in range(len(col_no)):
                    col_list.append(col_no[ix])
                if col_validation == col_no:
                    log("i", '[COLUMNS] Columns are Correct - Proceeding with Checks...!')
                else:
                    raise log('e', '[COLUMN_NAMES] CSV has incorrect column names...!')
                for row in reader:
                    if str(row[0]) == str(store_name):
                        list_size.append(row)
                validation_thread = len(list_size)
                #print(validation_thread)
                if validation_thread <= 0:
                    raise log('e', '[ROWS] Invalid Number of Rows... - Please input at least 1 row!')
                rows_removed = reader.line_num-1-validation_thread
                log("i", '{} Tasks Removed due to different Site Name! - Proceeding...'.format(rows_removed))
            f.close()
            log("i", 'Tasks Loaded: {} -> Now entering!'.format(validation_thread))
            print("\n")
            return list_size
        except Exception as e:
            log("e", 'Error: {}'.format(e))

            stop_program()

    except Exception as e:
        log("e", 'Error: {}'.format(e))

        stop_program()

def sendwebhookchecker(addy, name, video_link, image, email, passWord, username, webhook):
	data = {
		"embeds": [{
			"title": name,
			"url": (video_link),
			"color": 2225746,
			"footer": {
				"text": ("HardHatAIO " + ""),
				"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
			},
			"thumbnail": {
				"url": (image)
			},
			"author": {
				"name": "Nifty Checker",
				"url": (video_link)
			},
			"fields": [{
				"name": "Email",
				"value": email,
				"inline": True
			},{
				"name": "Username",
				"value": username,
				"inline": True
			},{
				"name": "Item",
				"value": addy,
				"inline": True
			},{
				"name": "Password",
				"value": (passWord),
				"inline": True
			}]
		}]
	}

	headers = {'Content-Type': 'application/json'}
	r = requests.post(webhook, json=data, headers=headers, verify=False)
	if r.status_code in (201, 301, 204, 302):
		log("i", "Webhook sent")
	else:
		log("e", f"Could not send Webhook error: {r.status_code}" )


def sendwebhookdecline(name, url, photo, price, delta, addy, accname, webhook, email, passWord):
	data = {
		"embeds": [{
			"title": name,
			"url": (url),
			"color": 16130395,
			"footer": {
				"text": ("HardHatAIO " + ""),
				"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
			},
			"thumbnail": {
				"url": (photo)
			},
			"author": {
				"name": "Nifty FAILED CHECKOUT",
				"url": (url)
			},
			"fields": [{
				"name": "Price",
				"value": price,
				"inline": True
			},{
				"name": "Checkout time",
				"value": "%.2fs" % delta,
				"inline": True
			},{
				"name": "Item",
				"value": addy,
				"inline": True
			},{
				"name": "Profile",
				"value": ("||" + accname + "||"),
				"inline": True
			}]
		}]
	}
	data2 = {
		"embeds": [{
			"title": name,
			"url": (url),
			"color": 16130395,
			"footer": {
				"text": ("HardHatAIO " + ""),
				"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
			},
			"thumbnail": {
				"url": (photo)
			},
			"author": {
				"name": "Nifty FAILED CHECKOUT",
				"url": (url)
			},
			"fields": [{
				"name": "Price",
				"value": price,
				"inline": True
			},{
				"name": "Checkout time",
				"value": "%.2fs" % delta,
				"inline": True
			},{
				"name": "Item",
				"value": addy,
				"inline": True
			},]
		}]
	}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(webhook, json=data, headers=headers, verify=False)
	if r.status_code in (201, 301, 204, 302):
		log("i", "Webhook sent")
	else:
		log("e", f"Could not send Webhook error: {r.status_code}" )


def sendwebhooksuccess(name, url, photo, price, delta, addy, accname, webhook, email, passWord):
	data = {
		"embeds": [{
			"title": name,
			"url": (url),
			"color": 2225746,
			"footer": {
				"text": ("HardHatAIO " + ""),
				"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
			},
			"thumbnail": {
				"url": (photo)
			},
			"author": {
				"name": "Nifty Successful CHECKOUT",
				"url": (url)
			},
			"fields": [{
				"name": "Price",
				"value": price,
				"inline": True
			},{
				"name": "Checkout time",
				"value": "%.2fs" % delta,
				"inline": True
			},{
				"name": "Item",
				"value": addy,
				"inline": True
			},{
				"name": "Profile",
				"value": ("||" + accname + "||"),
				"inline": True
			}]
		}]
	}
	data3 = {
			"embeds": [{
				"title": name,
				"url": (url),
				"color": 2225746,
				"footer": {
					"text": ("HardHatAIO " + ""),
					"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
				},
				"thumbnail": {
					"url": (photo)
				},
				"author": {
					"name": "Nifty Successful CHECKOUT",
					"url": (url)
				},
				"fields": [{
					"name": "Price",
					"value": price,
					"inline": True
				},{
					"name": "Checkout time",
					"value": "%.2fs" % delta,
					"inline": True
				},{
					"name": "Item",
					"value": addy,
					"inline": True
				},{
					"name": "Profile",
					"value": ("||" + accname + "||"),
					"inline": True
				},
				{
					"name": "email",
					"value": (email),
					"inline": True
				},
				{
					"name": "pass",
					"value": (passWord),
					"inline": True
				}]
			}]
	}

	data2 = {
		"embeds": [{
			"title": name,
			"url": (url),
			"color": 2225746,
			"footer": {
				"text": ("HardHatAIO " + ""),
				"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
			},
			"thumbnail": {
				"url": (photo)
			},
			"author": {
				"name": "Nifty Successful CHECKOUT",
				"url": (url)
			},
			"fields": [{
				"name": "Price",
				"value": price,
				"inline": True
			},{
				"name": "Checkout time",
				"value": "%.2fs" % delta,
				"inline": True
			},{
				"name": "Item",
				"value": addy,
				"inline": True
			}]
		}]
	}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(webhook, json=data, headers=headers, verify=False)
	if r.status_code in (201, 204, 301, 302):
		log("i", "Webhook sent")
	else:
		log("e", f"Could not send Webhook error: {r.status_code}" )

def sendwebhooksuccessRAF(name, url, photo, price, delta, addy, accname, webhook, email, passWord):
	data = {
			"embeds": [{
				"title": name,
				"url": (url),
				"color": 2225746,
				"footer": {
					"text": ("HardHatAIO " + ""),
					"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
				},
				"thumbnail": {
					"url": (photo)
				},
				"author": {
					"name": "Nifty Successful ENTRY RAFFLE",
					"url": (url)
				},
				"fields": [{
					"name": "Price",
					"value": price,
					"inline": True
				},{
					"name": "Checkout time",
					"value": "%.2fs" % delta,
					"inline": True
				},{
					"name": "Item",
					"value": addy,
					"inline": True
				},{
					"name": "Profile",
					"value": ("||" + accname + "||"),
					"inline": True
				}]
			}]
	}

	data3 = {
			"embeds": [{
				"title": name,
				"url": (url),
				"color": 2225746,
				"footer": {
					"text": ("HardHatAIO " + ""),
					"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
				},
				"thumbnail": {
					"url": (photo)
				},
				"author": {
					"name": "Nifty Successful ENTRY RAFFLE",
					"url": (url)
				},
				"fields": [{
					"name": "Price",
					"value": price,
					"inline": True
				},{
					"name": "Checkout time",
					"value": "%.2fs" % delta,
					"inline": True
				},{
					"name": "Item",
					"value": addy,
					"inline": True
				},{
					"name": "Profile",
					"value": ("||" + accname + "||"),
					"inline": True
				},
				{
					"name": "email",
					"value": (email),
					"inline": True
				},
				{
					"name": "pass",
					"value": (passWord),
					"inline": True
				}]
			}]
	}

	data2 = {
		"embeds": [{
			"title": name,
			"url": (url),
			"color": 2225746,
			"footer": {
				"text": ("HardHatAIO " + ""),
				"icon_url": "https://pbs.twimg.com/profile_images/1485640035609284613/d9XJSeR8_400x400.jpg"
			},
			"thumbnail": {
				"url": (photo)
			},
			"author": {
				"name": "Nifty Successful ENTRY RAFFLE",
				"url": (url)
			},
			"fields": [{
				"name": "Price",
				"value": price,
				"inline": True
			},{
				"name": "Checkout time",
				"value": "%.2fs" % delta,
				"inline": True
			},{
				"name": "Item",
				"value": addy,
				"inline": True
			}]
		}]
	}
	headers = {'Content-Type': 'application/json'}
	r = requests.post(webhook, json=data, headers=headers, verify=False)
	if r.status_code in (201, 204, 301, 302):
		log("i", "Webhook sent")
	else:
		log("e", f"Could not send Webhook error: {r.status_code}" )


def is_json(obj):
	try:
		json_object = json.loads(obj)
	except ValueError:
		return False
	return True


class smsPvaAPI():
	def __init__(self,API_KEY):
		self.API_ENDPOINT = "http://smspva.com/priemnik.php"
		self.API_KEY = API_KEY

	def check_response(self, resp) -> dict:
		if resp.status_code != 200 or not is_json(resp.text):
			raise Error(f"There was some problem making the request more info:\nStatus Code: {resp.status_code}\nText: {resp.text}")
		return resp.json()

	def get_balance(self, service: str = None) -> dict:
		params = dict(metod="get_balance",service=service,apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_userinfo(self, service: str = None, _id: int = None, operator: str = None) -> dict:
		params = dict(metod="get_userinfo",service=service,apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_count(self, service: str , country: str = None) -> dict:
		params = dict(metod="get_count_new",service=service,apikey=self.API_KEY,country=country)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_number(self, country: str, service: str = None) -> dict:
		params = dict(metod="get_number",country=country,service=service,apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_ban(self, service: str, _id: int) -> dict:
		params = dict(metod="ban", service=service, apikey=self.API_KEY, id=_id)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_sms(self, country: str, service: str, _id: int , sms: str = None) -> dict:
		params = dict(metod="get_sms", country=country, service=service, id=_id, apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_denial(self, country: str, service: str, _id: int) -> dict:
		params = dict(metod="denial", country=country, service=service, id=_id, apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_proverka(self, service: str, number: str) -> dict:
		params = dict(metod="get_proverka", service=service, number=number, apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_sim(self, service: str, _id: int) -> dict:
		params = dict(metod="balance_sim", service=service, id=_id, apikey=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)
	def get_sms_message(self, country: str, service: str, _id: str) -> dict:
		getCurrentTime = lambda: int(round(time.time() * 1000))
		addTenToCurrent = getCurrentTime() + 600000
		while addTenToCurrent >= getCurrentTime():
			request = self.get_sms(country ,service ,_id)
			print(request)
			if request["text"] != None:
				return request
				break
			time.sleep(20)

class fiveSIm():
	def __init__(self,API_KEY):
		self.API_ENDPOINT = "http://api2.5sim.net/stubs/handler_api.php"
		self.API_KEY = API_KEY

	def check_response(self, resp) -> dict:
		if resp.status_code != 200:
			raise Exception(f"There was some problem making the request more info:\nStatus Code: {resp.status_code}\nText: {resp.text}")
		if "NO_NUMBER" in resp.text:
			raise Exception(f"There was some problem making the request more info:\nStatus Code: {resp.status_code}\nText: {resp.text}")

		return resp.text

	def get_balance(self, service: str = None) -> dict:###
		params = dict(action="getBalance",api_key=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def set_status(self, _id: int ) -> dict:###
		params = dict(action="setStatus", id=_id, api_key=self.API_KEY, status=1)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_number(self, country: str) -> dict:###
		params = dict(action="getNumber",country=country,service="or",api_key=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_sms(self, _id: int ) -> dict:###
		params = dict(action="getStatus", id=_id, api_key=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)


	def get_sms_message(self, _id: str) -> dict:
		getCurrentTime = lambda: int(round(time.time() * 1000))
		addTenToCurrent = getCurrentTime() + 600000
		while addTenToCurrent >= getCurrentTime():
			request = self.get_sms(_id)
			#print(request)
			if "STATUS_OK" in request:
				return request
				break
			time.sleep(20)

def writeLog(**kwargs):
	with open('./log/{}.csv'.format(kwargs.get('site')),'a',newline='') as output:
		writer = csv.writer(output)

		writer.writerow(
			[
				kwargs.get('status'),
				kwargs.get('link'),
				kwargs.get('first'),
				kwargs.get('last'),
				kwargs.get('email'),
				kwargs.get('insta'),
				kwargs.get('size'),
				kwargs.get('phone'),
				kwargs.get('addy1'),
				kwargs.get('addy2'),
				kwargs.get('zip'),
				kwargs.get('state'),
				kwargs.get('city'),
				kwargs.get('country'),
				kwargs.get('store')
			]
		)

class smsActi():
	def __init__(self,API_KEY):
		self.API_ENDPOINT = "https://sms-activate.ru/stubs/handler_api.php"
		self.API_KEY = API_KEY

	def check_response(self, resp) -> dict:
		if resp.status_code != 200:
			log("w", f"There was some problem making the request more info:\nStatus Code: {resp.status_code}\nText: {resp.text}")
		if "NO_NUMBER" in resp.text:
			log("w",f"There was some problem making the request more info:\nStatus Code: {resp.status_code}\nText: {resp.text}")

		return resp.text

	def get_balance(self, service: str = None) -> dict:###
		params = dict(action="getBalance",api_key=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def set_status(self, _id: int ) -> dict:###
		params = dict(action="setStatus", id=_id, api_key=self.API_KEY, status=1)
		r = requests.get(self.API_ENDPOINT,params=params)
		print(r.text)
		return self.check_response(r)

	def get_number(self, country: str) -> dict:###
		params = dict(action="getNumber",country=country,service="ot",api_key=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)

	def get_sms(self, _id: int ) -> dict:###
		params = dict(action="getStatus", id=_id, api_key=self.API_KEY)
		r = requests.get(self.API_ENDPOINT,params=params)
		return self.check_response(r)


	def get_sms_message(self, _id: str) -> dict:
		getCurrentTime = lambda: int(round(time.time() * 1000))
		addTenToCurrent = getCurrentTime() + 600000
		while addTenToCurrent >= getCurrentTime():
			request = self.get_sms(_id)
			print(request)
			if "STATUS_OK" in request:
				return request
				break
			time.sleep(20)

def GetUUID_win():
        cmd = 'wmic csproduct get uuid'
        uuid = str(subprocess.check_output(cmd))
        pos1 = uuid.find("\\n")+2
        uuid = uuid[pos1:-15]
        return uuid

def GetUUID_mac():
	uuid = str(subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep -E '(UUID)'", shell=True)).split('"')[-2]
	return uuid

def activate():
	config = json.loads(open('config.json').read())
	key = config["KEY"]
	if key == "":
		print("[INFO] You are missing the key in you config file.")
		stop_program()
	API_key = 'TEST-TTRTRT-KEY' #our api key
	print('[INFO] Checking Key...')
	headers = {
		'apiKey':API_key,
		'Content-Type': 'application/json'}

	#print(platform.platform())

	if "mac" in platform.platform():
		hardware_uuid = GetUUID_mac()
	else:
		hardware_uuid = GetUUID_win()

	#print(hardware_uuid)
	nkey = key.replace("-","") + "@gmail.com"
	try:
		checkKey = requests.post('API_AUTH',headers=headers,json={"key":key}, verify=False)
		if checkKey.status_code == 200:
			resp = checkKey.json()
			#print(resp)
			#print(resp['machineId'])
			if resp['machineId'] == hardware_uuid:
				print('[INFO] Key authorised')
				token = createToken(nkey)
				return token

			elif resp['machineId'] == None:
				requests.post('API_AUTH',headers=headers,json={"key":key,"machine":hardware_uuid}, verify=False)
				print('[INFO] Key authorised')
				token = createToken(nkey)
				return token
			else:
				print('[INFO] Machine could not be validated, please reset it in Dash')
				stop_program()
		else:
			print('[INFO] Key does not exist or is not bound.')
			stop_program()
	except (requests.exceptions.ConnectionError, requests.exceptions.SSLError):
		log("e", "Cannot connect to the internet.")
		stop_program()

def createToken(nkey):
	import requests

	headers = {
		'accept': 'application/json',
		'Content-Type': 'application/json',
	}

	data = {
		"email": nkey,
		"password": "PASS",
		"is_active": True,
		"is_superuser": False,
		"is_verified": False
	}

	try:
		response = requests.post('ENTRIES_API', headers=headers, json=data)
		#print(response.content)

		if "id" in response.text:
			print("[INFO] Doing checks ...")
			#continue

		elif "REGISTER_USER_ALREADY_EXISTS" in response.text:
			print("[INFO] Doing checks ...")
			#continue

		else:
			log("e", "Error fetching user")

	except Exception as e:
		print(str(e))
		stop_program()

	try:
		headers = {
			'accept': 'application/json',
			'Content-Type': 'application/x-www-form-urlencoded',
		}
		data = {'grant_type': '','username': nkey,'password': 'PASS','scope': '','client_id': '','client_secret': ''}

		response = requests.post('API', headers=headers, data=data)
		resp = response.json()
		if resp['access_token']:
			token = resp['access_token']
			return token

		else:
			log("e", "Couldn't get login token")
			stop_program()

	except Exception as e:
		print(str(e))
		stop_program()




def create_db(db_file):
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		log("i", "Connection with database was initalized")
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()

def create_table(db_file, email, access_token, refresh_token):
	# Create database
	conn = sqlite3.connect(db_file)
	c = conn.cursor()
	c.execute("""CREATE TABLE IF NOT EXISTS emails_db (email TEXT UNIQUE, access_token TEXT, refresh_token TEXT)""")
	try:
		c.execute("""INSERT INTO emails_db (email, access_token, refresh_token) VALUES (?, ?, ?)""", (email, access_token, refresh_token))
		log('i', "Inserting in email and tokens in db <" + email + ">.")
	except:
		# Email already exists, updatinng tokens
		try:

			c.execute("""UPDATE emails_db SET access_token = ? WHERE email= ?""", (access_token, email))
			c.execute("""UPDATE emails_db SET refresh_token = ? WHERE email= ?""", (refresh_token, email))
			log("i", "Updated tokens in db")

		except (sqlite3.Error, Exception) as e:
			log('e', f"Database reading error: {e} [{email}]")

	# Close database
	conn.commit()
	c.close()
	conn.close()

def fetch_db(email):
	conn = sqlite3.connect('./db/email_db')
	c = conn.cursor()
	try:
		access_token = (c.execute('SELECT access_token FROM emails_db WHERE email=?', (email,)).fetchone())[0]
		refresh_token = (c.execute('SELECT refresh_token FROM emails_db WHERE email=?', (email,)).fetchone())[0]
		#print(access_token)
		#print(refresh_token)
	except (sqlite3.Error, Exception) as e:
		log('e', f"Database reading error: {e} [{email}]")

	conn.commit()
	c.close()
	conn.close()

	return access_token, refresh_token

def update_db(access_token, refresh_token, email):
	conn = sqlite3.connect('./db/email_db')
	c = conn.cursor()
	try:
		c.execute("""UPDATE emails_db SET access_token = ? WHERE email= ?""", (access_token, email))
		c.execute("""UPDATE emails_db SET refresh_token = ? WHERE email= ?""", (refresh_token, email))
		#print(access_token)
		#print(refresh_token)
	except (sqlite3.Error, Exception) as e:
		log('e', f"Database reading error: {e} [{email}]")

	conn.commit()
	c.close()
	conn.close()

	return access_token, refresh_token


def getTok(refreshTok, s, proxy_list, email):
		log("i", "Getting new Tokens")
		attempts = 0
		while attempts <= 5:
			try:
				headers = {
					'Host': 'api.niftygateway.com',
					'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
					'accept': 'application/json, text/plain, */*',
					'sec-ch-ua-mobile': '?0',
					'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
					'content-type': 'application/x-www-form-urlencoded',
					'origin': 'https://niftygateway.com',
					'sec-fetch-site': 'same-site',
					'sec-fetch-mode': 'cors',
					'sec-fetch-dest': 'empty',
					'accept-language': 'en-US,en;q=0.9',
				}

				data = f'grant_type=refresh_token&client_id=PsXGrgaKodNkEhtSYFOL8klAD2M3TlO4VgNNFuug&refresh_token={refreshTok}'

				response = s.post('https://api.niftygateway.com/o/token/', headers=headers, data=data)
				#print(response.content)
				#input("")
				resp = response.json()
				if "invalid_grant" in response.text:
					log("e", "Could not get token, account soft banned or token expired re-do login")
					writeLog(site='Nifty-Error-Token-{}'.format(date.today()),first=email,last=None,email=None,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
					return False
				elif resp['token_type'] == "Bearer":
					accessTok = resp['access_token']
					refreshTok = resp['refresh_token']
					update_db(accessTok, refreshTok, email)
					return accessTok, refreshTok
				else:
					log("e", "Couldn't get new tokens... requeest 2fa againf for this account")
					writeLog(site='Nifty-Error-Token-{}'.format(date.today()),first=email,last=None,email=None,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
					return False
			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(proxy_list) > 0:
					s.proxies = get_proxy(proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + " Getting token")
				time.sleep(0.1)
				return False
			attempts = attempts + 1
			if attempts == 5:
				return False

def random_char(y):
	return ''.join(random.choice(string.ascii_letters) for x in range(y))

def solvecaptcha_2cap(host, key_2captcha, site_key, session):
	log('i', "Solving captcha with 2Captcha")
	urlcap = "http://2captcha.com/in.php?key=" + key_2captcha + "&method=userrecaptcha&googlekey=" + site_key + "&pageurl=" + host
	resp = session.get(urlcap, verify=False)

	if resp.text[0:2] != 'OK':
		log('e', resp.text)
		print('Service error. Error code:' + resp.text)
		#input('Press ENTER to exit')
		return

	captcha_id = resp.text[3:]
	fetch_url = "http://2captcha.com/res.php?key=" + key_2captcha + "&action=get&id=" + captcha_id
	resp = requests.get(fetch_url, verify=False)
	cap_2 = False
	while 'CAPCHA_NOT_READY' in resp.text and cap_2 == False:
		time.sleep(3)
		fetch_url = "http://2captcha.com/res.php?key=" + key_2captcha + "&action=get&id=" + captcha_id
		resp = requests.get(fetch_url, verify=False)
		if resp.text[0:2] == 'OK':
			break

	response = resp.text[3:]
	return response

def solveV3captcha(url, api_key, site_key, session ):
    try:
        captchaURL = 'https://2captcha.com/in.php?key={}&method=userrecaptcha&version=v3&action=verify&min_score=0.3&googlekey={}&pageurl={}&json=1'.format(api_key,site_key,url)
        first = session.get(captchaURL)
        time.sleep(4)
        url = 'https://2captcha.com/res.php?key={}&action=get&taskinfo=1&id={}&json=1'.format(api_key,first.json()["request"])
        r = requests.get(url)
        while r.json()["request"] == "CAPCHA_NOT_READY":
            r = requests.get(url)
            time.sleep(1)
        return r.json()["request"]
    except Exception as e:
        print(e)

def solvecaptcha(url, site_key, api_key):
	log('i', "Solving captcha with Anticaptcha")
	try:
		client = AnticaptchaClient(api_key)
		task = NoCaptchaTaskProxylessTask(website_url=url, website_key=site_key)
		job = client.createTask(task)
		job.join()
		return job.get_solution_response()
	except AnticaptchaException as e:
		if e.error_code == 'ERROR_ZERO_BALANCE':
			print(e.error_id, e.error_code, e.error_description)
		else:
			raise

def capmonstersolver(url, site_key, api_key):
	log("i", "Solving with Capmonster")
	#print(api_key)
	try:
		capmonster = NoCaptchaTaskProxyless(client_key=api_key)
		taskId = capmonster.createTask(website_key=site_key, website_url=url)
		response = capmonster.joinTaskResult(taskId=taskId)
		#print(response)
		return response
	except Exception as e:
		log("e", str(e))
