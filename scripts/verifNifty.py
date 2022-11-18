import requests
import json
import time
import os
from datetime import date
from threading import Thread
from func.log import log
from func.functions import *
import threading
import re
import phonenumbers

requests.packages.urllib3.disable_warnings()

maxthreads = 250
sema = threading.Semaphore(value=maxthreads)
threads = list()

class ACCOUNT:
	sema.acquire()
	def __init__(self, accname, email, password, webhook, apiKey, proxy_list, countryCode, provider, prox):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		self.webhook = webhook
		self.apiKey = apiKey
		self.tries = 0
		self.proxy_list = proxy_list
		self.countryCode = countryCode
		tt = fetch_db(self.email)
		self.accessTok = tt[0]
		self.refreshTok = tt[1]
		self.ua = getUA()
		self.s = requests.session()
		self.provider = provider.lower()
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

			checkResp = self.checkAcc()
			if checkResp == False:
				break
			getResp = self.get_number()
			if getResp == False:
				break
			verif1Resp = self.verify1()
			if verif1Resp == False:
				break
			getResp = self.get_code()
			if getResp == False:
				break
			verif2Resp = self.verify2()
			if verif2Resp == True:
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



	def checkAcc(self):

		log('i', "Checking account status")
		headers = {
			'Host': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9',
		}
		while True:
			try:
				response = self.s.get('https://api.niftygateway.com//user/verification/', headers=headers, verify=False)
				try:
					resp = response.json()
					#print(resp)
				except Exception as e:
					log("e", "Error reading account status: " + str(e))
					time.sleep(1)

				try:
					if resp['message']['verified'] == True:
						log("e", "Account already verified, quitting")
						writeLog(site='Nifty-PhoneVerif-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='VERIFIED')
						return False
					else:
						response = self.s.delete('https://api.niftygateway.com/user/verification/', headers=headers)
						return True
				except:
					log("i", "Account not verified, proceeding")
					response = self.s.delete('https://api.niftygateway.com/user/verification/', headers=headers)
					return True
					#self.get_number()


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + "login")
				time.sleep(1)
				return False




	def get_number(self):
		log("i", "Getting number")
		if self.provider == "smspva":
			self.sms_pva = smsPvaAPI(self.apiKey)

			value = self.sms_pva.get_balance("opt19")
			v = value['response']
			if int(v) < 1:
				log("e", "Not enough balance")
				return False
			phoneRes = self.sms_pva.get_number(self.countryCode, "opt19")
			self.phone = "+" + str(phonenumbers.country_code_for_region(self.countryCode)) + phoneRes['number']
			self.id2 = phoneRes['id']
			log("s", f"Got phone numer {self.phone}")
			return True

		elif self.provider == "5sim":
			self.fivesim = fiveSIm(self.apiKey)

			value = self.fivesim.get_balance()
			#print(value)
			v = value.split(":")[1]
			if float(v) < 2.5:
				log("e", "Not enough balance")
				return False

			res = self.fivesim.get_number(self.countryCode).split(":")
			#print(res)
			self.phone = res[2]
			self.id2 = res[1]
			log("s", f"Got phone numer {self.phone} with id [{self.id2}]")
			return True

		elif self.provider == "smsactivate":
			self.smsacti = smsActi(self.apiKey)

			value = self.smsacti.get_balance()
			#print(value)
			#input("")
			v = value.split(":")[1]
			if float(v) < 2.5:
				log("e", "Not enough balance")
				return False

			res = self.smsacti.get_number(self.countryCode).split(":")
			if "NO_NUMBERS" in res:
				log("w", "No numbers available")
				return False
			self.phone = "+" + res[2]
			self.id2 = res[1]
			log("s", f"Got phone numer {self.phone} with id [{self.id2}]")
			#input("")
			return True

		else:
			log("e", "Please check name in config.json (5sim, smspva, smsactivate")
			return False

	def get_number2(self):
		log("i", "Getting number")
		if self.provider == "smspva":
			self.sms_pva = smsPvaAPI(self.apiKey)

			value = self.sms_pva.get_balance("opt19")
			v = value['response']
			if int(v) < 1:
				log("e", "Not enough balance")

			phoneRes = self.sms_pva.get_number(self.countryCode, "opt19")
			self.phone = "+" + str(phonenumbers.country_code_for_region(self.countryCode)) + phoneRes['number']
			self.id2 = phoneRes['id']
			log("s", f"Got phone numer {self.phone}")

		elif self.provider == "5sim":
			self.fivesim = fiveSIm(self.apiKey)

			value = self.fivesim.get_balance()
			#print(value)
			v = value.split(":")[1]
			if float(v) < 2.5:
				log("e", "Not enough balance")

			res = self.fivesim.get_number(self.countryCode).split(":")
			#print(res)
			self.phone = res[2]
			self.id2 = res[1]
			log("s", f"Got phone numer {self.phone} with id [{self.id2}]")

		elif self.provider == "smsactivate":
			self.smsacti = smsActi(self.apiKey)

			value = self.smsacti.get_balance()
			#print(value)
			#input("")
			v = value.split(":")[1]
			if float(v) < 2.5:
				log("e", "Not enough balance")
				return False

			res = self.smsacti.get_number(self.countryCode).split(":")
			print(res)
			self.phone = "+" + res[2]
			self.id2 = res[1]
			log("s", f"Got phone numer {self.phone} with id [{self.id2}]")
			#input("")
			return True

		else:
			log("e", "Please check name in config.json (5sim, smspva, smsactivate")
			return False

	def verify1(self):
		log("i", f"Verifying account with phone number [{self.phone}]")

		headers = {
			'Host': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
			'content-type': 'application/x-www-form-urlencoded',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}

		data = {
			'to': self.phone
		}
		attempts = 0
		while attempts <= 5:
			try:
				response = self.s.post('https://api.niftygateway.com/user/verification/', headers=headers, data=data, verify=False)
				r2 = self.s.patch('https://api.niftygateway.com//user/verification/', headers=headers)
				#print(response.content)

				try:
					resp = response.json()['didSucceed']

					if resp == True:
						log("s", "Number was sent correctly")
						return True
					elif "Request could not be made with this number" in response.text:
						log("e", "Number is already used in an existing account, changing the number")
						self.get_number2()

					elif "This user is already associated with a number" in response.text:
						log("i", "Deleting existing number")
						response = self.s.delete('https://api.niftygateway.com/user/verification/', headers=headers)
						return True

					else:
						log("e", "Number was not sent")
						print(response.content)
						time.sleep(1)
				except:
					log("e", "Couldn't send number to Nifty ")
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
					return True
					time.sleep(1)

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + " Error at sending number to nifty")
				time.sleep(1)
				return False
			attempts = attempts + 1
			if attempts == 5:
				return False



	def get_code(self):
		log("i", "Waiting for Code")
		if self.provider == "smspva":
			codeRes = self.sms_pva.get_sms_message(self.countryCode, "opt19", self.id2)
			self.codeR = codeRes['sms']
			self.code = re.findall(r'\b\d+\b', self.codeR)[0]
			log("s", f"Got code {self.code}")
			return True
		elif self.provider == "5sim":
			self.fivesim.set_status(self.id2)
			codeRes = self.fivesim.get_sms_message(self.id2)
			#print(codeRes)
			self.code = codeRes.split(":")[1]
			log("s", f"Got code {self.code}")
			return True

		elif self.provider == "smsactivate":
			self.smsacti.set_status(self.id2)
			codeRes = self.smsacti.get_sms_message(self.id2)
			#print(codeRes)
			self.code = codeRes.split(":")[2].replace(" ", "")
			log("s", f"Got code {self.code}")
			return True

		else:
			log("e", "Check provider in config")
			return False



	def verify2(self):
		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
			'content-type': 'application/x-www-form-urlencoded',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}


		data = {
			'code':self.code
		}
		#print(data)
		attempts = 0
		while attempts <= 5:
			try:
				response = self.s.put('https://api.niftygateway.com//user/verification/', headers=headers, data=data, verify=False)

				if "successfully" in response.text:
					log("s", "Account was succesfully verified")
					writeLog(site='Nifty-PhoneVerif-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='SUCCESS')
					return True
				else:
					log("e", "Account was not verified")
					print(response.content)


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + " Error at sending number to nifty")
				time.sleep(1)
				writeLog(site='Nifty-PhoneVerif-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
				return False
			attempts = attempts + 1
			if attempts == 5:
				log("e", "Could not verify Account")
				writeLog(site='Nifty-PhoneVerif-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
				return False

def main(token):
	try:
		config = json.loads(open('config.json').read())
	except Exception:
		log('i', "Couldn't load config file.")
		stop_program()
	webhook = config['webhook']
	apiKey = config['API_KEY']
	countryCode = config['SMS_COUNTRY']
	provider = config['SMS_PROVIDER']
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



	for i in rows:
		accname = i[1]
		email = i[2]
		password = i[3]
		prox = i[21]


		t = Thread(target=ACCOUNT, args=(accname, email, password, webhook, apiKey, proxies, countryCode, provider, prox))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	stop_program()
