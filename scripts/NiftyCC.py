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

class ACCOUNT:
	def __init__(self, accname, email, password, username, name, addy1, addy2, city, zipcode, state, country, ccNumber, expMonth, expYear, cvc, webhook, apiKey, proxy_list, prox):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		self.webhook = webhook
		self.name = name
		self.username = username
		self.addy1 = addy1
		self.addy2 = addy2
		self.city = city
		self.zipcode = zipcode
		self.state = state
		self.country = country
		self.ccNumber = ccNumber
		self.expMonth = expMonth
		self.expYear = expYear
		self.cvc = cvc
		self.apiKey = apiKey
		self.proxy_list = proxy_list
		tt = fetch_db(self.email)
		self.accessTok = tt[0]
		self.refreshTok = tt[1]
		self.s = requests.session()
		self.UA = getUA()
		self.prox = prox

		if self.prox == "":

			if len(self.proxy_list) > 0:
				self.s.proxies = get_proxy(self.proxy_list)
		else:
			log("i", "proxy is there")
			self.s.proxies = get_proxy(self.prox)


		while True:

			resp = self.login()
			if resp == False:
				break

			resp2 = self.createToken()
			if resp2 == False:
				break
			resp3 = self.addCard()
			if resp3 == False:
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

	def createToken(self):
		headers = {
			'Host': 'api.stripe.com',
			'authorization': 'Bearer pk_live_cVGVZJgrtMqPELUnLDx16giP',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
			'content-type': 'application/x-www-form-urlencoded',
			'accept': '*/*',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'cross-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9',
		}

		params = (
			('card[number]', self.ccNumber),
			('card[exp_month]', self.expMonth),
			('card[exp_year]', self.expYear),
			('card[cvc]', self.cvc),
			('currency', 'usd'),
			('card[address_zip]', [self.zipcode, self.zipcode]),
			('card[address_city]', self.city),
			('card[address_country]', self.country),
			('card[address_line1]', self.addy1),
			('card[address_line2]', self.addy2),
			('card[address_state]', self.state),
			('card[name]', self.name),
		)
		attempts = 0
		while attempts <= 10:
			try:
				self.s.proxies = {
					"http": None,
					"https": None,
				}
				response = self.s.post('https://api.stripe.com/v1/tokens', headers=headers, params=params, verify=False)
				#print(response.content)
				try:
					resp = response.json()
					self.cardIDtok = resp['id']
					return True

				except Exception as e:
					if "incorrect_number" in response.text:
						log("e", "Error with card number please check csv")
						return False
					elif "invalid" in response.text:
						log("e", "Wrong year or month in csv check your file")
						return False

					log("e", "Could not get card ID token" + str(e))
					time.sleep(0.1)
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(0.1)
			except Exception as e:
				log('e', str(e) + "Adding Card")
				time.sleep(0.1)
				return False
			attempts = attempts + 1
			if attempts == 10:
				return False



	def addCard(self):
		if len(self.proxy_list) > 0:
			self.s.proxies = get_proxy(self.proxy_list)

		headers = {
			'Host': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
			'content-type': 'application/json;charset=UTF-8',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9',
		}

		data = {
			"card_token": self.cardIDtok
		}
		while True:
			try:
				response = self.s.post('https://api.niftygateway.com/stripe/add-card/', headers=headers, json=data, verify=False)
				#print(response.content)
				if "Card added" in response.text:
					log("s", "Card succesfully added")
					writeLog(site='Nifty-CC-Adder-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.ccNumber,addy2=self.expMonth,zip=self.expYear,state=self.cvc,country=None,city=None,phone=None,insta=None,size=None,link=None,status='SUCCESS')
					return True

				elif response.status_code == 500:
					log("e", "Back end error, error with card or cvv or name etc..")
					writeLog(site='Nifty-CC-Adder-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.ccNumber,addy2=self.expMonth,zip=self.expYear,state=self.cvc,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
					return False
				else:
					log("e", "Error creating card with status code [%s]" % response.status_code)
					writeLog(site='Nifty-CC-Adder-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.ccNumber,addy2=self.expMonth,zip=self.expYear,state=self.cvc,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
					return False


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + "Adding Card")
				time.sleep(0.1)
				return False
			#print(response.content)





def main(token):
	try:
		config = json.loads(open('config.json').read())
	except Exception:
		log('i', "Couldn't load config file.")
		stop_program()
	webhook = config['webhook']
	apiKey = config['API_KEY']
	delay = config['DELAY']

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

	threads = []

	for i in rows:
		accname = i[1]
		email = i[2]
		password = i[3]
		username = i[9]
		name = i[10]
		addy1 = i[11]
		addy2 = i[12]
		city = i[13]
		zipcode = i[14]
		state = i[15]
		country = i[16]
		ccNumber = i[17]
		expMonth = i[18]
		expYear = i[19]
		cvc = i[20]
		prox = i[21]

		t = Thread(target=ACCOUNT, args=(accname, email, password, username, name, addy1, addy2, city, zipcode, state, country, ccNumber, expMonth, expYear, cvc, webhook, apiKey, proxies, prox))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	stop_program()
