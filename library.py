#!/usr/bin/env python

# ========================================
# Library Checker
# ----------------------------------------
# Checks the status of your library books.
# Parses them into readable objects for
# awesomeness. Currently works only with
# the Calgary Public Library system.
#
# http://calgarypubliclibrary.com
# ----------------------------------------
# @author: Hamish Macpherson
# @url: http://hami.sh/
# ========================================

import sys, re, os
import datetime
import logging
import ConfigParser
import smtplib

from string import Template

# Custom Includes
from libs import mechanize
from libs.titlecase import titlecase
from libs.BeautifulSoup import BeautifulSoup

# ==================================================
# CONFIGURATION
# --------------------------------------------------

c = ConfigParser.SafeConfigParser()
try:
	c.read(os.path.join(sys.path[0], 'settings/settings.cfg'))
except IOError:
	print "ERROR: Could not find 'settings/settings.cfg' in directory: " + str(sys.path[0])
	sys.exit(1)

# ==================================================
# LOGGING
# --------------------------------------------------

log_filename = c.get("settings", "LOG_FILENAME")
log_path = os.path.join(sys.path[0], log_filename)

logging.basicConfig(\
	filename = 	log_path, 
	level = 	logging.DEBUG, 
	format = 	'%(asctime)s %(message)s', 
	datefmt = 	'[%m/%d/%Y %I:%M:%S %p]')

# ==================================================
# TEMPLATES
# --------------------------------------------------

try:
	item_template = Template(open(os.path.join(sys.path[0], 'templates/item_template.htm'), "r").read())
	account_template = Template(open(os.path.join(sys.path[0], 'templates/account_template.htm'), "r").read())
	email_template = Template(open(os.path.join(sys.path[0], 'templates/email_template.eml'), "r").read())
except IOError:
	logging.error("Could not read one or more template files from templates/ in " + str(sys.path[0]))
	sys.exit(1)
	
# ==================================================
# PRIMARY FUNCTIONS
# --------------------------------------------------

def generateIncludes(items, account):
	
	# Items
	try:
		include_path = os.path.join(sys.path[0], c.get("settings", "INCLUDE_ITEMS_PATH"))
		include = open(include_path, "w")
	except IOError:
		logging.error("Could not open '" + include_path + "' for writing")
		sys.exit(1)
	
	logging.info("Writing " + str(len(items)) + " items to " + include_path)
	for i in items:
		html_tr = item_template.substitute(i)
		include.write(html_tr)
	
	include.close()
	
	# Account Info
	try:
		include_path = os.path.join(sys.path[0], c.get("settings", "INCLUDE_ACCOUNT_PATH"))
		include = open(include_path, "w")
	except IOError:
		logging.error("Could not open '" + include_path + "' for writing")
		sys.exit(1)
	
	logging.info("Writing account info to " + include_path)
	html = account_template.substitute(account)
	include.write(html)
	include.close()
		
	logging.info("Writing complete")		
	
def sendWarningEmail(items):
	logging.info("Sending warning email for " + str(len(items)) + " items")
	
	efrom_name = c.get("email", "FROM_NAME")
	efrom 	   = c.get("email", "FROM")
	eto 	   = c.get("email", "TO")
	esubject   = c.get("email", "SUBJECT")
	
	items_html = ""
	for item in items:
		items_html = items_html + "<li>%s by <em>%s</em><br>&mdash; due on %s</li>" % (item['title'], item['author'], item['due'])
	
	message = email_template.substitute(
	{
		'from_name' : efrom_name, 
		'from' : efrom, 
		'to' : eto, 
		'subject' : esubject,
		'items_html' : items_html
	})
			
	try:		
		m = smtplib.SMTP(c.get("email", "GMAIL_SERVER"))
		m.ehlo()
		m.starttls()
		m.ehlo()

		m.login(c.get("email", "GMAIL_LOGIN"), c.get("email", "GMAIL_PASSWORD"))
		m.sendmail(efrom, [eto], message)
		m.close()
		
		logging.info("Warning email sent")
		
	except:
		logging.error("There was an error/exception in sending the warning email")

