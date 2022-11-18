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
	def __init__(self, accname, email, password, proxy_list, prox):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		tt = fetch_db(self.email)
		self.accessTok = tt[0]
		self.refreshTok = tt[1]
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

			resp = self.login()
			if resp == False:
				break

			resp2 = self.userInfo()
			if resp2 == False:
				break
			resp3 = self.delCard()
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

	def userInfo(self):

		headers = {
			'authority': 'api.niftygateway.com',
			'accept': 'application/json, text/plain, */*',
			'authorization': 'Bearer ' + self.accessTok,
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
			'origin': 'https://niftygateway.com',
			'sec-fetch-site': 'same-site',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
			'dnt': '1',
		}
		attempts = 0
		while attempts <= 5:
			try:
				#print(self.s.proxies)
				profile = self.s.get('https://api.niftygateway.com/stripe/list-cards/', headers=headers, verify=False)
				#print(profile.content)
				#input("")
				try:
					resp = profile.json()
					self.cards = []
					if not resp['data']:
						log("w", "No cards in account, quitting")
						return False

					for i in resp['data']:
						self.cards.append(i['id'])
					#self.card = resp['data'][0]['id']
					#print(self.cards)
					#input("")
					return True
				except Exception as e:
					log("e", "Can't load user Info response or no cards in")
					if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
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
			if attempts == 5:
				return False

			#print(profile.content)



	def delCard(self):


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

		while True:
			try:
				for t in self.cards:
					data = {
						"card_id":t
					}
					response = self.s.post('https://api.niftygateway.com//stripe/delete-card/', headers=headers, json=data, verify=False)
					#print(response.text)
					if "Card " in response.text:
						log("s", "Card succesfully deleted")
						#return True

					elif response.status_code == 500:
						log("e", "Back end error")
						writeLog(site='Nifty-CC-Delete-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
						return False
					elif "Unable to delete credit card" in response.text:
						log("i", "All cards were deleted")
						writeLog(site='Nifty-CC-Delete-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='SUCCESS')
						return True
					elif "Error occured" in response.text:
						log("i", "All cards were deleted")
						writeLog(site='Nifty-CC-Delete-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='SUCCESS')
						return True
					else:
						log("e", "Error deleting card with status code [%s]" % response.status_code)
						writeLog(site='Nifty-CC-Delete-{}'.format(date.today()),first=self.accname,last=self.passWord,email=self.email,addy1=None,addy2=None,zip=None,state=None,country=None,city=None,phone=None,insta=None,size=None,link=None,status='FAILED')
						return False


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
						self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + " Deleting Card")
				time.sleep(0.1)
				return False
			#print(response.content)



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

	for i in rows:
		accname = i[1]
		email = i[2]
		password = i[3]
		prox = i[21]

		t = Thread(target=ACCOUNT, args=(accname, email, password, proxies, prox))

		threads.append(t)
		t.start()
		time.sleep(float(delay))

	for t in threads:
		t.join()
		#time.sleep(2)

	stop_program()
