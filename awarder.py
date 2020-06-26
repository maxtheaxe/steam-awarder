# awarder.py - steam-awarder - maxtheaxe
# code taken in part from my previous selenium/python projects
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import sys
import re
import time
import random
import signal
import os
import inspect
import csv
from win10toast import ToastNotifier

# set path to chrome driver for packaging purposes
# ref: https://stackoverflow.com/questions/41030257/is-there-a-way-to-bundle-a-binary-file-such-as-chromedriver-with-a-single-file
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe() ))[0]))

# launch() - launch sequence to get driver started, bring to login page
def launch(headless = False, verbose = False):
	# print("\tLaunching a bot...\n")
	driver = start_driver(headless) # start the driver and store it (will be returned)
	driver.get("https://steamcommunity.com/login/") # open steam login page
	toaster = ToastNotifier()
	toaster.show_toast("Steam Awarder","Please log in via the browser window.")
	input("\n\tHit Enter to continue...") # wait for user prompt to resume
	# print("\t", bot_name, "successfully launched.\n")
	return driver # return driver so it can be stored and used later

# start_driver() - starts the webdriver and returns it
def start_driver(headless = False):
	# set path to chrome driver for packaging purposes
	chromedriver = os.path.join(current_folder,"chromedriver.exe")
	# setup webdriver settings
	options = webdriver.ChromeOptions()
	# add ublock origin to reduce impact, block stuff
	# options.add_extension("ublock_origin.crx")
	# other settings
	options.headless = headless # headless or not, passed as arg
	options.add_experimental_option('excludeSwitches', ['enable-logging']) # chrome only maybe
	# make window size bigger
	# options.add_argument("--window-size=1600,1200")
	return webdriver.Chrome(options = options, executable_path = chromedriver)

# give_awards() - gives all possible rewards for all reviews for a given user
def give_awards(driver, given_url, max_pages = 3):
	# navigate to given url (should be reviews page)
	driver.get(given_url)
	# for a maximum of given number of pages of reviews (default 3)
	for n in range(max_pages):
		# collect award buttons on current page
		award_buttons = collect_award_buttons(driver)
		# loop over collected buttons
		for i in range(len(award_buttons)):
			# click the current button
			award_buttons[i].click()
			# now give all possible individual awards for that review
			# 10 accounts for future possible additions, without allowing total runaway
			for x in range(10):
				# run give review awards and store result
				result = give_review_awards(driver)
				# if result is false, break out of loop
				if (result == False):
					break
		# now move on to next page of reviews
		page_result = advance_page(driver)
		# if there wasn't another page to move on to
		if (page_result == False):
			# then break out of loop
			break
	return

# collect_award_buttons() - collects award buttons for each review displayed
# reference: https://www.guru99.com/xpath-selenium.html
def collect_award_buttons(driver):
	# find all award buttons on the given page and store 'em in a list
	award_buttons = driver.find_elements_by_xpath("//span[@onclick='UserReview_Award']")
	# return the list of buttons
	return award_buttons

# advance_page() - move to next page of reviews if possible
# reference: https://stackoverflow.com/a/32713128
def advance_page(driver):
	# collect all page buttons and store in list
	page_buttons = driver.find_elements_by_class_name('pagebtn')
	# check if secondary button(s) are disabled
	if ("disabled" in page_buttons[1].get_attribute('class').split(' ')):
		# then return false, because we've reached the end
		return False
	# otherwise, click the secondary button and advance the page
	page_buttons[1].click()
	# return True since there are more awards to be given
	return True

# give_review_awards() - gives all rewards for a given review
def give_review_awards(driver):
	# wait for modal overlay to appear (looks for class)
	wait = WebDriverWait(driver, 10)
	element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'FullModalOverlay')))
	# try to give an individual award and store the result
	result = give_individual_award(driver)
	# wait for modal overlay to close
	element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'FullModalOverlay')))
	# return result, so the parent function knows whether to try again for that review
	return result

# give_individual_award() - gives individual award for given review (modal already open)
def give_individual_award(driver):
	# store any "ungiven" individual award buttons on popup in list
	review_awards = driver.find_elements_by_xpath(
		"//button[@class='awardmodal_Button_3M92h unstyledbutton_UnstyledButton_1hcJa']")
	# if there are any left "ungiven"
	if (len(review_awards) > 0):
		# then select the first one
		review_awards[0].click()
	# otherwise, all have been given
	else:
		# click the close button to exit modal overlay
		driver.find_element_by_class_name('closeButton').click()
		# now return false to indicate none are left to give
		return False
	# find and click next twice (next, give award)
	for i in range(2):
		next_button = driver.find_element_by_xpath(
			"//button[@class='awardmodal_SubmitButton_2FENd unstyledbutton_UnstyledButton_1hcJa']")
		next_button.click()
	# return True to indicate one was given successfully (or at least one could've been)
	return True

# run_with_target() - takes in a url from cli and gives awards to that user
def run_with_target(driver):
	# ask user for url to target's reviews page
	reviews_url = input("\tWhat is the link for the target's reviews page? "\
		"\n\t(Paste it in and press Enter, or leave it blank to award the creator)\n\n\t")
	# check if they intentionally left it blank
	if (reviews_url == ""):
		# let them know they left it blank, and give them an option to continue
		secondary_url = input("\tYou left it blank, indicating you want to target " \
			"the creator of the program. \n\t(Leave it blank again to confirm, or enter " \
			"your intended target.)\n\n\t")
		# if they continue, feed creator's (my) link to program as target
		if (secondary_url == ""):
			reviews_url = "https://steamcommunity.com/id/JewishJuggernaut/recommended/"
		# otherwise, continue with the link they just entered
		else:
			reviews_url = secondary_url
	# check if given url is valid (create regex for reviews link)
	url_pattern = re.compile(
		"^https://steamcommunity.com/id/[a-zA-z0-9]{2,}/recommended/?$")
	# if not, call self again
	if not (bool(url_pattern.match(reviews_url))):
		# let the user know they messed up
		print("\n\tError: Invalid reviews link "\
			"(it should look something like:\n\t"\
			"https://steamcommunity.com/id/JewishJuggernaut/recommended/).\n")
		return run_with_target(driver)
	# give awards to that url
	give_awards(driver, reviews_url)
	# alert them it's finished giving awards for that user
	print("\n\tAwards successfully given.\n")
	return

def main():
	# display title
	print("\n\t--- Steam Awarder by Max ---\n")
	# warn users about using program
	input("\tWarning: Use this program at your own risk!\n\t(press Enter to continue)\n\n\t")
	# create the driver (browser window) and keep track of it
	main_driver = launch()
	# while program is running, accept input in form of links to reviews pages
	while True:
		run_with_target(main_driver)

if __name__ == '__main__':
	main()