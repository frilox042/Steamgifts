# Steamgifts
Auto-join Steamgifts giveaways, create stat with database, log
## Installation
This program works with python 3.5

For initializing the SQLite database, run:
```
python init_sg_db.py
```
A file named "sg_entry.db" should appear.

Put your **Steamgifts cookie** in "cookie.txt".

To find the cookie:

1. Go on Steamgifts
2. Press Ctrl-I
3. Go on Security
4. Click on "see Cookie" button
5. Find cookie named "PHPSESSID"
6. Copy-paste the content in the a file named "cookie.txt"

## Usage
To run the program for Auto-join, run:
```
python main.py
```

##Steamgifts account configuration
To use this program properly, you should configure your Steamgifts account as following:

Hide giveaways for games you already own? Yes

Hide giveaways for DLC if you're missing the base game? Yes

Hide giveaways above your level? Yes

##Todo

* Check if game have been won
* Make a cron
* Sync account
* Use generator for better performance in finding giveaways
* Make easier to configure
* Write unit-test
