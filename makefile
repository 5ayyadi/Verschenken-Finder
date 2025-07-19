up:
	docker-compose up --build

up-detached:
	docker-compose up -d

purge:
	docker rm -f $$(docker ps -a -q)
[update-pip]:
	python3 -m pip install --upgrade pip

[update-req]:
	pip freeze > requirements.txt

[update-all]:
	make update-pip
	make update-req
	docker rmi -f $$(docker images -q)