#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup
from concurrent import futures
import logging
import os
import requests
import re
import random
import sys
import time

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

# Ensure valid filename

try:
	if os.path.isfile(sOutput + ".txt"):
		sOutput = sOutput + str(random.randint(1, 9999))
except TypeError:
	sOutput = "".join([x for x in sDomain if x.isalnum()])
	if os.path.isfile(sOutput + ".txt"):
		sOutput = sOutput + str(random.randint(1, 9999))

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
		logging.debug("Now searching {} for {}".format(
			domain, lLink_container))

		try:
			r = requests.get(domain)
		except requests.exceptions.MissingSchema as e:
			logging.info(("Domain request error: ", e))
			continue

		bs4Site = BeautifulSoup(r.content, "lxml")

		return bs4Site


def link_search(bs4Site, lLink_container):

	for _, q in enumerate(lLink_container):
		iCounter = 0
		reg = re.findall(re.escape(q) + r"\..*?\"", str(bs4Site))

		if len(reg) != 0:
			with futures.ThreadPoolExecutor() as executor:
				a_future = {executor.submit(
					enumerate, reg): reg for reg in reg}
				for future in futures.as_completed(a_future):
					to_container = a_future[future]
					lOutput_container.append(to_container.strip("\""))
					iCounter += 1
			logging.debug(str(iCounter) + " instances of " +
						  q + " was found and added to output.")
		else:
			logging.debug(q + " was not found.")
			continue


def sitemap_search(sDomain, lLink_container):

	site = site_data(sDomain)

	urls = []

	for link in site.find_all("loc"):
		urls.append(link.string)

	with futures.ThreadPoolExecutor() as executor:
	    a_future = {executor.submit(
	        link_enumerator, url, None, lLink_container): url for url in urls}
	    for future in futures.as_completed(a_future):
	        site = future.result()
	        with futures.ThreadPoolExecutor() as executor:
	            a_future = {executor.submit(
	                link_search, data, lLink_container): data for data in site}


def export_links(lOutput_container, sOutput):

	with open(sOutput + ".txt", mode="w") as file:
		lOutput_container = set(lOutput_container)
		lOutput_container = sorted(lOutput_container)
		for element in lOutput_container:
			file.write(element + "\n")


def domain_schema_fixer(sDomain):

	try:
		_ = requests.get(sDomain)
	except requests.exceptions.MissingSchema:
		sDomain = "https://" + sDomain
		_ = requests.get(sDomain)
		logging.info("Argument missing https prefix.")
	except requests.exceptions.MissingSchema:
		sDomain = "http://" + sDomain
		_ = requests.get(sDomain)
		logging.info("Argumet missing http prefix.")


def keyboard_interrupt_save_and_exit():

	sKeyboard_int_error_msg = "Scraping interrupted. Saving and exiting."
	print(sKeyboard_int_error_msg)
	logging.warning(sKeyboard_int_error_msg)


def main(sDatabase, sDomain, sOutput, bLogging):

	logging.debug("--- New session started ---")
	logging.debug(msg="sDatabase={}, sDomain={}, sOutput={}, bLogging={}, bSitemap={}".format(
		sDatabase, sDomain, sOutput, bLogging, bSitemap))

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
		domain_schema_fixer(sDomain)

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
						domain_schema_fixer(line)
						lDomain_container.append(line.rstrip())

					if bSitemap:
						print("Now scraping sitemap {} for urls.".format(line))
						sitemap_search(line, lLink_container)
					else:
						link_search(link_enumerator(
							sDomain, lDomain_container, lLink_container), lLink_container)
		except KeyboardInterrupt:
			keyboard_interrupt_save_and_exit()

	else:
		if bSitemap:
			print("Now scraping sitemap {} for urls.".format(sDomain))
			try:
				sitemap_search(sDomain, lLink_container)
			except KeyboardInterrupt:
				keyboard_interrupt_save_and_exit()

		elif sDomain:
			link_search(link_enumerator(sDomain, lDomain_container,
										lLink_container), lLink_container)

	# Export data to txt

	export_links(lOutput_container, sOutput)


if __name__ == "__main__":
	a = time.time()
	main(sDatabase, sDomain, sOutput, bLogging)
	b = time.time()
	print("Scanning took", b-a, "seconds.")
