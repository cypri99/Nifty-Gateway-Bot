import os
from threading import Lock
import time, datetime, threading
from colorama import Fore, Back, Style
from colorama import init
init()
s_print_lock = Lock()

def gettime():
    now = str(datetime.datetime.now())
    now = now.split(' ')[1]
    threadname = threading.currentThread().getName()
    threadname = str(threadname).replace('Thread', 'Task')
    now = '[' + str(now) + ']' + '[' + str(threadname) + ']'
    return now

def s_print(*a, **b):
     """Thread safe print function"""
     with s_print_lock:
         print(*a, **b)

def log(tag, text):
    # Info tag
    if(tag == 'i'):
        s_print(Fore.CYAN + "[INFO]{} ".format(gettime()) + str(text) + Fore.WHITE)
    # Error tag
    elif(tag == 'e'):
        s_print(Fore.RED + "[ERROR]{} ".format(gettime()) + str(text) + Fore.WHITE)
    # Success tag
    elif(tag == 's'):
        s_print(Fore.GREEN + "[SUCCESS]{} ".format(gettime()) + str(text) + Fore.WHITE)
    # warning tag
    elif(tag == 'w'):
        s_print(Fore.YELLOW + "[WARNING]{} ".format(gettime()) + str(text) + Fore.WHITE)

