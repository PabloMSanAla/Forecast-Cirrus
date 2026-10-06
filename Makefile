# Top-level Makefile for FORECAST

.PHONY: all clean docs html lc df dc igm create_image

all: lc df dc igm create_image

lc:
	$(MAKE) -C lc

df:
	$(MAKE) -C df

dc:
	$(MAKE) -C dc

igm:
	$(MAKE) -C igm

create_image:
	$(MAKE) -C postprocessing/create_image

docs: html

html:
	$(MAKE) -C docs html

clean:
	$(MAKE) -C lc clean
	$(MAKE) -C df clean
	$(MAKE) -C dc clean
	$(MAKE) -C igm clean
	$(MAKE) -C postprocessing/create_image clean
	$(MAKE) -C docs clean