def processItems(html):
	
	# Setup some variables	
	items = []
	warning_items = []
	current_total_due = 0.0
	bill_total_due = 0.0
	
	# Parse HTML
	soup = BeautifulSoup(html)	
	trs = soup.findAll("tr")
	
	logging.debug("Found " + str(len(trs)) + " <tr> tags")
	
	# Loop through our table...
	for tr in trs:
		# this is how we know it's an item <tr> (if the label matches)
		label = tr.find("label", {"for" : re.compile(r'RENEW\d+')})
		if label:
			
			sendwarning = False
						
			# Title
			title = label.contents[2]
			title = title.strip().replace("&nbsp;", "") # remove extraneous blank spaces
			
			# See if the title contains meta information
			# ex. "Name of Item [videorecording (DVD)]"
			title_type_regex = re.compile(r'(.*?) \[(.*?)\((.*?)\)\]')
			title_break = title_type_regex.findall(title)
			if title_break:
				title = title_break[0][0]
				item_type = title_break[0][2].lower()
			else:
				item_type = "book"
				
			# Make the title Title Case
			# http://muffinresearch.co.uk/archives/2008/05/27/titlecasepy-titlecase-in-python/
			title = titlecase(title)
			
			# Fix some of the typography/formatting
			title = title.replace("&Amp;", "&amp;") # hackish fix for some titles				
			title = title.replace(" :", ":")			
			
			logging.info("Found Item: " + title)
			
			# Author
			try:
				author = label.contents[4]
				author = author.strip().replace("/ ", "")
				
				# Extract Date info, if present
				date = None
				split = re.split("(,\s*\d+)", author)
				if len(split) > 1:
					author = split[0]
					# this is actually the author's lifespan
					# and it's oddly formatted
					date = (''.join(split[1:])).replace(", ", "") 
			except IndexError:
				author = "Unknown"
				date = None
			
			# Get all the <td>s in this item <tr>
			tds = tr.findAll("td")
				
			# Times Renewed			
			try:
				block = tds[2].contents
				times_renewed = block[1].contents[0]
				times_renewed = int(times_renewed)
			except IndexError:
				times_renewed = 0	
			
			# Due date
			try:
				due = tds[3].contents[2].strip().split(",")[0]
				#due_date = datetime.strptime(due, "%m/%d/%Y")
				due_date = None
			except IndexError:
				due = None
			
			# Status
			try:
				# This will catch 'overdue'
				status_text = tds[4].contents[0].strip()
				status = status_text.lower()
			except IndexError:
				# not overdue
				pass
				
			# so, if item is not overdue
			if (status_text == ""):
				status_text = "Checked Out"
				status = "checkedout"
			
				# Renewed Message (?)
				if times_renewed == 1:
					status_text = "Renewed Once"
				elif times_renewed == 2:
					status_text = "Renewed Twice"	
				elif times_renewed == 3:
					status_text = "Last Renewal"
					
				# Check to see if we need to return this soon
				# and if we should send a warning email
				if due:
					l = map(int, due.split("/"))
					due_date = datetime.date(l[2], l[0], l[1])
					today = datetime.date.today()
					delta = due_date - today
					
					if delta.days > 0:
						if delta.days <= int(c.get("settings", "WARNING_DAYS")):
							status = "return"
							status_text = str(delta.days) + " Day(s) Left"
						
						# Flag if we should send warning email
						if delta.days <= int(c.get("settings", "EMAIL_DAYS")):
							sendwarning = True
			# Owed
			try:
				owed = tds[5].contents[0].strip().replace("$", "")
				try:
					owed = float(owed)
				except ValueError:
					owed = 0
			except IndexError:
				owed = 0
				
			if status == "overdue":
				status_text = status_text + " ($%.2f)" % owed
				current_total_due = current_total_due + owed
			
			# Build It!
			item = {
				"title" : title, 
				"author" : author, 
				"date" : date, 
				"times_renewed" : times_renewed,
				"due_date" : due_date, 
				"due" : due, 
				"status" : status,
				"status_text" : status_text, 
				"owed" : owed,
				"item_type" : item_type
			}			
			items.append(item)
			
			if sendwarning:
				warning_items.append(item)
	
	# Process other info
	
	if current_total_due > 0:
		str_total_due = "&#36; %.2f" % current_total_due
	else:
		str_total_due = "None"
		
	# Get outstanding bill
	d = soup.find("li", "amount_owed")
	if d:
		bill_total_due = d.find("div", "amount").contents[0]
	else:
		bill_total_due = "None"
	
	account = {
		"total_checkouts" : len(items),
		"current_total_due" : str_total_due,
		"bill_total_due" : bill_total_due,
		"card_number" : c.get("settings", "CARD_NUMBER")
	}
	
	generateIncludes(items, account)
	
	# Any warnings to send?
	if len(warning_items):
		sendWarningEmail(warning_items)

