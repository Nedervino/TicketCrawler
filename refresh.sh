HOST=https://www.ticketswap.nl/
FISSA=https://www.ticketswap.nl/listing/awakenings-early-new-years-special/998303/39db47efab

rm log
touch log

while :
do

	CookieFileName=cookies.txt
	curl --cookie  $CookieFileName --cookie-jar $CookieFileName \
	-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36' \
	-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'cache-control: max-age=0' \
	GET $HOST -v

	curl -s --cookie cookies.txt \
	-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36' \
	-H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'cache-control: max-age=0' \
	-X GET $FISSA | grep 'andere tickets' >> log
	
	echo $(date) >> log

	sleep 1

done