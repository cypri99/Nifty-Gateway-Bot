# Nifty-Gateway-Bot
## Bot Menu
<img width="656" alt="Bot_Menu" src="https://user-images.githubusercontent.com/42317273/202818919-379b7676-ba13-4ee0-b2c3-ab50c987c4d2.png">

Here is one of the bots I made for NiftyGateway. It is probably not working anymore because they might have changed some endpoints but it's an easy fix.
Sorry if the code is a bit messy but it was a script for personal use!

You can get the bot to run the menu by doing:

1) Make sure to have python3

2) pip install -r requirements.txt

3) python3 main.py

It will give you a token error if you try to choose a script because I used to have every user registered in my API for analytics purpuses. 

I am mainly putting this code out for you to see the process of each scripts. Up to you to modify it.

# AccLegit.py

That was a script to make your account look more legit by adding a picture and a bio.

# accountNifty.py

Script to create accounts and check if some were already made or not

# checker.py

Script to check which NFTs were in your account

# deleterCC.py

Made to delete the credit cards on the nifty accounts. 

# login.py

I had to make this script pretty fast because NiftyGateway added 2FA and I had to create a script to gather these codes and add them to a database because login tokens were valid for 30 days (something like that)

# NiftyCC.py

Script to add credit cards to nifty accounts

# niftyfcfs.py

Here is all the magic ! That is where I would have a module for first come first serve and raffle. 2 different functions in the same script

# Niftynumcheck.py

Every nifty account needed to be phone verified and sometimes numbers would expire from the SMS providers.

# Scraper.py

I think I was in the making of automating the process of reading the 2fa codes in the emails

#VerifNifty.py

This was used to phone verified your accounts by a 3rd party

