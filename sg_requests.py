import requests
from bs4 import BeautifulSoup as bs
import os
import json
import sqlite3
import re
import time
import logging

logger = logging.getLogger('sg_logger.sg_requests')

def getLink(soup):
    return soup.find('a', {'class': 'giveaway__heading__name'}).attrs['href']


def getCode(soup):
    link = getLink(soup)
    return link.split('/')[2]


def getPrice(soup):
    return int(soup.findAll('span', {'class': 'giveaway__heading__thin'})[-1].text[1:-2])


class SgRequests(object):
    """docstring"""
    base_url = 'http://steamgifts.com'
    sqlite_db_name = 'sg_entry.db'
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
        working_dir = os.getcwd()
        f = open(working_dir + '/cookie.txt', "r+")
        text = f.read()
        self.cookie = {'PHPSESSID': str(text).strip()}
        f.close()
        self.points = self.get_current_points()
        self.xsrf_token = self.get_xsrf_token()

    def check_if_already_entered(self, giveaway_code):
        conn = sqlite3.connect(self.sqlite_db_name)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM ENTRY WHERE CODE= (?)", (giveaway_code,))
        res = c.fetchone()[0] == 1
        conn.close()
        return res

    def add_an_entry(self, giveaway_code, giveaway_price, giveaway_link):
        conn = sqlite3.connect(self.sqlite_db_name)
        c = conn.cursor()
        name = giveaway_link.split('/')[3]
        c.execute("INSERT INTO ENTRY VALUES(?,?,?)", (giveaway_code, giveaway_price, name))
        conn.commit()
        conn.close()

    def get_xsrf_token(self):
        r = self.get('')
        soup = bs(r.text, 'html.parser')
        js_script = soup.find('script', {'type': 'text/javascript'})
        return re.search("', '\w*'", js_script.text).group()[4:-1]

    def get_current_points(self):
        r = self.get('')
        soup = bs(r.text, 'html.parser')
        return int(soup.find('span', {'class': 'nav__points'}).text)

    def get(self, path_url):
        time.sleep(self.time_to_sleep_between_each_request)
        return requests.get(self.base_url + path_url, headers=self.header_pages, cookies=self.cookie)

    def enter(self, giveaway_link, giveaway_code, giveaway_price):
        if not self.check_if_already_entered(giveaway_code):
            if giveaway_price <= self.points:
                time.sleep(self.time_to_sleep_between_each_request)
                payload = {'xsrf_token': self.xsrf_token,
                           'do': 'entry_insert', 'code': giveaway_code}
                header_entry = self.header_entry_template
                header_entry['Referer'] = self.base_url + giveaway_link
                r = requests.post(self.base_url + "/ajax.php",
                                  headers=header_entry, cookies=self.cookie, data=payload)
                if r.status_code == 200:
                    json_tmp = json.loads(r.text)
                    if json_tmp['type'] == 'success':
                        self.points = int(json_tmp['points'])
                        self.add_an_entry(giveaway_code, giveaway_price, giveaway_link)
                        logger.info('Adding entry : ' + giveaway_code)
                    else:
                        logger.warning('Not a succes for : ' + giveaway_code)
                else:
                    logger.warning('Failed with status_code : ' + str(r.status_code))
            else:
                logger.warning('Not enough points to enter : ' +
                      giveaway_link, ' / cost : ' + giveaway_price)
        else:
            logger.warning('Already Done for : ' + giveaway_code)
    def page_has_next(self, soup):
        tmp = soup.findAll('a')
        return len([x for x in tmp if x.has_attr('data-page-number')]) != 0

    def isLimitReached(self, value, list):
        if (value != -1):
            return value <= sum(c for (a, b, c) in list)
        else:
            return False

    def browser_pages(self, path_url, func, acc=[], page=1, limitPoint=-1):
        r = self.get(path_url + '&page=' + str(page))
        soup = bs(r.text, 'html.parser')
        acc = acc + func(soup)
        if (not self.isLimitReached(limitPoint, acc)) and self.page_has_next(soup):
            return self.browser_pages(path_url, func, acc=acc, page=(page + 1), limitPoint=limitPoint)
        else:
            return acc

    def findAllWishListedGiveaway(self, limitPoint=-1):
        def f(soup):
            page_heading = soup.find('div', {'class': 'page__heading'})
            soup_wishlist = page_heading.next_sibling.next_sibling
            div = soup_wishlist.find_all(
                'div', {'class': 'giveaway__row-outer-wrap'})
            return [(getLink(i), getCode(i), getPrice(i)) for i in div]
        return self.browser_pages('/giveaways/search?type=wishlist', f, limitPoint=limitPoint)

    def findAll50copies(self, limitPoint=-1):
        def f(soup):
            pinned = soup.find('div' , {'class' : 'pinned-giveaways__outer-wrap'})
            div = pinned.find_all(
                'div', {'class': 'giveaway__row-outer-wrap'})
            return [(getLink(i), getCode(i), getPrice(i)) for i in div]
        return self.browser_pages('/giveaways/search?q=SthNeverMatchHere', f, limitPoint=limitPoint)

    def findAllByName(self, name, limitPoint=-1):
        def f(soup):
            page_heading = soup.find('div', {'class': 'page__heading'})
            soup_wishlist = page_heading.next_sibling.next_sibling
            div = soup_wishlist.find_all(
                'div', {'class': 'giveaway__row-outer-wrap'})
            return [(getLink(i), getCode(i), getPrice(i)) for i in div]
        return self.browser_pages('/giveaways/search?q='+name, f, limitPoint=limitPoint)

    def findAllGiveaway(self, limitPoint=300):
        def f(soup):
            page_heading = soup.find('div', {'class': 'page__heading'})
            soup_wishlist = page_heading.next_sibling.next_sibling
            div = soup_wishlist.find_all(
                'div', {'class': 'giveaway__row-outer-wrap'})
            return [(getLink(i), getCode(i), getPrice(i)) for i in div]
        return self.browser_pages('/giveaways/search?', f, limitPoint=limitPoint)


    def doEntry(self, giveaways):
        self.points = self.get_current_points()
        for g in giveaways:
            self.enter(*g)

    def run(self):
        wishlist = self.findAllWishListedGiveaway()
        self.doEntry(wishlist)
        pinned = self.findAll50copies()
        self.doEntry(pinned)
