import sg_requests
import logging

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

def main():
    setup()
    sg = sg_requests.SgRequests()
    sg.run()

if __name__ == '__main__':
    main()
