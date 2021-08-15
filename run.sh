#!/bin/bash

CarSoup() {
	local IMAGE_NAME=carsoup
	local SRC=app/car.py

	IMG_TIME=0
	docker image ls | grep -q ${IMAGE_NAME} && IMG_TIME=$( date -d $(docker inspect -f '{{ .Created }}' ${IMAGE_NAME}) +%s)
	DFILE_TIME=$( date -r Dockerfile +%s )
	SRC_TIME=$( date -r ${SRC} +%s )

	if [ $DFILE_TIME -gt $IMG_TIME ] 
	then
		docker build -t ${IMAGE_NAME} .
	elif [ $SRC_TIME -gt $IMG_TIME ] && git status -s | grep -iqm1 -e " M" -e " D" -e "??" 
		docker build -t ${IMAGE_NAME} .
	fi

	docker run -it ${IMAGE_NAME} python car.py $@
}

CarSoup $@
