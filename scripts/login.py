import requests
import json
import time
import os
from datetime import date
import csv
from threading import Thread
from func.log import log
from func.functions import *
import threading

requests.packages.urllib3.disable_warnings()

class CHECK:
	def __init__(self, accname, email, password, username, proxy_list):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		self.username = username
		self.verifCode = ""
		self.proxy_list = proxy_list
		self.s = requests.session()
		self.UA = getUA()
		self.link = "https://niftygateway.com/"

		if len(self.proxy_list) > 0:
			self.s.proxies = get_proxy(self.proxy_list)


		while True:

			login = self.login()
			if login == False:
				break
			else:
				break

	def login(self):

		log('i', "Requesting login captcha")

		if json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower() == 'anticaptcha':
			#log('i', Fore.CYAN + "Solving captcha with Anticaptcha")
			gresponse = solvecaptcha(api_key=json.loads(open('config.json').read())['CAPTCHA_KEY'] ,
									site_key='6LdbJ2UbAAAAAIYAB4viUUyuNmeTZ6GAZo7BNzXL',
									url=self.link)
		elif json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower()  == '2captcha':
			#log('i', Fore.CYAN + get_time() + "Solving captcha with 2captcha")
			gresponse = solveV3captcha(self.link, json.loads(open('config.json').read())['CAPTCHA_KEY'],
									'6LdbJ2UbAAAAAIYAB4viUUyuNmeTZ6GAZo7BNzXL', self.s)
		elif json.loads(open('config.json').read())['CAPTCHA_PROVIDER'].lower() == 'capmonster':
			gresponse = capmonstersolver(api_key=json.loads(open('config.json').read())['CAPTCHA_KEY'] ,
									site_key='6LdbJ2UbAAAAAIYAB4viUUyuNmeTZ6GAZo7BNzXL',
									url=self.link)
		else:
			log('e', "You are missing the provider, please check your info in config")
			stop_program()

		log("i", "Requesting login token")
		"""
		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'user-agent': self.UA,
			'content-type': 'application/x-www-form-urlencoded',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9',
		}


		headers = {
			'Host': 'api.niftygateway.com',
			'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
			'accept': 'application/json, text/plain, */*',
			'x-castle-client-id': 'BQU4IRqT7r3ESkiphaLihFGq12sm1w94JdnZazXZzDsBX0JvPNp-Rjjs3lUynipvad0hpLe2hWg-JC7bedGtD1-UvRFPtb4KCez8WwbxnwpFsLwfSaq6UAaQvB9DtfImR7ryJHX5iksX6Y1aE4blQgaYohtKvIUORJK7Hwns4VwI6uRLDpKaP2uV_ktKsLkOBp63CE22-0tlsaAES7z9UhT34kUS7ONeCOjnUgaKsw1Hq7tEE-rlRRXvvmMV7upTQ7ixCVHa1eAmTdoKFui3DRS8tPc_kLwfQ7X6OQ_5hyNi-ZUZR6m6AkWq8l0V6XZ_F_bjRBfg5VsK-eNRFunoWxb5kybO2U1rlmB5aybZeWvj2WX1nnN8FYlFawGfs5IrZonSaybZffSGSHXnQpS2JkC5kitmmZcr7Em2CwbY0ksm2NRr2Q',
			'sec-ch-ua-mobile': '?0',
			'content-type': 'application/x-www-form-urlencoded',
			'user-agent': self.UA,
			'x-sid': '803df952-51b5-42af-b9a0-23bd77e6e4bf',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'referer': 'https://niftygateway.com/',
			'accept-language': 'en-US,en;q=0.9',
		}


		data = {
		'grant_type': 'password',
		'client_id': 'PsXGrgaKodNkEhtSYFOL8klAD2M3TlO4VgNNFuug',
		'password': self.passWord,
		'username': self.email,
		'captcha_token_v3': gresponse
		}
		"""

		headers = {
			'authority': 'api.niftygateway.com',
			'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
			'accept': 'application/json, text/plain, */*',
			'x-castle-client-id': 'Ly8SCzC5xJfuYGKDr4jIrnuA_eu0XD_4t1lL66dZXruT39DvrlrpxqpsTNWgHrjv-12zJCU2F-ispLxb61E_j80UL5HdNSyKm2xu25RxDYrXMC6f2yoo0JQQLp_RNWCm1TpgpOd5GMuFaR_agQZ3wpQYMJvYPBeO1hIpn5tsc9yaanbLnBIIv_kVbMvYMCuOlB4liN82acv3MTKE2Txv0oZ3cMWAbHHemmh10pQKIY3VKynEgWp3xYdvLOOHbnjT0TgjicNaR2C0zUiKhGgljYY8JnetEC6f0TVouZ15FaPweQeZ1SkogtcqYN2HaeT_hXZxxIVgd9uYeXHRhGl624R5AaZYWdzrG-Dy62JZ8rt8WflBDvDtnwXH-ooOOA-k9JpA67RZ-XYFxO923TgpisAo9F890AmuZSsQj7lbQOW0WUfrSw',
			'sec-ch-ua-mobile': '?0',
			'content-type': 'application/x-www-form-urlencoded',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
			'x-sid': 'c2444852-daf2-4c73-98a8-d9f26c5171a2',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'referer': 'https://niftygateway.com/',
			'accept-language': 'en-US,en;q=0.9',
		}

		data = {
		'grant_type': 'password',
		'client_id': 'PsXGrgaKodNkEhtSYFOL8klAD2M3TlO4VgNNFuug',
		'password': 'Soleil@777!',
		'username': 'cypri99@gmail.com',
		'captcha_token_v3': '03AGdBq24M0_vN0bo_EHS9Ct8LlA0bYFnSpQh8wM8Tt7Lm6f_VDo5QEJMiE9UcptiKtDIYhO10jK-wu_iN4TyO4Ho6LeauVv8TOvvZIgc2EXpR91pYugABvGqTWlCVIO68CopCkl267TeTyDI8EpMSh2GmakiB0V-p9suh2aTus0QlxPQcuvNCQUMOqEWx-sClJNFyuPD9k2jYV74c5cKmFRhBCE64kYEhgVBUsDb6I3J4pO19TSg-L2elJ4nQsJvZRhgv3JocT8ZEqo073veO_MVkhb9sIDQ05A6EJGBNDhLVSvUivC6CvpV1YusZfEtn8UfmmL63vUEe6SSq0-m33FIsAWa_tsdeYr_qw06R2IXbyxlCd925cCifUyI3Mjm3EcsGmZVYj3AaorWX5f_gxELPIsZbeYnVjrd7jeQcCc6anqAGbI9ZGVdolQ3fMhdXdK-Da0Lnptfd'
		}

		print(data)
		attempts = 0
		while attempts < 1:
			try:
				response = self.s.post('https://api.niftygateway.com/o/token/', headers=headers, data=data, verify=False, timeout=8)
				print(response.content)
				if "messageerror" in response.text:
					log("e", "Account is temp ban")
					return False
				if "Invalid credentials given." in response.text:
					log("e", "Invalid credentials")
					return False
				resp = response.json()
				if response.status_code == 200 and resp['didSucceed'] == True:
					log("s", "Successfuly requested 2fa code")
					self.twotok = resp['data']['twofa_token']
					with open('{}.csv'.format('LoginVerif'),'a',newline='') as output:
						writer = csv.writer(output)

						writer.writerow(
							[
								self.email,
								self.passWord,
								self.twotok,
								self.verifCode
							]
						)
					return True
				else:
					log("e", "Could not request code, retrying")
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
					self.UA = getUA()

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				self.UA = getUA()
				time.sleep(1)
			except Exception as e:
				log('e', "Code request error: " + str(e))
				time.sleep(0.1)
				return False
			attempts = attempts + 1
			if attempts == 10:
				return False
