#!/usr/bin/env python
#coding=utf-8

import requests, time, json
from bs4 import BeautifulSoup
from aladin.helpers import toint
from db_conn import CollectionQueue, CollectionHistory, session, headers, Goods

s = requests.session()


class GetLulus():
    def __init__(self, url, category='', secondary_category=''):
        self.url = url
        self.pages_list = []
        self.site_name = 'Lulus'
        self.category = category
        self.second_category = secondary_category

        self.check_page()
        self.start_page()

    def requests_page(self, url, retry=0, max_retry=3):
        print url
        if retry > max_retry:
            return None

        try:
            r = s.get(url, headers=headers, timeout=60)
            # if r:
            #     print r
            # else:
            #     print '============'
            if r.status_code != 200:
                raise Exception("[Status Code Error] %s" % r.status_code)
            return r.text
        except Exception, e:
            print Exception
            print e
            print("[Requests Page Error] url:%s" % url)
            time.sleep(retry + 1)
            return self.requests_page(url, retry=retry + 1)

    def check_page(self):
        html_text = self.requests_page(self.url)
        # print html_text
        if not html_text:
            return
        soup = BeautifulSoup(html_text)
        page_list = soup.select("ul.cf a")
        # print page_list
        page_number = page_list[-2].text.strip() if page_list else 0  # max page number
        page_number = toint(page_number) + 1

        # for p in range(1, page_number):
        #     print p
        #
        #     url = 'http://www.lulus.com/categories/page' + '%d' + '-24/' % p
        #     print url

        # page_number = str(page_number)
        # print page_number
        # for p in page_number:
        #     print p
            # url = 'http://www.lulus.com/categories/page' + '%s' + '-24/' % p
            # print url
        for i in page_list:
            # print i
            link = i.attrs.get('href')
            print link
            url = 'http://www.lulus.com' + '%s' % link
            # print url
            self.pages_list.append(url)
        # for i in range (1, page_number):
        #     url =

    def start_page(self):
        for index, page in enumerate(self.pages_list):
            self.get_page(page, index + 1)

    def get_page(self, url, page_number):
        # print url
        html_text = self.requests_page(url)
        if not html_text:
            return
        soup = BeautifulSoup(html_text)
        product_list = soup.select("div.category-image")
        # print product_list
        for index, p in enumerate(product_list):
            rank = (page_number - 1) * 60 + index + 1
            print rank
            data_price = p.select("span.price")[-1]
            data_url = p.select("a")[0].attrs.get('href')
            true_data_url = 'http://www.lulus.com' + data_url
            # print true_data_url
            data_name = p.select("img")[0].attrs.get('alt')
            # print data_name
            img_url = p.select("img")[1].attrs.get('data-src')
            print img_url

            if not data_price or not data_name or not true_data_url:
                print("[Not Found] url:%s" % url)
                return

            find_queue = session.query(CollectionQueue).filter(CollectionQueue.site_name == 'Lulus') \
                .filter(CollectionQueue.url == true_data_url).first()
            print find_queue
            if not find_queue:
                cq = CollectionQueue()
                cq.site_name = self.site_name
                cq.add_time = int(time.time())
                cq.category = self.category
                cq.secondary_category = self.second_category
                cq.rank = rank
                cq.url = true_data_url
                cq.img_url = img_url
                session.add(cq)
                session.commit()
                print("added....")


url1 = 'http://www.lulus.com/categories/13_2402/vacation-dresses.html'
url2 = 'http://www.lulus.com/categories/299_2226/formal-dresses.html'
if __name__ == '__main__':
    g1 = GetLulus(url1, 'test', 'test2')
    g2 = GetLulus(url2, 'zzz', 'zzzz')
