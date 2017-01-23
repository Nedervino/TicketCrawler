# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import os
import threading
# import subprocess

#  TODO
#  - Implement url hashtable to prevent constant re-iterating of reserved links
#  - Proxy rotation using tor project / private proxy list instead of proxymesh
#  - Loop within python script instead of in bash script: https://doc.scrapy.org/en/latest/topics/practices.html run script from within python script
#  - remove multi-url structure, code cleanup
#  - Open browser and login before start of loop, needs all bash functionality rewritten within python


class singleRunSpider(scrapy.Spider):
    name = "singleRun"
    baseUrl = os.environ['ticket_site']
    start_urls = ["https://www.ticketswap.nl/event/canto-ostinato-in-de-grote-zaal-tivolivredenburg/e9d0ac25-c408-479c-8b75-832c52466026"]
    successful = False
    ticketNumber = 0
    ticketList = []

    def __init__(self, *a, **kw):
        super(singleRunSpider, self).__init__(*a, **kw)
        # self.browser = webdriver.Chrome()
        # self.browser = webdriver.PhantomJS() #headless testing

    def start_requests(self):
        # self.setInterval(self.loop, 12)
        for url in self.start_urls:
            request = scrapy.Request(url=url, callback=self.parse)
            # print 'Request headers:'
            # print request.headers
            yield request
            # yield scrapy.Request('http://checkip.dyndns.org/', callback=self.check_ip)

    # def loop(self):
    #     url = self.start_urls[0]
    #     return scrapy.Request(url=url, callback=self.parse)

    def check_ip(self, response):
        pub_ip = response.xpath('//body/text()').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')[0]
        print "My public IP is: " + pub_ip

    def parse(self, response):
        print 'parsing'
        # print response.request.headers['User-Agent']
        # print response.request.headers
        print response.headers
        # del self.ticketList[:]


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
        # if 'Iemand anders' in response.body or 'Helaas! deze tickets zijn' in response.body or 'verwijderd' in response.body:
        #     if 'Iemand anders' in response.body:
        #         print 'a'
        #     print 'Tickets zijn al bezet'
        #     with open('lastCrawl.html', 'wb') as F:
        #         F.write(response.body)
        if 'Oeps, iets te vaak vernieuwd' in response.body:
            self.botAlert(response)
        elif 'Koop e-ticket' not in response.body:
            print 'Tickets zijn al bezet'
            with open('lastCrawl.html', 'wb') as F:
                F.write(response.body)
        else:
            print 'Tickets nog beschikbaar. Browser wordt geopend'
            os.system('say "Ticket found"')
            self.browser = webdriver.Chrome()
            # self.browser.get(response.url)
            # self.browser.find_element_by_link_text('Inloggen').click()
            
            self.browser.get(response.url)
            self.browser.implicitly_wait(2)
            self.browser.find_element_by_class_name("btn-buy").click()

            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
            self.browser.save_screenshot('facebook.png')
            inputElement = self.browser.find_element_by_name("email")  # self.browser.find_element_by_class_name("inputtext")
            inputElement.clear()
            inputElement.send_keys(os.environ['fb_email'])
            inputElement = self.browser.find_element_by_name("pass")  # self.browser.find_element_by_class_name("inputpassword")
            inputElement.clear()
            inputElement.send_keys(os.environ['fb_password'])
            self.browser.save_screenshot('facebook2.png')
            self.browser.find_element_by_name('login').click()

            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
            time.sleep(7)

            # if "Bestelling afronden" in self.driver.page_source:
            if 'Bestelling afronden' in self.browser.page_source:
                print 'Gereserveerd'
                os.system('say "Ticket placed in cart"')
                self.successful = True
                # self.setInterval(self.notifyUser, 4)
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
        # os.system('say "Crawled too often"')
        # print "Start : %s" % time.ctime()
        # time.sleep(1)
        # print "End : %s" % time.ctime()
        with open('lastCrawl.html', 'wb') as F:
            F.write(response.body)

        # self.browser = webdriver.Chrome()
        # self.browser.get(response.url)
        # raw_input('Press ENTER to continue')
        print 'Press ENTER to continue'


    def notifyUser(self):
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
