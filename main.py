from sg_requests import SgRequests
from sg_requests import InvalidCookieException
import logging
import sys



def setup():
    logger = logging.getLogger('sg_logger')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('sg.log')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

def handleCookieException():
    print("Invalid cookie, check 'cookie.txt' file or see README.md")

def main():
    setup()
    try:
        sg = SgRequests()
        if '--sync' in sys.argv:
            sg.sync()
        sg.run()
        if '--notif' in sys.argv:
            sg.sync()
            sg.checkNotif()
    except InvalidCookieException:
        handleCookieException()

if __name__ == '__main__':
    main()
