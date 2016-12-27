# -*- coding: utf-8 -*-
import scrapy
import time
# import os
# import subprocess


class TicketswapSpider(scrapy.Spider):
    name = "ticketswap"
    baseUrl = "http://www.ticketswap.nl"
    start_urls = ["https://www.ticketswap.nl/event/dgtl-amsterdam-2017/saturday/57830a0c-8095-4f66-90e7-763ff961b894/57560"]
    successful = False

    def parse(self, response):
        if 'Aangeboden' not in response.xpath('//section[1]/h2/text()').extract():
            if 'Oeps, iets te vaak vernieuwd' in response.body:
                print 'Te vaak gecrawled'
                print "Start : %s" % time.ctime()
                time.sleep(1)
                print "End : %s" % time.ctime()
                with open('lastCrawl.html', 'wb') as F:
                    F.write(response.body)
            else:
                print 'Geen tickets aangeboden op dit moment'
        else:
            print 'Kaartjes aangeboden'
            for ticket in response.xpath('//section[1]/div/article'):
                if self.successful:
                    break
                print 'hi'
                ticketUrl = ticket.xpath('div[1]/h3/a/@href').extract_first()  # ticket.extract().xpath('div[0]/h3/a').extract()
                url = self.baseUrl + ticketUrl
                print 'Ticket link: ' + url
                yield scrapy.Request(url, callback=self.buyTicket)

    def buyTicket(self, response):
        self.logger.info("Visited %s", response.url)
        # subprocess.call(["./tg.sh"], shell=True)
        # while 1:
        #   os.system('say "Ticket found"')
        #   time.sleep(4)
        # open https://www.ticketswap.nl/cart

        if False:
            self.successful = True




        # CORRECT
        # response.xpath('//section[1]/div/article').extract_first()
        # response.xpath('/html/body/div[4]/div/section[1]/div/article').extract_first()
        # response.xpath('//section[1]/h2').extract_first() == <h2>Aangeboden</h2> anders geen tickets aangeboden

        # OLD
        # Xpath & css selectors. Cutoff at article for item iteration, use rest of path for retrieving url
        # body > div.l-content > div > section:nth-child(3) > div > article > div.listings-item--title > h3 > a
        # /html/body/div[4]/div/section[1]/div/article/div[1]/h3/a