# ==================================================
# LOGIN TO LIBRARY PAGE
# returns a response and mechanize Browser object
# --------------------------------------------------

def login():
	logging.info("[mechanize] Loading " + c.get("settings", "START_URL"))
	browser = mechanize.Browser()
	browser.set_handle_robots(False) # get past robots.txt prevention
	browser.open(c.get("settings", "START_URL"))
	
	# Load My Account Page
	logging.info("[mechanize] Loading Account Page")
	browser.follow_link(text_regex=r"My\s*Account", nr=0)
	
	# We'll need to login
	logging.info("[mechanize] Logging into account")
	browser.select_form(name="loginform")
	browser["user_id"] = c.get("settings", "CARD_NUMBER")
	browser["password"] = c.get("settings", "CARD_PASSWORD")	
	response = browser.submit()
	
	logging.info("[mechanize] Login success")
	
	return (response, browser)

# ==================================================
# SCRAPE THE PAGE FOR ITEMS
# --------------------------------------------------

def scrape():
	(response, browser) = login()	
	logging.info("[mechanize] Scraping items from HTML")
	html = response.read()
	processItems(html)

# ==================================================
# RENEW AN ITEM
# --------------------------------------------------

def renew(itemID):
	(response, browser) = login()
	html = response.read()
	logging.info("[mechanize] Renewing item ID = " + itemID)
	
	# Select the renewal form
	browser.select_form(nr=2)
	
	# Find the item we want to renew and 'check' it
	control = browser.find_control(id=itemID)
	control.items[0].selected = True
	
	# Submit the form
	response = browser.submit()
	html = response.read()
	
	# Dump HTML Response
#	f = open("response.htm", "w")
#	f.write(html)
#	f.close()
	
	# Was it successful?
	# We should find this string on the page
	if html.find("item was renewed"):
		logging.info("Item " + itemID + " was renewed successfully")		
	else:
		logging.info("Failed to renew Item with ID '" + itemID + "' - Maybe the limit has been reached?")

# ==================================================
# ENTRY POINT
# --------------------------------------------------

if __name__ == '__main__':
	logging.info("* Script Started *")
	# TEST MODE
	if len(sys.argv) > 1 and sys.argv[1].lower() == "test":		
		try:
			testpath = os.path.join(sys.path[0], sys.argv[2])	
			html = open(testpath, "r").read()
			logging.info("Reading " + testpath)
			processItems(html)
				
		except IOError:
			err = "ERROR: Could not open test file: " + testpath
			print err
			logging.error(err)
	
	# RENEW ITEM
	elif len(sys.argv) > 1 and sys.argv[1].lower() == "renew":
		try:
			renew(sys.argv[2])
		except IndexError:
			err = "ERROR: No item ID passed."
			print err
			logging.error(err)	
	
	# LIVE PULL MODE		
	elif "scrape" in sys.argv:
		scrape()
		
	else:
		err = "ERROR: Please pass correct arguments."
		print err
		logging.error(err)
		
	# TODO, add usage.
	
	logging.info("* Script Finished *")	
		