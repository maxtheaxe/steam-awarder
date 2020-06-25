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
def give_awards(driver, given_url):
	# navigate to given url (should be reviews page)
	driver.get(given_url)
	# for a maximum of 20 pages of reviews
	for n in range(20):
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
	page_buttons = driver.get_elements_by_class_name('pagebtn')
	# check if secondary button(s) are disabled
	if (page_buttons[1].get_attribute('class').contains('disabled')):
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

def main(argv):
	# display title
	print("\n\t--- Steam Awarder by Max ---\n")
	# warn users about using program
	input("\tWarning: Use this program at your own risk!\n\t(press Enter to continue)\n\n\t")
	# create the driver (browser window) and keep track of it
	main_driver = launch()


if __name__ == '__main__':
	print("\n\t--- Steam Awarder by Max ---\n")
	# warn users about using program
	input("\tWarning: Use this program at your own risk!\n\t(press Enter to continue)\n\n\t")
	bot_list = cavalry(num_bots, headless, verbose, proxy) # store the bots in a list for easy closing later
	# Tell Python to run the handler() function when SIGINT is recieved
	signal.signal(signal.SIGINT, signal_handler)
	print("\n\tUse Control + C to close all bots.") # print instructions
	# wait 25 min for login code (this was a workaround for when I had issues getting codes)
	# time.sleep(1500)
	while True:
		# run maintenance every 20 minutes
		try:
			group_maintenance(bot_list)
		except:
			print("\tCheck your internet speed--it may not be fast enough to run this.")
		time.sleep(1200)
		# ask for a stream link
		# selected_stream = input("\tPaste a stream link and hit enter.\n")
		# tell all the bots to enter that stream
		# enter_stream(selected_stream)
		pass