import requests
import json
import time
import base64
from datetime import date
from threading import Thread
from func.log import log
from func.functions import *
import threading
import os
import re
import phonenumbers

requests.packages.urllib3.disable_warnings()

class ACCOUNT:
	def __init__(self, accname, email, password, proxy_list, prox):
		self.accname = accname
		self.email = email.lower()
		self.passWord = password
		tt = fetch_db(self.email)
		self.accessTok = tt[0]
		self.refreshTok = tt[1]
		self.tries = 0
		self.proxy_list = proxy_list
		self.ua = getUA()
		self.s = requests.session()
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



	def checkAcc(self):

		log('i', "Fetching image and quote")
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
		#attemps = 0
		while True:
			try:
				response = self.s.get('https://api.niftygateway.com/user/profile/', headers=headers, verify=False)

				res = response.json()
				#print(res)


				img_url = res['userProfile']['profile_pic_url']
				name = res['userProfile']['name']
				profile_url = res['userProfile']['profile_url']

				#print(profile_url)
				#input("")
				r = self.s.get("https://goquotes-api.herokuapp.com/api/v1/random?count=1", verify=False)
				#r.json()
				quote = r.json()['quotes'][0]['text']
				#print(quote)

				data = {
					"bio": quote,
					"prof_pic_url": img_url,
					"name": name,
					"prof_url": profile_url
				}
				#print(data)
				log('i', "Got quote and added it")

				response = self.s.post('https://api.niftygateway.com/user/alter-user-profile/', headers=headers, data=data, verify=False)

				headers1 = {
					'authority': 'picsum.photos',
					'upgrade-insecure-requests': '1',
					'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
					'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
					'sec-fetch-site': 'none',
					'sec-fetch-mode': 'navigate',
					'sec-fetch-user': '?1',
					'sec-fetch-dest': 'document',
					'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6,en-AU;q=0.5',
					#'cookie': '__cfduid=db2e82484a84880f6840d214864ff6d9b1615384012; _ga=GA1.2.1354780666.1615384015; _gid=GA1.2.416707745.1615384015',
					'dnt': '1',
				}

				response3 = self.s.get('https://picsum.photos/200', headers=headers1, verify=False)

				new_img = str(base64.b64encode(response3.content))
				rr = new_img.replace("b'", "")
				sss = rr.replace("'", "")
				#print(sss)
				data3 = {
					"new_profile_pic":f"data:image/jpeg;base64," + sss
				}
				#print(data3)

				headers = {
					'Host': 'api.niftygateway.com',
					'accept': 'application/json, text/plain, */*',
					'authorization': 'Bearer ' + self.accessTok,
					'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
					'content-type': 'application/json',
					'origin': 'https://niftygateway.com',
					'sec-fetch-site': 'same-site',
					'sec-fetch-mode': 'cors',
					'sec-fetch-dest': 'empty',
					'accept-language': 'en-US,en;q=0.9',
				}

				response = self.s.post('https://api.niftygateway.com//user/update-profile-picture/', headers=headers, json=data3, verify=False)

				#print(response.content)

				log('s', "Got image and added it")
				return True


			except (requests.exceptions.ProxyError, requests.exceptions.SSLError):
				log('i', "Proxy is banned")
				if len(self.proxy_list) > 0:
					self.s.proxies = get_proxy(self.proxy_list)
				time.sleep(1)
			except Exception as e:
				log('e', str(e) + "login")
				time.sleep(1)
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
