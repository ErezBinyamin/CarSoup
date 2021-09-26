#!/bin/bash

CarSoup() {
	local IMAGE_NAME=carsoup
		
	if echo "$@" | grep -q '\-\-build'
	then
		docker build -t ${IMAGE_NAME} .
	fi
	docker run -it ${IMAGE_NAME} python car.py $(echo $@ | grep -v '\-\-build')

}

CarSoup $@
