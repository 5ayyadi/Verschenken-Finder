up:
	docker-compose up --build

up-detached:
	docker-compose up -d

purge:
	docker rm -f $$(docker ps -a -q)
	docker rmi -f $$(docker images -q)