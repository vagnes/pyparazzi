#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup
import logging
import os
import requests
import re
import random
import sys

# CLI setup

parser = argparse.ArgumentParser(
        description="Pyparazzi CLI")
parser.add_argument(
	"-d", "--domain", metavar="str", type=str, default=None,
	help="Domain to start the search.")
parser.add_argument(
	"-s", "--sitemap", action="store_true",
	help="Search through sitemap. Specify sitemap with -d/--domain.")
parser.add_argument(
	"-o", "--output", metavar="str", type=str,
	help="Name of output file.")
parser.add_argument(
	"--database", metavar="str", type=str, default="std_database.txt",
	help="Name of non-standard database.")
parser.add_argument(
	"--log", action="store_true",
	help="Enable logging.")
parser.add_argument(
	"-f", "--file", metavar="str", type=str,
	help="Import url from file to scan")

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

# Give args/input proper var names

sDomain = args.domain
sOutput = args.output
sDatabase = args.database
sFile_with_urls = args.file
bLogging = args.log
bSitemap = args.sitemap

# Enable logging

if bLogging:
	logging.basicConfig(filename=str(sOutput)+".log", level=logging.DEBUG,
	format="%(asctime)s - %(levelname)s %(module)s - %(funcName)s: %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S")

# Init containers

lLink_container = []
lOutput_container = []
lDomain_container = []

# Functions

def site_data(sDomain):

	# Request domain data

	try:
		r = requests.get(sDomain)
	except requests.exceptions.MissingSchema:
		sDomain = "https://" + sDomain
		r = requests.get(sDomain)
		logging.info("Argument missing https prefix.")
	except requests.exceptions.MissingSchema:
		sDomain = "http://" + sDomain
		r = requests.get(sDomain)
		logging.info("Argumet missing http prefix.")
	
	# Parse data

	bs4Site = BeautifulSoup(r.content, "lxml")

	return bs4Site

def link_enumerator(sDomain, lDomain_container, lLink_container):

	# If there are no domains in the domain container, it means that /
	# there is only one domain to be scanned

	if lDomain_container == None or len(lDomain_container) == 0:
		sDomain_enum = [sDomain]
	else:
		sDomain_enum = lDomain_container

	for domain in sDomain_enum:
		logging.debug("Now searching {} for {}".format(domain, lLink_container))

		try:
			r = requests.get(domain)
		except requests.exceptions.MissingSchema as e:
			logging.info(("Domain request error: ", e))
			continue
			
		bs4Site = BeautifulSoup(r.content, "lxml")

		return bs4Site

def link_search(bs4Site, lLink_container):
	
	for x, q in enumerate(lLink_container):
		iCounter = 0
		reg = re.findall(re.escape(q) + r"\..*?\"", str(bs4Site))

		if len(reg) != 0:
			for x, y in enumerate(reg):
				lOutput_container.append(y.strip("\""))
				iCounter += 1
			logging.debug(str(iCounter) + " instances of " + q + " was found and added to output.")
		else:
			logging.debug(q + " was not found.")
			continue

def sitemap_search(sDomain, lLink_container):
	
	site = site_data(sDomain)
	
	urls = []
	
	for link in site.find_all("loc"):
		urls.append(link.string)

	for url in urls:
		link_search(link_enumerator(url, None, lLink_container), lLink_container)

def export_links(lOutput_container, sOutput):

	if os.path.isfile(sOutput + ".txt"):
		sOutput = sOutput + str(random.randint(1, 9999))
	
	with open(sOutput + ".txt", mode="w") as file:
			lOutput_container = set(lOutput_container)
			lOutput_container = sorted(lOutput_container)
			for element in lOutput_container:
				file.write(element + "\n")

def keyboard_interrupt_save_and_exit():
	sKeyboard_int_error_msg = "Scraping interrupted. Saving and exiting."
	print(sKeyboard_int_error_msg)
	logging.warning(sKeyboard_int_error_msg)

def main(sDatabase, sDomain, sOutput, bLogging):

	logging.debug("--- New session started ---")
	logging.debug(msg="sDatabase={}, sDomain={}, sOutput={}, bLogging={}, bSitemap={}".format(sDatabase, sDomain, sOutput, bLogging, bSitemap))
	
	# Open database

	with open(sDatabase, mode="r") as file:
		for line in file:
			if re.findall(r"^##.*", str(line)):
				continue
			elif re.findall(r"^\s.*", str(line)):
				continue
			else:
				lLink_container.append(line.rstrip())

	# Request domain data
	if sDomain is not None:
		try:
			r = requests.get(sDomain)
		except requests.exceptions.MissingSchema:
			sDomain = "https://" + sDomain
			r = requests.get(sDomain)
			logging.info("Argument missing https prefix.")
		except requests.exceptions.MissingSchema:
			sDomain = "http://" + sDomain
			r = requests.get(sDomain)
			logging.info("Argumet missing http prefix.")

	# CLI option launcher

	if sFile_with_urls:
		try:
			with open(sFile_with_urls, mode="r") as file:
				for line in file:
					if re.findall(r"^##.*", str(line)):
						continue
					elif re.findall(r"^\s.*", str(line)):
						continue
					else:
						line = line.rstrip()
						try:
							r = requests.get(line)
						except requests.exceptions.MissingSchema:
							line = "https://" + line
							r = requests.get(line)
							logging.info("Argument missing https prefix.")
						except requests.exceptions.MissingSchema:
							line = "http://" + line
							r = requests.get(line)
							logging.info("Argumet missing http prefix.")
						
						lDomain_container.append(line.rstrip())
				
					if bSitemap:
						print(f"Now scraping sitemap {line} for urls.")
						sitemap_search(line, lLink_container)
					else:
						link_search(link_enumerator(sDomain, lDomain_container, lLink_container), lLink_container)
		except KeyboardInterrupt:
			keyboard_interrupt_save_and_exit()

	else:
		if bSitemap:
			print(f"Now scraping sitemap {sDomain} for urls.")
			try:
				sitemap_search(sDomain, lLink_container)
			except KeyboardInterrupt:
				keyboard_interrupt_save_and_exit()

		elif sDomain:
			link_search(link_enumerator(sDomain, lDomain_container, lLink_container), lLink_container)

	# Export data to txt

	export_links(lOutput_container, sOutput)
	
if __name__ == "__main__":
	main(sDatabase, sDomain, sOutput, bLogging)