import requests
import json
import time
import os
import imaplib
import email
from datetime import date
from datetime import datetime
import csv
from threading import Thread
from func.log import log
from func.functions import *
import threading

requests.packages.urllib3.disable_warnings()

class CHECK:
	def __init__(self, email, password, token, proxy_list):
		self.email = email.lower()
		self.passWord = password
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

		log("i", "Requesting login token")

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
		'grant_type': 'password',
		'client_id': 'PsXGrgaKodNkEhtSYFOL8klAD2M3TlO4VgNNFuug',
		'password': self.passWord,
		'username': self.email
		}
		attempts = 0
		while attempts <= 10:
			try:
				response = self.s.post('https://api.niftygateway.com/o/token/', headers=headers, data=data, verify=False)
				#print(response.content)
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
		while attempts <= 10:
			try:
				response = self.s.post('https://api.niftygateway.com/o/twofa/', headers=headers, data=data, verify=False)
				#print(response.content)
				resp = response.json()
				if response.status_code == 200 and resp['didSucceed'] == True:
					log("s", "Successfuly sent 2fa code, saving session in db")
					self.accessTok = resp['access_token']
					self.refreshTok =  resp['refresh_token']

					create_table("./db/email_db", self.email, self.accessTok, self.refreshTok)


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
	threads = []

	EMAIL_ACCOUNT = ''
	PASSWORD = ''




	mail = imaplib.IMAP4_SSL('imap.gmail.com')
	mail.login(EMAIL_ACCOUNT, PASSWORD)
	mail.list()
	mail.select("inbox")

	result, data = mail.search(None, '(FROM "elymabey@outlook.com" SUBJECT "verify")' )

	ids = data[0] # data is a list.
	id_list = ids.split() # ids is a space separated string
	latest_email_id = id_list[-1] # get the latest

	result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822)             for the given ID

	raw_email = data[0][1] # here's the body, which is raw text of the whole email
	# including headers and alternate payloads
	raw_email_string = raw_email.decode('utf-8')
	print(raw_email_string)

"""
	for i in rows:
		email = i[0]
		password = i[1]
		token = i[2]

		t = Thread(target=CHECK, args=(email, password, token, proxies))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)
"""



