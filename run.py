import func.logo
from func.log import log
from func.functions import is_int
import sys, json
from colorama import Fore, init
from datetime import date

from scripts import niftyfcfs
from scripts import accountNifty
from scripts import verifNifty
from scripts import NiftyCC
from scripts import deleterCC
from scripts import niftyNumCheck
from scripts import checker
from scripts import acclegit
from scripts import login
from scripts import scraper
from func import functions

supported_scripts = {
    "Nifty auto-checkout/entry": niftyfcfs,
    "Nifty Account Gen": accountNifty,
    "Nifty Phone Verification": verifNifty,
    "Nifty CC Adder": NiftyCC,
    "Nifty CC Deleter": deleterCC,
    "Nifty Checker (phone)": niftyNumCheck,
    "Nifty Win Checker": checker,
    "Nifty Image Adder and Quote": acclegit,
    "Nifty Token login": login,
    #"Nifty Code Scraper": scraper
}

def run_from_console():

    print(Fore.GREEN + func.logo.console_logo + Fore.WHITE)
    print(f"Kichta x Lockers x nifty V 0.1.16 (Made by zanga99#0001)\n")

    #token = functions.activate()

    index = 1
    print("Menu:")
    config = json.loads(open('config.json').read())
    tkey = config["KEY"]


    for key, value in sorted(supported_scripts.items()):
        print("{}) [{}]".format(index, key))
        index += 1

    choice = input("\nPlease choose an option: ")
    if not (is_int(choice)) or int(choice) > len(supported_scripts):
        print("Bad input. Exiting...")
    else:
        key_chosen, value_chosen = sorted(supported_scripts.items())[int(choice) - 1]
        print("Starting {}...\n\n".format(key_chosen))
        eval("value_chosen.main(token)")



