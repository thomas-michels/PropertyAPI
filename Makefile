include ./.env

build:
	docker build -t property-api --no-cache .

run:
	docker run --env-file .env --network ${DEV_CONTAINER_NETWORK} -p ${APPLICATION_PORT}:8000 --name property-api -d property-api
