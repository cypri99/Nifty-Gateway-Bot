import requests
import json
import time
import os
from datetime import date
from threading import Thread
from func.log import log
import sys
from func.functions import *
import threading

requests.packages.urllib3.disable_warnings()

maxthreads = 250
sema = threading.Semaphore(value=maxthreads)
threads = list()

class CHECKOUT:
	sema.acquire()
	def __init__(self, accname, email, password, addy, niftyType, paymode, raffle, pack, webhook, proxy_list, token, prox):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		self.token = token
		self.addy = addy
		self.paymode = paymode
		self.webhook = webhook
		self.raffle = raffle
		self.pack = pack
		self.niftyType = niftyType
		self.proxy_list = proxy_list
		tt = fetch_db(self.email)
		self.link = f"https://niftygateway.com/enterdrawing/?contractAddress={self.addy}&niftyType={self.niftyType}"
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
			loginResp = self.login()
			if loginResp == False:
				break

			userResp = self.userInfo()
			if userResp == False:
				break

			respaAtc = self.atc()
			if respaAtc == False:
				break

			if self.raffle == "yes":
				resp2 = self.checkoutRaffle()
				if resp2 == True:
					sendwebhooksuccessRAF(self.name, self.url, self.photo, self.price, self.delta, self.addy, self.accname, self.webhook, self.email, self.passWord)
					break
				else:
					break

			else:
				res = self.checkoutFCFS()
				if res == True:
					sendwebhooksuccess(self.name, self.url, self.photo, self.price, self.delta, self.addy, self.accname, self.webhook, self.email, self.passWord)
					break
				else:
					break

		sema.release()



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
				#print(self.accessTok)
				#print(self.refreshTok)
				#input("")
				#nn = True
				#if nn == True:
				if "Authentication credentials were not provided." in response.text:
					log('e', "Token expired, retreiving a new one")
					newtok = getTok(self.refreshTok, self.s, self.proxy_list, self.email)
					#print(newtok)
					#input("")
					if newtok == False:
						return False
					else:
						self.accessTok = newtok[0]
						self.refreshTok = newtok[1]
						log("i", "Got new tokens, retrying")
						return True

				elif response.json()['didSucceed'] == True:
					log("s", "Successfully logged in")
					self.username = response.json()['userProfile']['profile_url']
					#print(self.username)
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

	def userInfo(self):

		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': self.UA,
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}
		attempts = 0
		while attempts <= 10:
			try:
				response = self.s.get('https://api.niftygateway.com//user/profile/', headers=headers, verify=False)
				self.username = response.json()['userProfile']['profile_url']
				#print(self.username)
				#print(self.s.proxies)
				profile = self.s.get('https://api.niftygateway.com/stripe/list-cards/', headers=headers, verify=False)
				#print(profile.content)
				#input("")
				try:
					resp = profile.json()
					self.card = resp['data'][-1]['id']
					self.fingerprint = resp['data'][0]['fingerprint']
					#print(self.card)
					#input("")
					return True
				except Exception as e:
					log("e", "Can't load user Info response ['")
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
					getUA()
					time.sleep(1)

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)

			except Exception as e:
				log('e', str(e) + " Error at getting user info")
				return False
			attempts = attempts + 1
			if attempts == 10:
				return False

			#print(profile.content)

	def atc(self):

		self.start = time.time()
		headers = {
			'Host': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'en-US,en;q=0.9',
		}

		data = {
			"contractAddress": self.addy,
			"niftyType": self.niftyType
		}
		params = (
			('contract_address', self.addy),
		)
		while True:
			try:
				data = self.s.get('https://api.niftygateway.com/function%20URL()%20%7B%20[native%20code]%20%7Dbuilder/get-storefront/', headers=headers, params=params, verify=False)
				#print(data.content)
				#input("")
				try:
					var = data.json()
					for i in var['nifties']:
						if int(self.niftyType) == i['niftyType']:
							self.name = i['niftyTitle']
							self.photo = i['contractObj']['project_icon']
							self.addy = i['niftyContractAddress']
							self.price = str(i['niftyPriceInCents'])

							log("i", "Selecting item "  + self.name)
							return True
				except Exception as e:
					log("e", "Can't read atc response")
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
					time.sleep(1)

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(0.1)
			except Exception as e:
				log('e', str(e) + "atc")
				return False

	def checkoutRaffle(self):
		#print(self.link)

		if json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower() == 'anticaptcha':
			#log('i', Fore.CYAN + "Solving captcha with Anticaptcha")
			gresponse = solvecaptcha(api_key=json.loads(open('config.json').read())['CAPTCHA_KEY'] ,
									site_key='6LeMnHgaAAAAAGKJeoPpHDYHdomeGkU5_RG1y0n_',
									url=self.link)
		elif json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower()  == '2captcha':
			#log('i', Fore.CYAN + get_time() + "Solving captcha with 2captcha")
			gresponse = solvecaptcha_2cap(self.link, json.loads(open('config.json').read())['CAPTCHA_KEY'],
									'6LeMnHgaAAAAAGKJeoPpHDYHdomeGkU5_RG1y0n_', self.s)
		elif json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower() == 'capmonster':
			gresponse = capmonstersolver(api_key=json.loads(open('config.json').read())['CAPTCHA_KEY'] ,
									site_key='6LeMnHgaAAAAAGKJeoPpHDYHdomeGkU5_RG1y0n_',
									url=self.link)
		else:
			log('e', "You are missing the provider, please check your info in config")
			stop_program()
		#print(gresponse)
		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': self.UA,
			'content-type': 'application/json;charset=UTF-8',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}

		headers2 = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
			'content-type': 'application/json;charset=UTF-8',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}

		#print(self.pack)

		if self.pack == "no":
			#print("hello")

			#**drawing
			data22 = {
				"contractAddress":self.addy,
				"niftyType":int(self.niftyType),
				"paymentType":"card",
				"fingerprint": "gv00AcDKYg6cnqCy",
				"cc_token":self.card
			}
			data2 = {
				"contractAddress":self.addy,
				"paymentType":"card",
				"cc_token":self.card,
				"niftyType":int(self.niftyType),
				"fingerprint":self.fingerprint,
				"captcha_token": gresponse,
				"beeple_answers": ""
			}

			#data22 = '{"contractAddress":"0xbc8adb88debc9d6c48e96faca0a44185414803f1","paymentType":"card","cc_token":"card_1IQxPnJcHyb9zWah94i5Nc8K","fingerprint":"gv00AcDKYg6cnqCy"}'
			#print(data2)

			data3 = {
				"contractAddress":self.addy,
				"niftyType":self.niftyType,
				"beeple_answers": "jmkDJWwMnyH3XB+4uSF+uQ==",
				"paymentType":"balance",
			}
			#print(data3)
		else:
			#print("hello")

			#**drawing
			data2 = {
				"contractAddress":self.addy,
				"packType":self.niftyType,
				"paymentType":"card",
				"cc_token":self.card,
				"fingerprint":self.fingerprint
			}

			data3 = {
				"contractAddress":self.addy,
				"packType":self.niftyType,
				"paymentType":"balance",
				"fingerprint":self.fingerprint
			}
			#print(data2)
		#tt = True
		while True:
			try:
				if self.paymode == "cc":
					response = self.s.post('https://api.niftygateway.com/drawing/enter/', headers=headers, json=data2, verify=False)
			#response = s.post('https://api.niftygateway.com/user/purchase-centralized-listing/', headers=headers, data=data, verify=False)

				if self.paymode == "balance":
					response = self.s.post('https://api.niftygateway.com/drawing/enter/', headers=headers2, data=data3, verify=False)
			#response = s.post('https://api.niftygateway.com/user/purchase-centralized-listing/', headers=headers, data=data, verify=False)

				self.end = time.time()
				self.delta = self.end - self.start
				#print(response.content)

				self.url = f"https://niftygateway.com/itemdetail/primary/{self.addy}/{self.niftyType}"
				#print(response.content)
				if response.status_code == 406:
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
					time.sleep(0.1)
					pass

				try:
					check = response.json()
				except Exception as e:
					log("e", "Could not read respoonse from checkout " + str(e))
					time.sleep(1)

				print(response.content)
				try:
					if "no longer available" in response.text:
						log("i", "Item not available yet, retrying")
						time.sleep(0.1)

					elif "Invalid reCaptcha token" in response.text:
						log("w", "invalid captcha")
						return False

					elif "drawing has ended" in response.text:
						log("w", "The drawing has ended or item is not live yet")
						#writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
						#return False
						time.sleep(0.1)

					elif check['didSucceed'] == True:
						log("s", "Succesfully Entered the raffle")
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='SUCCESS')

						return True


					elif "maximum amount of entries" in response.text:
						log("i", "Already entered")
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
						return False

					elif "has not been validated" in response.text:
						log("e", "Account was not valited")
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
						return False

				except Exception as e:
					#message = check['message']
					log("e", "Decline reason: " + str(e))
					sendwebhookdecline(self.name, self.url, self.photo, self.price, self.delta, self.addy, self.accname, self.webhook, self.email, self.passWord)
					time.sleep(0.1)
					writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
					return False


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(0.1)
			except Exception as e:
				log('e', str(e) + " checkout")
				writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
				return False



	def checkoutFCFS(self):

		#print(json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower())

		if json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower() == 'anticaptcha':
			#log('i', Fore.CYAN + "Solving captcha with Anticaptcha")
			gresponse = solvecaptcha(api_key=json.loads(open('config.json').read())['CAPTCHA_KEY'] ,
									site_key='6LeMnHgaAAAAAGKJeoPpHDYHdomeGkU5_RG1y0n_',
									url=self.link)
		elif json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower()  == '2captcha':
			#log('i', Fore.CYAN + get_time() + "Solving captcha with 2captcha")
			gresponse = solvecaptcha_2cap(self.link, json.loads(open('config.json').read())['CAPTCHA_KEY'],
									'6LeMnHgaAAAAAGKJeoPpHDYHdomeGkU5_RG1y0n_', self.s)
		elif json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower() == 'capmonster':
			gresponse = capmonstersolver(api_key=json.loads(open('config.json').read())['CAPTCHA_KEY'] ,
									site_key='6LeMnHgaAAAAAGKJeoPpHDYHdomeGkU5_RG1y0n_',
									url=self.link)
		else:
			log('e', "You are missing the provider, please check your info in config")
			stop_program()

		headers = {
			'Host': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
			'content-type': 'application/x-www-form-urlencoded',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'en-US,en;q=0.9',
			"cache-control": "no-cache",
			"pragma": "no-cache"
		}



		if self.pack == "no":

			#####CC cheeckout######
			data = {
				'amount_in_cents':self.price,
				'contractAddress': self.addy,
				'payment_type':'card',
				'payment_type':'card',
				'card_id': self.card,
				'cc_token': self.card,
				'tx_data_type': 'builder_purchase_generate',
				"niftyType":self.niftyType,
				"captcha_token": gresponse,
				"fingerprint":self.fingerprint
			}
			#######Balance############
			data1 = {
				'amount_in_cents':self.price,
				'contractAddress': self.addy,
				'payment_type':'balance',
				'payment_type':'balance',
				'tx_data_type': 'builder_purchase_generate',
				"niftyType":self.niftyType,
				"captcha_token": gresponse,
				"fingerprint":self.fingerprint
			}
			data2 = {
				'amount_in_cents':self.price,
				'contractAddress': self.addy,
				'payment_type':'prepaid_eth',
				'payment_type':'prepaid_eth',
				'tx_data_type': 'builder_purchase_generate',
				"niftyType":self.niftyType,
				"captcha_token": gresponse,
				"fingerprint":self.fingerprint
			}

		else:
			data = {
				'amount_in_cents':self.price,
				'contractAddress': self.addy,
				'payment_type':'card',
				'payment_type':'card',
				'card_id': self.card,
				'cc_token': self.card,
				'tx_data_type': 'builder_purchase_generate',
				"packType":self.niftyType,
				"captcha_token": gresponse,
				"fingerprint":self.fingerprint
			}
			#######Balance############
			data1 = {
				'amount_in_cents':self.price,
				'contractAddress': self.addy,
				'payment_type':'balance',
				'payment_type':'balance',
				'tx_data_type': 'builder_purchase_generate',
				"packType":self.niftyType,
				"captcha_token": gresponse,
				"fingerprint":self.fingerprint
			}
			data2 = {
				'amount_in_cents':self.price,
				'contractAddress': self.addy,
				'payment_type':'prepaid_eth',
				'payment_type':'prepaid_eth',
				'tx_data_type': 'builder_purchase_generate',
				"packType":self.niftyType,
				"captcha_token": gresponse,
				"fingerprint":self.fingerprint
			}

		while True:
			try:
				if self.paymode.lower() == "cc":
					response = self.s.post('https://api.niftygateway.com/user/purchase-unminted-nifty/', headers=headers, data=data, verify=False)
					#response = s.post('https://api.niftygateway.com/user/purchase-centralized-listing/', headers=headers, data=data, verify=False)

				elif self.paymode.lower() == "balance":

					response = self.s.post('https://api.niftygateway.com/user/purchase-unminted-nifty/', headers=headers, data=data1, verify=False)
					#response = s.post('https://api.niftygateway.com/user/purchase-centralized-listing/', headers=headers, data=data, verify=False)
				elif self.paymode.lower() == "eth":
					response = self.s.post('https://api.niftygateway.com/user/purchase-unminted-nifty/', headers=headers, data=data2, verify=False)

				else:
					log("e", "Wrong payment methode check your csv")
					return False

				self.end = time.time()
				self.delta = self.end - self.start
				#print(response.content)
				self.url = f"https://niftygateway.com/itemdetail/primary/{self.addy}/{self.niftyType}"

				try:
					check = response.json()
				except Exception as e:
					log("e", "Could not read response from checkout " + str(e))
					time.sleep(0.1)

				#pipi = True
				#print(response.content)
				try:
					if "no longer available" in response.text:
						log("w", "Item not available yet, retrying")
						time.sleep(0.1)
						#sendwebhookdecline(self.name, self.url, self.photo, self.price, self.delta, self.addy, self.accname, self.webhook)
					elif "Request was throttled" in response.text:
						log("w", "Still waiting on item to drop")

						if len(self.proxy_list) > 0:
							self.s.proxies = get_proxy(self.proxy_list)
						#print(response.headers)
						time.sleep(0.1)

					elif "This project is not for sale on the primary market" in response.text:
						log("i", "item is not available anymore")
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
						#sendwebhookdecline(self.name, self.url, self.photo, self.price, self.delta, self.addy, self.accname, self.webhook, self.email, self.passWord)
						return False

					elif "has ended" in response.text:
						log("e", "The sale has ended")
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
						time.sleep(0.1)
						return False

					elif "is no longer open" in response.text:
						log("e", "The sale is closed")
						time.sleep(0.1)
						#print(response.headers)
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
						return False

					elif check['didSucceed'] == True:
						log("s", "Succesfully checkout") #
						writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='SUCCESS')
						return True

				except Exception as e:
					#message = check['message']
					log("e", "Decline reason: " + str(e))
					sendwebhookdecline(self.name, self.url, self.photo, self.price, self.delta, self.addy, self.accname, self.webhook, self.email, self.passWord)
					time.sleep(0.1)
					writeLog(site='Nifty-FCFS-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=self.name,addy2=self.addy,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=self.url,status='FAILED')
					return False

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(0.1)

			except Exception as e:
				log('e', str(e))


def main(token):
	try:
		config = json.loads(open('config.json').read())
	except Exception:
		log('i', "Couldn't load config file.")
		stop_program()
	webhook = config['webhook']
	delay = config['DELAY']

	try:
		proxies = read_from_txt("proxies.txt")
	except Exception:
		proxies = 0
		log('i', "Proxy file is empty, using local host.")

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

	threads = []

	for i in rows:
		accname = i[1]
		email = i[2]
		password = i[3]
		addy = i[4]
		niftyType = i[5]
		paymode = i[6]
		raffle = i[7]
		pack = i[8]
		prox = i[21]
		t = Thread(target=CHECKOUT, args=(accname, email, password, addy, niftyType, paymode, raffle, pack, webhook, proxies, token, prox))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	stop_program()
