PYTHON_VER?=3.12
NETBOX_VER?=v4.3.3


COMPOSE_FILE=./develop/docker-compose.yml
BUILD_NAME=plugsbox
VERFILE=./plugsbox/version.py


cbuild:
	docker compose -f ${COMPOSE_FILE} \
		-p ${BUILD_NAME} build \
		--build-arg netbox_ver=${NETBOX_VER} \
		--build-arg python_ver=${PYTHON_VER}

debug:
	@echo "Starting Netbox .. "
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up

start:
	@echo "Starting Netbox in detached mode.. "
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d

stop:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down

destroy:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down -v
	#docker volume rm -f ${BUILD_NAME}_pgdata_aputils

nbshell:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py nbshell

shell:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py shell

adduser:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py createsuperuser

collectstatic:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} run netbox python manage.py collectstatic

migrations:
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} up -d postgres
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} \
	run netbox python manage.py makemigrations ${BUILD_NAME}
	docker compose -f ${COMPOSE_FILE} -p ${BUILD_NAME} down


pbuild:
	python3 -m pip install --upgrade build
	python3 -m build

pypipub:
	python3 -m pip install --user --upgrade twine
	python3 -m twine upload dist/*
