IMAGE_NAME=carsoup

.PHONY: all
all: .image_build

.image_build: Dockerfile app/car.py app/requirements.txt
	docker build -t $(IMAGE_NAME) .
	touch .image_build
