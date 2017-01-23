#!/bin/bash 
iteration=0
SECONDS=0
tabOpen=false

while true
do 
	((iteration++))
    printf "\nExecuting run number %d\n" $iteration
    scrapy crawl singleRun | tee out.log
    printf "\nRun $iteration\n" $iteration >> total.log
    cat out.log >> total.log
    errorCode=${PIPESTATUS[0]}
    if grep -q "Press ENTER to continue" out.log; then
    	interval=$SECONDS
    	printf "\nFailed run number %d after $(($interval / 60)) minutes and $(($interval % 60)) seconds, starting over\n" $iteration
    	echo "$(($interval / 60)) minutes and $(($interval % 60)) seconds" >> total.log
    	if [ "$tabOpen" = false ]; then
    		# open <url_to_event_page>
    		echo "$(($interval / 60)) minutes and $(($interval % 60)) seconds" >> intervals.log
    		tabOpen=true
    	fi
    	# sleep 120
    	iteration=0
    	SECONDS=0
    else
    	tabOpen=false
    fi
    if [[ "$iteration" -gt 20 ]]; then
    	# duration=120
    	duration=$[ ( $RANDOM % 3 )  + 2 ]	# TODO
    else
    	duration=$[ ( $RANDOM % 3 )  + 2 ]  # TODO
    fi
    printf "\nEnding run number %d with exit code %d. Sleeping for %d seconds\n" $iteration $errorCode $duration
    sleep "$duration"
done