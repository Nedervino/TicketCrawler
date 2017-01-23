# -*- coding: utf-8 -*-
import scrapy
import time
from selenium import webdriver
import os
import threading
import random
import requests

#  TODO
#  - Implement url hashtable to prevent constant re-iterating of reserved links
#  - Proxy rotation using tor project / private proxy list instead of proxymesh
#  - remove multi-url structure, code cleanup
#  - Deploy on EC2, start scraping via lambda telegram bot

# scrapy crawl ticketswap -a url=https://www.ticketswap.nl/event/canto-ostinato-in-de-grote-zaal-tivolivredenburg/e9d0ac25-c408-479c-8b75-832c52466026


class TicketswapSpider(scrapy.Spider):
    name = "ticketswap"
    baseUrl = "https://www.ticketswap.nl"
    firstSoldTicketUrl = None
    # start_urls = ["https://www.ticketswap.nl/event/canto-ostinato-in-de-grote-zaal-tivolivredenburg/e9d0ac25-c408-479c-8b75-832c52466026"]
    successful = False
    ticketNumber = 0
    iteration = 0

    # telegram settings: https://www.codementor.io/garethdwyer/tutorials/building-a-telegram-bot-using-python-part-1-goi5fncay
    TOKEN = os.environ['telegram_token']
    telegramUrl = "https://api.telegram.org/bot{}/".format(TOKEN)
    chatId = 57249435

    custom_settings = {
        "DOWNLOAD_DELAY": 0.25
    }


    def __init__(self, url=' ', *args, **kwargs):
        self.start_urls = [url]
        super(TicketswapSpider, self).__init__(*args, **kwargs)
        # self.browser = webdriver.PhantomJS()  # headless testing
        # driver.set_window_size(1024, 768)     # optional
        self.browser = webdriver.Chrome()
        self.browser.get('https://www.ticketswap.nl')
        self.browser.find_element_by_link_text('Inloggen').click()

        for handle in self.browser.window_handles:
            self.browser.switch_to_window(handle)
        # self.browser.implicitly_wait(1)  # TODO: necessary?
        inputElement = self.browser.find_element_by_name("email")
        # inputElement.clear() causing InvalidElementStateException
        inputElement.send_keys(os.environ['fb_email'])
        inputElement = self.browser.find_element_by_name("pass")
        # inputElement.clear() causing InvalidElementStateException
        inputElement.send_keys(os.environ['fb_password'])
        self.browser.find_element_by_name('login').click()

        for handle in self.browser.window_handles:
            self.browser.switch_to_window(handle)


    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(url=url, callback=self.visitFirstSoldTicket, dont_filter=True)
            yield request
            # yield scrapy.Request('http://checkip.dyndns.org/', callback=self.check_ip)   # enable to check proxy per request


    def check_ip(self, response):
        pub_ip = response.xpath('//body/text()').re('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')[0]
        print "My public IP is: " + pub_ip


        # /html/body/div[4]/div/section[1]/div[1]/article[1]

    # No random captcha's when crawling via this page
    def visitFirstSoldTicket(self, response):
        if 'Aangeboden' in response.xpath('//section[1]/h2').extract_first():
            self.firstSoldTicketUrl = self.baseUrl + response.xpath('//section[2]/div/article/div[1]/h3/a/@href').extract_first()
        elif 'Verkocht' in response.xpath('//section[1]/h2').extract_first():
            self.firstSoldTicketUrl = self.baseUrl + response.xpath('//section[1]/div/article/div[1]/h3/a/@href').extract_first()
        print 'Opening first sold ticket link: ' + self.firstSoldTicketUrl
        request = scrapy.Request(url=self.firstSoldTicketUrl, callback=self.parse, dont_filter=True)
        yield request


    def sendTelegramMessage(self, text):
        print 'Notifying via Telegram'
        url = self.telegramUrl + "sendMessage?text={}&chat_id={}".format(text, self.chatId)
        r = requests.get(url)
        print r.status_code

    def parse(self, response):
        self.iteration += 1
        print 'Parsing. Successful iteration ' + str(self.iteration)
        # print response.request.headers['User-Agent']
        # print response.request.headers
        # print response.headers

        if ('Plaats een oproep' in response.body) or self.iteration < 7:
            sleepDuration = random.uniform(1.1, 2.0)  # (0.6, 1.1)
            print 'No tickets offered. Sleeping for ' + str(sleepDuration)
            time.sleep(sleepDuration)
            yield scrapy.Request(url=self.firstSoldTicketUrl, callback=self.parse, dont_filter=True)
        elif 'Oeps, iets te vaak vernieuwd' in response.body:
            self.iteration = 0
            # self.botAlert(response)
            text = "Crawled too often."
            self.sendTelegramMessage(text)
            print text
            self.browser.get(self.start_urls[0])
            raw_input('Press ENTER to continue')
            yield scrapy.Request(url=self.firstSoldTicketUrl, callback=self.parse, dont_filter=True)
        else:
            self.iteration = 0
            print 'Tickets found'
            self.browser.get(response.url)
            ticketArray = response.xpath('//body/div[3]/div/div[2]/article')  # Old xpath '//body/div[3]/div/div[2]/article' was changed
            if not ticketArray:
                print 'No tickets found for current xpath'
            for ticket in ticketArray:
                if self.successful:
                    break
                ticketUrl = ticket.xpath('div[1]/h3/a/@href').extract_first()
                url = self.baseUrl + ticketUrl
                print 'Trying ticketlink: ' + url
                # yield scrapy.Request(url, callback=self.buyTicket, dont_filter=True)
                

                # TODO: function call
                os.system('say "Ticket found"')
                self.browser.get(url)
                if 'Koop e-ticket' not in self.browser.page_source:
                    print 'Tickets are already reserved by someone else'
                    # with open('lastCrawl.html', 'wb') as F:
                    #     F.write()
                    yield scrapy.Request(self.firstSoldTicketUrl, callback=self.parse, dont_filter=True)
                else:
                    self.browser.find_element_by_class_name("btn-buy").click()
                    time.sleep(2)
                    if 'Pay with iDEAL' in self.browser.page_source:
                        print 'Reserved tickets'
                        os.system('say "Ticket placed in cart"')
                        text = "Reserved ticket. Visit https://www.ticketswap.nl/cart to complete payment."
                        self.sendTelegramMessage(text)
                        self.successful = True
                    elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                        print 'Error during Facebook login'
                    else:
                        text = 'Something went wrong in Selenium'
                        self.sendTelegramMessage(text)
                        print text
                        self.browser.save_screenshot('errorScreenshot.png')
                        yield scrapy.Request(self.firstSoldTicketUrl, callback=self.parse, dont_filter=True)




                break   # TODO: rewrite for-yield


    def buyTicket(self, response):
        if self.successful:
            return
        self.ticketNumber += 1
        print 'Ticket request number ' + str(self.ticketNumber)
        if 'Oeps, iets te vaak vernieuwd' in response.body:
            self.botAlert(response)
        elif 'Koop e-ticket' not in response.body:
            print 'Tickets are already reserved by someone else'


            yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        else:
            print 'Tickets still available. Opening browser'
            os.system('say "Ticket found"')
            self.browser.get(response.url)
            self.browser.find_element_by_class_name("btn-buy").click()
            time.sleep(2)

            if 'Pay with iDEAL' in self.browser.page_source:
                print 'Reserved tickets'
                os.system('say "Ticket placed in cart"')
                self.successful = True
                # self.setInterval(self.notifyUser, 4)
                # subprocess.call(["./tg.sh"], shell=True)
                # while 1:
                #     os.system('say "Ticket found"')
                #     time.sleep(4)
            elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                print 'Error during Facebook login'
                yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
            else:
                print 'Something went wrong in Selenium'


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
            print 'Tickets are already reserved by someone else'
            # with open('lastCrawl.html', 'wb') as F:
            #     F.write()
            yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)
        else:
            self.browser.find_element_by_class_name("btn-buy").click()
            time.sleep(2)
            if 'Pay with iDEAL' in self.browser.page_source:
                print 'Reserved ticket'
                os.system('say "Ticket placed in cart"')
                self.successful = True
                # self.setInterval(self.notifyUser, 4)
                # subprocess.call(["./tg.sh"], shell=True)
                # while 1:
                #     os.system('say "Ticket found"')
                #     time.sleep(4)
            elif 'Je hebt ons geen toegang gegeven tot je Facebook account' in self.browser.page_source:
                print 'Error during Facebook login'
            else:
                print 'Something went wrong in Selenium'
                self.browser.save_screenshot('errorScreenshot.png')
                yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)


    def botAlert(self, response):
        print 'Bot alert. Opening browser to complete Captcha'
        # os.system('say "Crawled too often"')
        # with open('lastCrawl.html', 'wb') as F:
        #     F.write(response.body)
        self.browser.get(self.start_urls[0])
        raw_input('Press ENTER to continue')
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)



    def notifyUser(self):
        # os.system('say "Ticket found"')
        print 'Ticket found'


    def setInterval(self, func, sec):
        def funcWrapper():
            self.setInterval(func, sec)
            func()
        t = threading.Timer(sec, funcWrapper)
        t.start()
        return t
