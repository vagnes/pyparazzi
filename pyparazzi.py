#!/usr/bin/env python3
import argparse
import logging
import os
import re
import sys
import time

from bs4 import BeautifulSoup


class Pyparazzi(object):

	def __init__(self, requests, bLogging=False):

		# Dependency injection
		self.requests = requests
		self.bLogging = bLogging

		# Init containers
		self.lOutput_container = []

	# Functions

	def site_data(self, sDomain):

		# Request domain data

		try:
			r = self.requests.get(sDomain)
		except self.requests.exceptions.MissingSchema:
			sDomain = "https://" + sDomain
			r = self.requests.get(sDomain)
			logging.info("Argument missing https prefix.")
		except self.requests.exceptions.MissingSchema:
			sDomain = "http://" + sDomain
			r = self.requests.get(sDomain)
			logging.info("Argumet missing http prefix.")

		# Parse data

		bs4Site = BeautifulSoup(r.content, "lxml")

		return bs4Site

	def link_enumerator(self, domain):

		# If there are no domains in the domain container, it means that /
		# there is only one domain to be scanned

		logging.debug("Now searching {}".format(domain))

		try:
			r = self.requests.get(domain)
		except self.requests.exceptions.MissingSchema as e:
			try:
				logging.debug("Missing schema. Trying HTTP.")
				r = self.requests.get("http://" + domain)
			except self.requests.exceptions.RequestException:
				logging.debug("HTTP failed. Trying HTTPS.")
				r = self.requests.get("https://" + domain)

		bs4Site = BeautifulSoup(r.content, "lxml")

		return bs4Site

	def link_search(self, bs4Site, lLink_pattern):

		found = 0

		for y in lLink_pattern.finditer(str(bs4Site)):
			self.lOutput_container.append(y.group().strip("\""))
			found += 1

		logging.debug(str(found) + " instances found and added to output.")

	def sitemap_search(self, sDomain, lLink_container):

		site = self.site_data(sDomain)

		urls = []

		for link in site.find_all("loc"):
			urls.append(link.string)

		for url in urls:
			logging.info(f"Now scraping {url} for urls.")
			self.link_search(self.link_enumerator(url), lLink_container)

	def export_links(self, file):

		lOutput_container = set(self.lOutput_container)
		lOutput_container = sorted(lOutput_container)
		for element in lOutput_container:
			file.write(element + "\n")

	def keyboard_interrupt_save_and_exit(self):
		sKeyboard_int_error_msg = "Scraping interrupted. Saving and exiting."
		print(sKeyboard_int_error_msg)
		logging.warning(sKeyboard_int_error_msg)

	def main(self, sDatabase, sDomains, bSitemap, sOutput):

		logging.debug("--- New session started ---")
		logging.debug(msg="sDatabase={}, sDomains={}, sOutput={}, bLogging={}, bSitemap={}".format(sDatabase, sDomains, sOutput, self.bLogging, bSitemap))

		# Open database
		lLink_container = []

		for line in sDatabase:
			if re.findall(r"^##.*", str(line)):
				continue
			elif re.findall(r"^\s.*", str(line)):
				continue
			else:
				lLink_container.append(re.escape(line.rstrip()))

		if len(lLink_container) == 0:
			logging.fatal("No entries in database")
			return

		lLink_pattern = re.compile("(({domains})\.[^\s\"]+)".format(domains='|'.join(lLink_container)))

		# Request domain data
		for sDomain in sDomains:
			try:
				if bSitemap:
					logging.info(f"Now scraping sitemap {sDomain} for urls.")
					self.sitemap_search(sDomain, lLink_pattern)
				else:
					logging.info(f"Now scraping {sDomain} for urls.")
					self.link_search(self.link_enumerator(sDomain), lLink_pattern)
			except KeyboardInterrupt:
				self.keyboard_interrupt_save_and_exit()

		self.export_links(sOutput)

if __name__ == "__main__":
	import requests
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
		"-o", "--output", metavar="str", type=str, default='output',
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

	sOutput = args.output
	sDatabaseFile = args.database
	bLogging = args.log
	bSitemap = args.sitemap

	# Enable logging

	if bLogging:
		logging.basicConfig(filename=str(sOutput)+".log", level=logging.DEBUG,
		format="%(asctime)s - %(levelname)s %(module)s - %(funcName)s: %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S")

	sDomains = []

	if args.domain and args.file:
		logging.fatal("Both domain and domains file provided. Which is it?")
		sys.exit(1)
	elif args.domain:
		sDomains = [args.domain]
	else:
		with open(args.file, mode="r") as file:
			for line in file:
				if re.findall(r"^##.*", str(line)):
					continue
				elif re.findall(r"^\s.*", str(line)):
					continue
				else:
					sDomains.append(line.rstrip())

	pyparazzi = Pyparazzi(requests, bLogging)

	with open(sDatabaseFile, mode="r") as file:
		sDatabase = file.readlines()

	if os.path.isfile(sOutput + ".txt"):
		sOutput = sOutput + time.strftime('%Y%m%d%H%M%S')

	with open(sOutput + ".txt", mode="w") as file:
		pyparazzi.main(sDatabase, sDomains, bSitemap, file)