class SESSION:
	def __init__(self, accname, email, password, token, codeVerif, proxy_list):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		self.verifCode = codeVerif
		self.token = token
		self.proxy_list = proxy_list
		self.s = requests.session()
		self.UA = getUA()
		if len(self.proxy_list) > 0:
			self.s.proxies = get_proxy(self.proxy_list)


		while True:

			login = self.login()
			if login == False:
				break
			else:
				break

	def login(self):

		log("i", "Sending verification code")

		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'user-agent': self.UA,
			'content-type': 'application/x-www-form-urlencoded',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9',
		}

		data = {
			'token': self.token,
			'code': self.verifCode
		}
		attempts = 0
		while attempts < 1:
			try:
				response = self.s.post('https://api.niftygateway.com/o/twofa/', headers=headers, data=data, verify=False, timeout=6)
				#print(response.content)
				resp = response.json()
				if response.status_code == 200 and resp['didSucceed'] == True:
					log("s", f"Successfuly sent 2fa code, saving session in db [{self.email}]")
					self.accessTok = resp['access_token']
					self.refreshTok =  resp['refresh_token']

					create_table("./db/email_db", self.email, self.accessTok, self.refreshTok)


					return True
				else:
					log("e", f"Could not request code, retrying [{self.email}]")
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
					self.UA = getUA()

			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				self.UA = getUA()
				time.sleep(1)
			except Exception as e:
				log('e', "Code request error: " + str(e))
				time.sleep(0.1)
				return False
			attempts = attempts + 1
			if attempts == 10:
				return False

def main(token):

	try:
		create_db("./db/email_db")
	except:
		log("e", "Could not create db")

	#input("")

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
	threads = []

	for i in rows:
		accname = i[1]
		email = i[2]
		password = i[3]
		username = i[9]

		t = Thread(target=CHECK, args=(accname, email, password, username, proxies))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	input("PRESS ENTER WHEN READY")

	with open('LoginVerif.csv', newline='') as f:
		creader = csv.reader(f)
		next(creader)
		#print(reader[1:])
		#input("")

		for row in creader:
			email = row[0]
			password = row[1]
			token = row[2]
			codeVerif = row[3]

			t = Thread(target=SESSION, args=(accname, email, password, token, codeVerif, proxies))

			threads.append(t)
			t.start()
			time.sleep(0.1)

		for t in threads:
			t.join()
			#time.sleep(2)

	stop_program()

