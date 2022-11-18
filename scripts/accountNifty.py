import requests
import json
import os
import time
from datetime import date
from threading import Thread
from func.log import log
from func.functions import *
import threading

requests.packages.urllib3.disable_warnings()

class ACCOUNT:
	def __init__(self, accname, email, password, username, name, webhook, proxy_list, prox):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		self.webhook = webhook
		self.name = name
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


		while True:
			resp = self.create()
			if resp == False:
				break
			else:
				break


	def create(self):

		headers = {
			'Host': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'user-agent': self.UA,
			'content-type': 'application/json;charset=UTF-8',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9',
		}

		data = {
			"email": self.email,
			"password": self.passWord,
			"username": self.username,
			"name": self.name,
			"subscribe": "false",
			"referral": ""
		}
		while True:
			try:
				response = self.s.post('https://api.niftygateway.com/users/signup/', headers=headers, json=data, verify=False)

				try:
					resp = response.json()['didSucceed']

					if resp == True:
						log("s", f"Account {self.email} was succesfully created" )
						writeLog(site='Nifty-AccountGen-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='SUCCESS')
						return True
					elif "url_taken" in response.text:
						log("e", "Account or username already taken")
						writeLog(site='Nifty-AccountGen-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
						return False
					elif "email_registered" in response.text:
						log("e", "Account or username already taken")
						writeLog(site='Nifty-AccountGen-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
						return False
					else:
						log("e", "Could not create account {%s}" % self.email)
						print(response.content)
						time.sleep(1)
				except:
					log("e", "Could not create account, retying...")
					#print(response.content)
					time.sleep(1)
					self.create()


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				self.UA = getUA()
				time.sleep(0.1)
			except Exception as e:
				log('e', str(e) + "login")
				time.sleep(0.1)
				writeLog(site='Nifty-AccountGen-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
				return False




def main(token):
	try:
		config = json.loads(open('config.json').read())
	except Exception:
		log('i', "Couldn't load config file.")
		stop_program()
	webhook = config['webhook']
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
		prox = i[21]

		t = Thread(target=ACCOUNT, args=(accname, email, password, username, name, webhook, proxies, prox))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	stop_program()
