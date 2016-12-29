# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import os
import threading
import random
import sys
# import subprocess

#  TODO
#  - Implement url hashtable to prevent constant re-iterating of reserved links
#  - Proxy rotation using tor project / private proxy list instead of proxymesh
#  - Loop within python script instead of in bash script: https://doc.scrapy.org/en/latest/topics/practices.html run script from within python script
#  - remove multi-url structure, code cleanup
#  - Open browser and login before start of loop, needs all bash functionality rewritten within python


class Spider2Spider(scrapy.Spider):
    name = "spider2"
    baseUrl = "http://www.ticketswap.nl"
    # start_urls = ["https://www.ticketswap.nl/event/next-mondays-hangover-fck-nye/6911a50c-58c3-45bf-9578-83253fdb40bd"]  # ["https://www.ticketswap.nl/event/robbie-williams-the-heavy-entertainment-show/floor/de997992-367e-4eb4-b873-bffe7b253102/48520"]  #  ["https://www.ticketswap.nl/event/next-mondays-hangover-fck-nye/6911a50c-58c3-45bf-9578-83253fdb40bd"]
    # start_urls = ["https://www.ticketswap.nl/listing/awakenings-early-new-years-special/998303/39db47efab"]
    # start_urls = ["https://www.ticketswap.nl/listing/next-mondays-hangover-fck-nye/999132/f3720ea5b0"]
    successful = False
    ticketNumber = 0
    iteration = 0
    # ticketList = []

    custom_settings = {
        "DOWNLOAD_DELAY": 0.25
    }

    def __init__(self, url=' ',*args, **kwargs):
        urlVariable = url
        print urlVariable
        self.start_urls = [urlVariable]
        super(Spider2Spider, self).__init__(*args, **kwargs)
        # self.browser = webdriver.PhantomJS() #headless testing
        self.browser = webdriver.Chrome()
        self.browser.get('https://www.ticketswap.nl')
        self.browser.find_element_by_link_text('Inloggen').click()

        for handle in self.browser.window_handles:
            self.browser.switch_to_window(handle)
        self.browser.save_screenshot('facebook.png')
        inputElement = self.browser.find_element_by_name("email")
        inputElement.clear()
        inputElement.send_keys(os.environ['fb_email'])
        inputElement = self.browser.find_element_by_name("pass")
        inputElement.clear()
        inputElement.send_keys(os.environ['fb_password'])
        self.browser.save_screenshot('facebook2.png')
        self.browser.find_element_by_name('login').click()

        for handle in self.browser.window_handles:
            self.browser.switch_to_window(handle)


    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield request
            # yield scrapy.Request('http://checkip.dyndns.org/', callback=self.check_ip)

    def check_ip(self, response):
        pub_ip = response.xpath('//body/text()').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')[0]
        print "My public IP is: " + pub_ip


    def parse(self, response):
        self.iteration += 1
        print 'Parsing. Successful iteration ' + str(self.iteration)
        # print response.request.headers['User-Agent']
        # print response.request.headers
        # print response.headers
        # del self.ticketList[:]

        if 'Plaats een oproep' in response.body:
            print 'Geen tickets aangeboden op dit moment'
            sleepDuration = random.uniform(0.6, 1.1)
            print 'Sleeping for ' + str(sleepDuration)
            time.sleep(sleepDuration)
            yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)
        elif 'Oeps, iets te vaak vernieuwd' in response.body:
            self.iteration = 0
            # self.botAlert(response)
            print 'Te vaak gecrawled'
            self.browser.get(self.start_urls[0])
            raw_input('Press ENTER to continue')
            yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)
        else:
            self.iteration = 0
            print 'Kaartjes aangeboden'
            for ticket in response.xpath('//body/div[4]/div/div[2]/article'):  # response.xpath('//body/div[3]/div/div[2]/article'):
                if self.successful:
                    break
                ticketUrl = ticket.xpath('div[1]/h3/a/@href').extract_first()  # ticket.extract().xpath('div[0]/h3/a').extract()
                url = self.baseUrl + ticketUrl
                print 'Trying ticketlink: ' + url
                # yield scrapy.Request(url, callback=self.buyTicket, dont_filter=True)
                

                # TODO: function call

                os.system('say "Ticket found"')
                self.browser.get(url)
                if 'Koop e-ticket' not in self.browser.page_source:
                    print 'Tickets zijn al bezet'
                    self.browser.save_screenshot('ticketswap2.png')
                    # with open('lastCrawl.html', 'wb') as F:
                    #     F.write()
                    yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
                else:
                    self.browser.find_element_by_class_name("btn-buy").click()
                    time.sleep(2)
                    if 'Bestelling afronden' in self.browser.page_source:
                        print 'Gereserveerd'
                        os.system('say "Ticket placed in cart"')
                        self.successful = True
                        # self.setInterval(self.notifyUser, 4)
                        # subprocess.call(["./tg.sh"], shell=True)
                        # while 1:
                        #     os.system('say "Ticket found"')
                        #     time.sleep(4)
                    elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                        print 'Error tijdens Facebook login'
                    else:
                        print 'Er ging iets fout in Selenium'
                        self.browser.save_screenshot('ticketswap2.png')
                        yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)






                break   # TODO: remove


    def buyTicket(self, response):
        if self.successful:
            return
        self.ticketNumber += 1
        print 'Ticket request number ' + str(self.ticketNumber)
        if 'Oeps, iets te vaak vernieuwd' in response.body:
            self.botAlert(response)
        elif 'Koop e-ticket' not in response.body:
            print 'Tickets zijn al bezet'


            yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        else:
            print 'Tickets nog beschikbaar. Browser wordt geopend'
            os.system('say "Ticket found"')
            self.browser.get(response.url)
            self.browser.find_element_by_class_name("btn-buy").click()
            time.sleep(2)
            # self.browser.save_screenshot('ticketswap2.png')

            if 'Bestelling afronden' in self.browser.page_source:
                print 'Gereserveerd'
                os.system('say "Ticket placed in cart"')
                self.successful = True
                # self.setInterval(self.notifyUser, 4)
                # subprocess.call(["./tg.sh"], shell=True)
                # while 1:
                #     os.system('say "Ticket found"')
                #     time.sleep(4)
            elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                print 'Error tijdens Facebook login'
            else:
                print 'Er ging iets fout in Selenium'


    def buyTicket2(self, url):
        if self.successful:
            return
        self.ticketNumber += 1
        print 'Ticket request number ' + str(self.ticketNumber)
        # if 'Oeps, iets te vaak vernieuwd' in response.body:
        #     self.botAlert(response)
        # # elif 'Koop e-ticket' not in response.body:
        #     print 'Tickets zijn al bezet'

        #     with open('lastCrawl.html', 'wb') as F:
        #         F.write(response.body)
        #     yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        # print 'Tickets nog beschikbaar. Browser wordt geopend'
        os.system('say "Ticket found"')
        self.browser.get(url)
        if 'Koop e-ticket' not in self.browser.page_source:
            print 'Tickets zijn al bezet'
            self.browser.save_screenshot('ticketswap2.png')
            # with open('lastCrawl.html', 'wb') as F:
            #     F.write()
            yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        else:
            self.browser.find_element_by_class_name("btn-buy").click()
            time.sleep(2)
            if 'Bestelling afronden' in self.browser.page_source:
                print 'Gereserveerd'
                os.system('say "Ticket placed in cart"')
                self.successful = True
                # self.setInterval(self.notifyUser, 4)
                # subprocess.call(["./tg.sh"], shell=True)
                # while 1:
                #     os.system('say "Ticket found"')
                #     time.sleep(4)
            elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                print 'Error tijdens Facebook login'
            else:
                print 'Er ging iets fout in Selenium'
                self.browser.save_screenshot('ticketswap2.png')
                yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)


    def botAlert(self, response):
        print 'botAlert'
        # os.system('say "Crawled too often"')
        # print "Start : %s" % time.ctime()
        # time.sleep(1)
        # print "End : %s" % time.ctime()
        # with open('lastCrawl.html', 'wb') as F:
        #     F.write(response.body)

        # self.browser = webdriver.Chrome()
        self.browser.get(self.start_urls[0])
        raw_input('Press ENTER to continue')
        # print 'Press ENTER to continue'
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)



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


        # CORRECT
        # response.xpath('//section[1]/div/article').extract_first()
        # response.xpath('/html/body/div[4]/div/section[1]/div/article').extract_first()
        # response.xpath('//section[1]/h2').extract_first() == <h2>Aangeboden</h2> anders geen tickets aangeboden

        # OLD
        # Xpath & css selectors. Cutoff at article for item iteration, use rest of path for retrieving url
        # body > div.l-content > div > section:nth-child(3) > div > article > div.listings-item--title > h3 > a
        # /html/body/div[4]/div/section[1]/div/article/div[1]/h3/a
