#!/usr/bin/env python
# coding: utf-8

# # IMPORTING LIBS

# In[1]:


import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tkinter import Tk     
from tkinter.filedialog import askopenfilename
import os
import sys
import re
import shutil
import numpy as np
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.progress import track


# # HELPER FUNCTIONS

# In[2]:


def setup_drivers():
    data_path = os.getcwd() + "\\data"
    options = webdriver.ChromeOptions()
    options.add_argument(fr'--user-data-dir={data_path}')
    chromedriver = webdriver.Chrome(executable_path=r'chromedriver.exe',options=options)
    wait = WebDriverWait(chromedriver,30)
    return chromedriver,wait


# In[3]:


def copy_data_folder():
    src = os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data"
    if not(os.path.exists(src)):
        print("Google Chrome is needed for this script.")
        print("Exiting...")
        time.sleep(2)
        sys.exit()
    dest = os.getcwd() + "\\data"
    if (os.path.exists(dest)):
        shutil.rmtree(dest)
    try:
        shutil.copytree(src,dest)
    except:
        pass


# In[4]:


def switch_acc(chromedriver,wait,email):
    chromedriver.get("https://www.youtube.com")
    top_btn_xPath = '''//*[@id="img"]'''
    wait.until(EC.element_to_be_clickable((By.XPATH,top_btn_xPath))).click()
    switch_acc_btn_xPath = '''/html/body/ytd-app/ytd-popup-container/iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/
    div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[4]/a/paper-item'''
    wait.until(EC.element_to_be_clickable((By.XPATH,switch_acc_btn_xPath))).click()
    time.sleep(2)
    email_elements = chromedriver.find_elements_by_xpath('''//*[@id="contents"]/ytd-account-item-section-renderer/ytd-account-item-section-header-renderer/yt-formatted-string/a''')
    email_index = -1
    for i in range(len(email_elements)):
        if(email_elements[i].text == email):
            email_index = i
    if(email_index == -1):
        return False
    switch_elements =  chromedriver.find_elements_by_xpath('''//*[@id="contents"]/ytd-account-item-renderer/paper-icon-item''')
    switch_elements[email_index].click()
    return True


# In[5]:


def get_subscriptions(chromedriver,save_to_file=False):
    chromedriver.get("https://www.youtube.com/feed/channels")
    script = '''
    var pageHeight = 0;
    function findHighestNode(nodesList) {
        for (var i = nodesList.length - 1; i >= 0; i--) {
            if (nodesList[i].scrollHeight && nodesList[i].clientHeight) {
                var elHeight = Math.max(nodesList[i].scrollHeight, nodesList[i].clientHeight);
                pageHeight = Math.max(elHeight, pageHeight);
            }
            if (nodesList[i].childNodes.length) findHighestNode(nodesList[i].childNodes);
        }
    }

    findHighestNode(document.documentElement.childNodes);
    window.scrollTo(0, pageHeight);
    pageHeight = 0;
    findHighestNode(document.documentElement.childNodes);
    return pageHeight
    '''
    lenOfPage = chromedriver.execute_script(script)
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = chromedriver.execute_script(script)
        if lastCount==lenOfPage:
            match=True
    html = chromedriver.page_source
    finder = re.compile(r'''<yt-formatted-string id="text" title="" class="style-scope ytd-channel-name">(.+?)</yt-formatted-string>''')
    subs = finder.findall(html)
    if(subs[-1] == "<!--css-build:shady-->"):
        subs = subs[:-1]
    for i in range(len(subs)):
        subs[i] = subs[i].replace(","," ") 
    if(save_to_file):
        subs_array = np.array(subs)
        np.savetxt("subs.csv",subs_array,delimiter=",",fmt="%s",encoding='utf-8')
    return subs


# In[6]:


def subscriber(chromedriver,subs_list):
    search_xPath = '''//*[@id="search"]'''
    sub_btn_xPath = '''//*[@id="subscribe-button"]/ytd-subscribe-button-renderer/paper-button'''
    for cname in track(subs_list,description="Subscribing"):
        chromedriver.get('''https://youtube.com''')
        search = wait.until(EC.element_to_be_clickable((By.XPATH,search_xPath)))
        search.send_keys(cname + Keys.ENTER)
        try:
            sub_btn = wait.until(EC.element_to_be_clickable((By.XPATH,sub_btn_xPath)))
            sub_btn.click()
        except:
            continue


# In[7]:


def exit_program(chromedriver):
    chromedriver.close()
    data_path = os.getcwd() + "\\data"
    os.system('cls')
    print("Deleting temp files....")
    try:
        shutil.rmtree(data_path)
        print("Deleted temp files. Exiting...")
    except:
        print("Error deleting temp files. Manually delete \data folder.\nExiting...")
    time.sleep(2)
    os.system('cls')
    sys.exit()


# In[9]:


menu = '''
1. Save subs list to csv.\n
2. Copy subs from csv.\n
3. Copy subs from one email to another.\n
4. Exit.\n'''
os.system('cls')
print("Copying chrome data.....")
copy_data_folder()
print("Copying finished.")
time.sleep(2)
os.system('cls')
subs_list = None
while True:
    os.system('cls')
    print(Panel(menu, title="Youtube Subscriptions Copy"))
    console = Console()
    option = console.input("Choose an option : ")
    os.system('cls')
    if(option == "1"):
        email = console.input("Enter your email : ")
        chromedriver,wait = setup_drivers()
        switch_acc(chromedriver,wait,email)
        get_subscriptions(chromedriver,save_to_file=True)
        chromedriver.close()
    elif(option == "2"):
        Tk().withdraw()
        chromedriver,wait = setup_drivers()
        filename = askopenfilename(filetypes=[("CSV Files","*.csv")])
        subs_list = list(np.genfromtxt(filename,delimiter=",",dtype=str,encoding="utf-8"))
        email = console.input("Enter your email to which subs are to be copied : ")
        r = switch_acc(chromedriver,wait,email)
        if(r == False):
            print("Email not found...")
            time.sleep(2)
            break
        subscriber(chromedriver,subs_list)
        chromedriver.close()
    elif(option == "3"):
        email1 = console.input("Enter your email from which subs are to be taken : ")
        chromedriver,wait = setup_drivers()
        r = switch_acc(chromedriver,wait,email1)
        if(r == False):
            print("Email not found...")
            time.sleep(2)
            break
        subs_list = get_subscriptions(chromedriver)
        os.system('cls')
        email2 = console.input("Enter your email to which subs are to be copied : ")
        r = switch_acc(chromedriver,wait,email2)
        if(r == False):
            print("Email not found...")
            time.sleep(2)
            break
        subscriber(chromedriver,subs_list)
        chromedriver.close()
    elif(option == "4"):
        exit_program()


# In[ ]:





# In[ ]:




