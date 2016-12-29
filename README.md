#Ticket scraper

This spider, written using the python scrapy framework, periodically crawls a popular dutch ticket trading website to check for available tickets and immediately order them once found. The website uses reCaptcha to prevent refreshing more than a couple of times per minute. To bypass this system, the spider uses a combination of proxy rotation and user agent rotation. Each consecutive request is routed past a different proxy IP using one out of the 90 most commonly found user agent strings. The bot uses Selenium webdriver to log in using facebook, and perform the interaction with the ticket buying page which contains dynamic content.

<br>

####Installation
The scraper uses Scrapy and Selenium for Python, both of which need to be installed on the system prior to running the code
To install Scrapy, see <https://doc.scrapy.org/en/latest/intro/install.html>
To install Selenium for Python, see <https://selenium-python.readthedocs.io/installation.html>
Run the following to complete the installation
```
pip install scrapy-random-useragent
```


####Configuration
The script rotates proxies via the proxymesh service. You can get a free 1 month trial on <https://proxymesh.com>. After you've registered, visit <https://proxymesh.com/account/dashboard/> and choose an authorized host. Combining this with your login credits gives you the string needed for the spider, in the following form:
<username>:<password>@<country>.proxymesh.com:<port>

This string, along with your facebook login credentials, need to be stored as environment variables before running the script. The following three environment variables need to be set: http_proxy, fb_email, and fb_password.
To set these on a unix system, the following three lines can be executed in your terminal or stored in your .bash_profile/.bashrc. Make sure to restart your terminal before running the script.

```
export http_proxy=<username>:<password>@fr.proxymesh.com:<port>
export fb_email=<facebook_email>
export fb_password=<facebook_password>
```


####Execution
The project contains two spiders, located in the ticketswapSpider/spiders directory. spider2 is the working version, and can be started by running the following command from the root:
```
scrapy crawl spider2 -a url=<url_to_first_sold_event_ticket>
```







Set your http_proxy environment variable to the proxy address
For example, on a unix system for a french proxyrotation server
export http_proxy=<username>:<password>@fr.proxymesh.com:<port>

A list of the most common user agent strings is included in useragentsMostCommon.txt, and on each request a random user agent is chosen from this list