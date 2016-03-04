import requests
from bs4 import BeautifulSoup as bs
import os
import json
import sqlite3
import re
import time
import logging
from sgdb import SgDb
from functools import partial


logger = logging.getLogger('sg_logger.sg_requests')


class InvalidCookieException(Exception):
    pass


class SgRequests(object):
    """ A simple class using requests on steamgifts
    We assume your account is well configure

    usage:

        >>>sg = SgRequests()
        >>>ag.run()

    require:
        You should put a valid cookie in the file 'cookie.txt'
    """
    base_url = 'http://www.steamgifts.com'
    sqlite_db_name = 'sg_entry.db'
    timeout = (30.0, 30.0)  # (timeout, time to read)
    time_to_sleep_between_each_request = 0
    header_pages = {
        'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }
    header_entry_template = {
        'Host': 'www.steamgifts.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }

    def __init__(self):
        """ Require valid cookie in the file '/cookie.txt'"""
        working_dir = os.getcwd()
        f = open(working_dir + '/cookie.txt', "r+")
        text = f.read()
        self.cookie = {'PHPSESSID': str(text).strip()}
        f.close()
        try:
            self.xsrf_token = self.__get_xsrf_token()
        except:
            logger.error("Invalid cookie")
            raise InvalidCookieException()
        self.points = self.__get_current_points()
        self.db = SgDb(self.sqlite_db_name)

    def __get_xsrf_token(self):
        r = self.get('')
        soup = bs(r.text, 'html.parser')
        js_script = soup.find('script', {'type': 'text/javascript'})
        return re.search("', '\w*'", js_script.text).group()[4:-1]

    def __get_current_points(self):
        r = self.get('')
        soup = bs(r.text, 'html.parser')
        return int(soup.find('span', {'class': 'nav__points'}).text)

    def __getLink(self, soup):
        return soup.find('a', {'class': 'giveaway__heading__name'}).attrs['href']

    def __getCode(self, soup):
        link = self.__getLink(soup)
        return link.split('/')[2]

    def __getPrice(self, soup):
        return int(soup.findAll('span', {'class': 'giveaway__heading__thin'})[-1].text[1:-2])

    def get(self, path_url):
        time.sleep(self.time_to_sleep_between_each_request)
        logger.info('getting page : "' + self.base_url + path_url + '"')
        return requests.get(self.base_url + path_url, headers=self.header_pages, cookies=self.cookie, timeout=self.timeout)

    def enter(self, giveaway_link, giveaway_code, giveaway_price):
        """ Send a request to enter to the giveaway
        This fonction check if giveaway already entered,
        check if you have enough points
        If it is ok then do the request to enter
        If enter is ok then register the entry in database
        Check log to see what happen
        :param giveaway_link: link for giveaway (exemple: '/giveaway/xxxxx/game')
        :param giveaway_code: code of the giveaway
        :param giveaway_price: int value of giveaway
        """
        if not self.db.check_if_already_entered(giveaway_code):
            if giveaway_price <= self.points:
                time.sleep(self.time_to_sleep_between_each_request)
                payload = {'xsrf_token': self.xsrf_token,
                           'do': 'entry_insert', 'code': giveaway_code}
                header_entry = self.header_entry_template
                header_entry['Referer'] = self.base_url + giveaway_link
                r = requests.post(self.base_url + "/ajax.php",
                                  headers=header_entry, cookies=self.cookie, data=payload, timeout=self.timeout)
                if r.status_code == 200:
                    json_tmp = json.loads(r.text)
                    if json_tmp['type'] == 'success':
                        self.points = int(json_tmp['points'])
                        self.db.add_an_entry(
                            giveaway_code, giveaway_price, giveaway_link)
                        logger.info('Adding entry : ' + giveaway_code)
                    else:
                        logger.warning('Not a succes for : ' + giveaway_code)
                else:
                    logger.warning(
                        'Failed with status_code : ' + str(r.status_code))
            else:
                logger.info('Not enough points to enter : ' +
                            giveaway_link + ' / cost : ' + str(giveaway_price))
        else:
            logger.info('Already Done for : ' + giveaway_code)

    def __page_has_next(self, soup):
        tmp = soup.findAll('a')
        return len([x for x in tmp if x.has_attr('data-page-number')]) != 0

    def __isLimitReached(self, value, list):
        if (value != -1):
            return value <= sum(c for (a, b, c) in list)
        else:
            return False

    def __generateEntry(self, soup):
        page_heading = soup.find('div', {'class': 'page__heading'})
        soup_wishlist = page_heading.next_sibling.next_sibling
        div = soup_wishlist.find_all(
            'div', {'class': 'giveaway__row-outer-wrap'})
        for i in div:
            yield (self.__getLink(i), self.__getCode(i), self.__getPrice(i))

    def __generateEntry50copies(self, soup):
        pinned = soup.find('div', {'class': 'pinned-giveaways__outer-wrap'})
        div = pinned.find_all(
            'div', {'class': 'giveaway__row-outer-wrap'})
        for i in div:
            yield (self.__getLink(i), self.__getCode(i), self.__getPrice(i))

    def generateEntryByBrowsingPage(self, path_url, func, page=1):
        r = self.get(path_url + '&page=' + str(page))
        soup = bs(r.text, 'html.parser')
        yield from func(soup)
        if self.__page_has_next(soup):
            yield from self.generateEntryByBrowsingPage(path_url, func, page=(page + 1))

    def generateWishlistEntry(self):
        yield from self.generateEntryByBrowsingPage('/giveaways/search?type=wishlist', self.__generateEntry)

    def generate50copiesEntry(self):
        yield from self.generateEntryByBrowsingPage('/giveaways/search?q=SthNeverMatchHere', self.__generateEntry50copies)

    def generateAllEntry(self):
        yield from self.generateEntryByBrowsingPage('/giveaways/search?', self.__generateEntry)

    def generateEntryByName(self, name):
        yield from self.generateEntryByBrowsingPage('/giveaways/search?q=' + name, self.__generateEntry)


    def pointGreaterThan(self, point):
        return self.points > point

    def doEntryByGenerator(self, entryGenerator, canContinue):
        for g in entryGenerator:
            if not canContinue():
                break
            self.enter(*g)

    def run(self):
        self.doEntryByGenerator(self.generateWishlistEntry(), partial(self.pointGreaterThan, point=0))
        self.doEntryByGenerator(self.generate50copiesEntry(), partial(self.pointGreaterThan, point=0))
        self.doEntryByGenerator(self.generateAllEntry(),
                                partial(self.pointGreaterThan, point=0))

    def sync(self):
        header = self.header_entry_template
        header['Referer'] = "http://www.steamgifts.com/account/profile/sync"
        payload = {"xsrf_token": self.xsrf_token,
                   "do": "sync"}
        r = requests.post(self.base_url + "/ajax.php",
                          cookies=self.cookie, headers=header, data=payload)
        if r.status_code == 200:
            json_tmp = json.loads(r.text)
            if json_tmp['type'] == 'success':
                logger.info(json_tmp["msg"])
            else:
                logger.warning("Fail to sync account")
        else:
            logger.warning(
                'Failed to sync with status_code : ' + str(r.status_code))
