.PHONY: all

all: pull render sync_s3

pull:
	python pull.py

render:
	python render.py

sync_s3:
	sh sync_s3.sh