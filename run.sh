#!/bin/bash

CarSoup() {
	local IMAGE_NAME=carsoup
	make
	docker run -it ${IMAGE_NAME} python car.py $(echo $@ | grep -v '\-\-build')
}

CarSoup $@
