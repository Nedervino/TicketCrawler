# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import signal
import os
import threading
# import subprocess

#  TODO
#  - Implement url hashtable to prevent constant re-iterating of reserved links
#  - Proxy rotation
#  - User agent rotation
#  - Loop every 12 seconds
#  - Don't call all parse methods


class TicketswapSpider(scrapy.Spider):
    name = "ticketswap"
    baseUrl = "http://www.ticketswap.nl"
    # start_urls = ["https://www.ticketswap.nl/event/drake-the-boy-meets-world-tour/floor/5ac0bb61-c5f4-4c58-9567-4da2d9cc439d/30473"]
    successful = False
    ticketNumber = 0

    def __init__(self, *a, **kw):
        super(TicketswapSpider, self).__init__(*a, **kw)
        print 'initialized'
        self.browser = webdriver.Chrome()
        # self.browser = webdriver.PhantomJS() #headless testing

    def start_requests(self):
        urls = ["https://www.ticketswap.nl/event/drake-the-boy-meets-world-tour/floor/5ac0bb61-c5f4-4c58-9567-4da2d9cc439d/30473"]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if 'Aangeboden' not in response.xpath('//section[1]/h2/text()').extract():
            if 'Oeps, iets te vaak vernieuwd' in response.body:
                self.botAlert(response)
            else:
                print 'Geen tickets aangeboden op dit moment'
        else:
            print 'Kaartjes aangeboden'
            for ticket in response.xpath('//section[1]/div/article'):
                if self.successful:
                    break
                ticketUrl = ticket.xpath('div[1]/h3/a/@href').extract_first()  # ticket.extract().xpath('div[0]/h3/a').extract()
                url = self.baseUrl + ticketUrl
                print 'Trying ticketlink: ' + url
                yield scrapy.Request(url, callback=self.buyTicket)
                break   # TODO: remove


    def buyTicket(self, response):
        if self.successful:
            return
        self.ticketNumber += 1
        print 'Ticket request number ' + str(self.ticketNumber)
        if False: #  'Iemand anders' in response.body or 'Helaas! deze tickets zijn' in response.body or 'verwijderd' in response.body:
            print 'Tickets zijn al bezet'
            with open('lastCrawl.html', 'wb') as F:
                F.write(response.body)
        elif 'Oeps, iets te vaak vernieuwd' in response.body:
            self.botAlert(response)
        else:
            print 'Tickets nog beschikbaar. Browser wordt geopend'
            # self.browser.get(response.url)
            # self.browser.find_element_by_link_text('Inloggen').click()
            self.browser.get(response.url)
            self.browser.save_screenshot('ticketswap.png')
            self.browser.implicitly_wait(5)
            self.browser.find_element_by_class_name("btn-buy").click()
            # self.browser.find_element_by_link_text('Koop e-ticket').click()

            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
            self.browser.save_screenshot('facebook.png')
            inputElement = self.browser.find_element_by_name("email")  # self.browser.find_element_by_class_name("inputtext")
            inputElement.clear()
            inputElement.send_keys('tim.nederveen@hotmail.com')
            inputElement = self.browser.find_element_by_name("pass")  # self.browser.find_element_by_class_name("inputpassword")
            inputElement.clear()
            inputElement.send_keys('mijzelfnatuurlijk')
            self.browser.save_screenshot('facebook2.png')
            self.browser.find_element_by_name('login').click()

            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
            time.sleep(10)
            self.browser.save_screenshot('ticketswap2.png')

            # if "Bestelling afronden" in self.driver.page_source:
            if 'Bestelling afronden' in self.browser.page_source:
                print 'Gereserveerd'
                self.successful = True
                self.setInterval(self.notifyUser, 4)
                # subprocess.call(["./tg.sh"], shell=True)
                # while 1:
                #     os.system('say "Ticket found"')
                #     time.sleep(4)

                # open https://www.ticketswap.nl/cart
            elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                print 'Error tijdens Facebook login'
            else:
                print 'Er ging iets fout in Selenium'


    def botAlert(self, response):
        print 'Te vaak gecrawled'
        # print "Start : %s" % time.ctime()
        # time.sleep(1)
        # print "End : %s" % time.ctime()
        with open('lastCrawl.html', 'wb') as F:
            F.write(response.body)
        self.browser.get(response.url)
        input('Press ENTER to continue')
        # time.sleep(10)
        # while True:
        #     time.sleep(1)


    def notifyUser():
        # os.system('say "Ticket found"')
        print 'ticket found'


    def setInterval(self, func, sec):
        def funcWrapper():
            self.setInterval(func, sec)
            func()
        t = threading.Timer(sec, funcWrapper)
        t.start()
        return t

    # def gracefulExit(self,signum, frame):
    #       self.kill_now = True


        # CORRECT
        # response.xpath('//section[1]/div/article').extract_first()
        # response.xpath('/html/body/div[4]/div/section[1]/div/article').extract_first()
        # response.xpath('//section[1]/h2').extract_first() == <h2>Aangeboden</h2> anders geen tickets aangeboden

        # OLD
        # Xpath & css selectors. Cutoff at article for item iteration, use rest of path for retrieving url
        # body > div.l-content > div > section:nth-child(3) > div > article > div.listings-item--title > h3 > a
        # /html/body/div[4]/div/section[1]/div/article/div[1]/h3/a
