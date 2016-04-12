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

### Option arguments
To sync your account, run:
```
python main.py --sync
```

If you want to get mail when you won a game or receive messages, you should complete the file mailNotifier.py
with the mail who will receive notification, the mail who sends them with the password.
The program use smtp to send mail so you have to find the smtp of your mail.
Moreover, you need the smtp port (it should be 587).

```
python main.py --notif
```

##Steamgifts account configuration
To use this program properly, you should configure your Steamgifts account as following:

Hide giveaways for games you already own? Yes

Hide giveaways for DLC if you're missing the base game? Yes

Hide giveaways above your level? Yes
