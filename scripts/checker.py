import requests
import json
import time
import os
from datetime import date
from threading import Thread
from func.log import log
from func.functions import *
import threading

requests.packages.urllib3.disable_warnings()

class CHECK:
	def __init__(self, accname, email, password, username, proxy_list, webhook, prox):
		self.accname = accname
		self.webhook = webhook
		self.email = email.lower()
		self.passWord = password
		tt = fetch_db(self.email)
		self.accessTok = tt[0]
		self.refreshTok = tt[1]
		self.username = username
		self.proxy_list = proxy_list
		self.s = requests.session()
		self.UA = getUA()
		self.prox = prox

		if self.prox == "":

			if len(self.proxy_list) > 0:
				self.s.proxies = get_proxy(self.proxy_list)
		else:
			log("i", "proxy is there")
			self.s.proxies = get_proxy(self.prox)

		#print(self.accessTok)
		#print(self.refreshTok)
		#input("")


		while True:

			login = self.login()
			if login == False:
				break

			resp = self.check()
			if resp == False:
				break
			else:
				break

	def login(self):
		log("i", "Logging in")
		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}

		attempts = 0
		while attempts <= 5:
			try:
				response = self.s.get('https://api.niftygateway.com//user/profile/', headers=headers, verify=False)
				#print(response.content)
				if "Authentication credentials were not provided." in response.text:
					log('e', "Token expired, retreiving a new one")
					newtok = getTok(self.refreshTok, self.s, self.proxy_list, self.email)
					if newtok == False:
						return False
					else:
						self.accessTok = newtok[0]
						self.refreshTok = newtok[1]
						return True
					log("i", "Got new tokens, retrying")
				elif response.json()['didSucceed'] == True:
					log("s", "Successfully logged in")
					return True

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				self.UA = getUA()
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + "login")
				time.sleep(0.1)
				return False
			attempts = attempts + 1
			if attempts == 5:
				return False


	def check(self):

		log("i", f"Fetching account [{self.email}]")

		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'pragma': 'no-cache',
			'cache-control': 'no-cache',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}

		attempts = 0

		while attempts <= 10:
			try:
				response = self.s.get('https://api.niftygateway.com//user/profile/', headers=headers, verify=False)
				res = response.json()

				#print(res)
				self.User = res['userProfile']['profile_url']

				self.balance = res['userProfile']['account_balance_in_cents']
				if int(self.balance) > 0:
					writeLog(site='Nifty-CHECKER-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.username,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='POSITIVE Balance')

				params = (('profile_url', self.User),)
				#print(params)
				response = self.s.get('https://api.niftygateway.com//user/profile-and-offchain-nifties-by-url/', headers=headers, params=params, verify=False)
				#print(self.s.proxies)
				#print(response.content)
				#input("")
				resp = response.json()
				if not resp['userProfileAndNifties']['nifties']:
					log("w", "No nifties in the account")
					return False
				for i in resp['userProfileAndNifties']['nifties']:
					log("s", "Found Nifty")
					addy = i['contractAddress']
					name = i['project_name'] + " " + i['name']
					video_link = i['image_url']
					image = i['unmintedNiftyObjThatCreatedThis']['contractObj']['project_cover_photo_url']
					sendwebhookchecker(addy, name, video_link, image, self.email, self.passWord, self.User, self.webhook)
					writeLog(site='Nifty-CHECKER-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.username,addy2=name,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='Success')
				return True

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				self.UA = getUA()
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + "login")
				time.sleep(0.1)
				return False
			attempts = attempts + 1
			if attempts == 10:
				return False





def main(token):
	try:
		config = json.loads(open('config.json').read())
	except Exception:
		log('i', "Couldn't load config file.")
		stop_program()

	try:
		z = 1
		n = []
		arr = os.listdir('.')
		for i in arr:
			if "csv" in i:
				n.append(i)
				log("i", f"[{z}] " + i)
				z += 1
		fileS = int(input("Choose your csv (Number): "))
		#print(n[fileS - 1])
		#input("")
		rows = check_csv(n[fileS - 1], "Nifty")
	except Exception as e:
		log("e", "The csv file is not located")
		stop_program()
	try:
		proxies = read_from_txt("proxies.txt")
	except Exception:
		proxies = 0
		log('i', "Proxy file is empty, using local host.")

	delay = config['DELAY']
	webhook = config['webhook']
	threads = []

	for i in rows:
		accname = i[1]
		email = i[2]
		password = i[3]
		username = i[9]
		prox = i[21]

		t = Thread(target=CHECK, args=(accname, email, password, username, proxies, webhook, prox))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	stop_program()
