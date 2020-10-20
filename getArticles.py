#!/usr/bin/env python
# coding=utf-8
# author: L. Rodrigues
# creation: 15.10.2020

import time, json, sys, os, subprocess, re, csv, random
from lxml import html #pip install lxml cssselect
import time, datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.sql import exists, and_
from math import ceil

from ressources.webdriver import Chrome, Firefox # fichier selenium_driver.py à placer dans le même dossier que votre script
from ressources.documentation import Documentation # fichier documentation.py qui se trouve dans le dossier ressource
from ressources.db import *
from ressources.project_utils import mapping_countries, map_country

ADS_PER_PAGE=20


def check_exists_by_xpath(webelement, xpath): 
    """Check whether exist"""

    try:
        webelement.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def saveData(browser, path):
    '''Fonction pour l'exemple qui enregistre le code client, la capture d'écran et code serveur'''

    browser.clientCode(path+'_clientCode.html')
    browser.screenshot(path+'_screenshot.png', width=1080) #on fixe la largeur de la fenêtre avec width
    
    #TODO : Trouver un moyen de prendre le code serveur et retourner en arrière sinon le script marche pas
    #browser.serverCode(path+'_serverCode.html')
    
    #Possibles solutions

    #browser.driver.back()
    #browser.driver.execute_script("window.history.go(-1)")

def resume_extraction(browser, session, pages) :
    """Check if the first ad of the page is in the database. Otherwise pass n pages per n pages until the first new ad
    and then go back n pages further. The purpose is to locate the interval of n pages where the script has stopped.    
    This function has been made because there is no way to select a specific page on the website or go n pages further"""

    #Obtain the total number of pages for this country at this moment, the purpose is to avoid reaching the last page
    raw_string=browser.driver.find_element_by_xpath("//div[@style][contains(text(),\"Number of ads: \")]").text
    total_pages=ceil(int(re.findall("Number of ads: (\d*)\. .*", raw_string)[0])/ADS_PER_PAGE)
    #Extract the first ad before the loop
    firstad = browser.driver.find_elements_by_xpath('//div[@class="row clearfix"][@style]')[0]
    ad_number = firstad.find_element_by_xpath(".//input[@type=\"checkbox\"]").get_attribute("name") 
    country= map_country(browser.driver.current_url)

    #Counter that counts the number of pages that have been passed
    counter=0
    while session.query(exists().where(and_(Urls_ads.ad_number==ad_number,Urls_ads.country_id==country ))).scalar() and not counter==total_pages-1 :
        for n in range(pages) :
            time.sleep(random.uniform(0.2, 1))
            test = 0
            while not test :
                try :
                    browser.driver.find_element_by_xpath("//input[@name=\"button_hits_seen\"]").click() 
                    test=1
                except WebDriverException as e:
                    print(f"{e}\n")
                    doc.adderrorlog(f"{e}\n")
                    #The webdriver is on a error page, go back
                    browser.driver.back()
            counter+=1
            #Need to break otherwise an error pops up since we're trying to the next button that doesn't exist anymore at the end
            print(f"{country} - Skipped pages : {counter} / Total pages : {total_pages}\n")
            doc.addlog(f"{country} - Skipped pages : {counter} / Total pages : {total_pages}\n")
            if counter==total_pages-1 :
                break
        #print(f"{country} : Skip {pages} pages\n")
        firstad = browser.driver.find_elements_by_xpath('//div[@class="row clearfix"][@style]')[0]
        ad_number = firstad.find_element_by_xpath(".//input[@type=\"checkbox\"]").get_attribute("name") 
    #Go back n pages whether we are not at the first page. We check with the presence of the previous button
    if check_exists_by_xpath(browser.driver, "//input[@name=\"previous_hits_button\"]") :
        #Number of pages to go back according to the number we have really skip
        back_pages = counter%pages if pages!=counter else pages
        for n in range(back_pages) :
            time.sleep(random.uniform(0.2, 1))
            test = 0
            while not test :
                try :
                    browser.driver.find_element_by_xpath("//input[@name=\"previous_hits_button\"]").click() 
                    test =1
                except WebDriverException as e:
                    print(f"{e}\n")
                    doc.adderrorlog(f"{e}\n")
                    #The webdriver is on a error page, go back
                    browser.driver.back()
            counter-=1
        print(f"{country} : Go back {back_pages} pages\n")
        doc.addlog(f"{country} : Go back {back_pages} pages\n")
    doc.addlog(f"{country} : To resume the extraction : {counter} have been passed per {pages} pages interval")
    print(f"{country} : SUCCESS Resume")

def getbirds(browser, url) :   
    """Go to bird section"""
    url = url.strip("/") + "/pets/Birds/"
    info = browser.get(url)
    return info

def getads(browser, session, pages=20, update=True) :
    """Go through all pages to collect articles' urls, number of pages to search the last stop. Whether there are
    new recent articles, the function updates the database rather than resume the extraction"""

    #Get the current country
    country= map_country(browser.driver.current_url)
    #Check we are updating
    print(f"{country} : Updating the ads") if not check_update(browser, session) else None
    doc.addlog(f"{country} : Updating the ads")
    #If the country has not yet been extracted, no resume. If number of entries < the pages interval, no resume.
    nbr_entries_country=len(session.query(Urls_ads).filter(Urls_ads.country_id==country).all())
    if nbr_entries_country ==0 or nbr_entries_country < pages :
        pass
    else :
        #Resume the extraction
        print(f"{country} : Resuming extraction...")
        doc.addlog(f"{country} : Resuming extraction...")
        resume_extraction(browser, session, pages)
    #Just to avoid passing the first page
    counter=0
    #Allow to break whether we have updated the start of the ads and there is no more new ads
    counter_not_new=0
    #No need to wait between requests, it is on the same page, just javascript
    #When the next button disappears at the end 
    while check_exists_by_xpath(browser.driver, "//input[@name=\"button_hits_seen\"]")  :
        #Click on the "next button" / Except the first page
        time.sleep(random.uniform(2, 2.5))
        #Try until it works or CTRL-C
        test = 0
        while not test :
            try :
                browser.driver.find_element_by_xpath("//input[@name=\"button_hits_seen\"]").click() if counter==1 else None
                counter=1
                test =1
            except WebDriverException as e:
                print(f"{e}\n")
                doc.adderrorlog(f"{e}\n")
                #The webdriver is on a error page, go back
                browser.driver.back()
        for ad in browser.driver.find_elements_by_xpath('//div[@class="row clearfix"][@style]') :
            #The website is inconsistent, there is tag without ad
            ad_number = ad.find_element_by_xpath(".//input[@type=\"checkbox\"]").get_attribute("name") 
            url = ad.find_element_by_xpath(".//a").get_attribute("href") 
            #Check if the entry already exists and do nothing in case according to the ad_number and country
            if session.query(exists().where(and_(Urls_ads.ad_number==ad_number,Urls_ads.country_id==country ))).scalar() :
                counter_not_new+=1
            else :
                #Refresh the counter since an entry has been added
                counter_not_new=0
                entry=Urls_ads(url=url, ad_number=int(ad_number), country_id=country)
                entry.insertURL(session)
                print(f"{country} : Ad added\n")
                doc.addlog(f"{country} : Ad added\n")
        print(f"{country} :\n\tNext page\n\tNo new entry since {counter_not_new} entries\n")
        doc.addlog(f"{country} :\n\tNext page\n\tNo new entry since {counter_not_new} entries\n")
        if counter_not_new > (pages*ADS_PER_PAGE) :
            #We have updated the country
            print(f"{country} : Ads have been updated")
            break
    print(f"{country} : No more ads\n")
    doc.addlog(f"{country} : No more ads\n")

def check_update(browser, session) :
    """Give TRUE whether the database is up to date"""
    firstad = browser.driver.find_elements_by_xpath('//div[@class="row clearfix"][@style]')[0]
    ad_number = firstad.find_element_by_xpath(".//input[@type=\"checkbox\"]").get_attribute("name") 
    country= map_country(browser.driver.current_url)
    resp = session.query(exists().where(and_(Urls_ads.ad_number==ad_number,Urls_ads.country_id==country ))).scalar()
    return resp




if __name__ == '__main__':
    cT = datetime.datetime.now()
    date_extraction = f"{str(cT.year)}-{str(cT.month)}-{str(cT.day)}_{str(cT.hour)}-{str(cT.minute)}"
     #~~~~~~~~~~~~~~~ Configuration ~~~~~~~~~~~~~~~#
    filename_prefix = 'urlArticles'
    path = f'./results/getArticles/{date_extraction}_'

    browser = Firefox(tor=False, headless=True)
    doc = Documentation(driver=browser.driver)

    #~~~~~~~~~~~~~~~ Catch'em all ~~~~~~~~~~~~~~~#
    """REMOVE TO UPDATE THE COUNTRY => That's the only solution you can't go to the end of the ads' list
    and you can't select a specific page AND you can't sort by age (Advanced search doesn't work at the moment)"""

    completed_countries=["UNITED KINGDOM"] #REMOVE TO UPDATE
    for row in session.query(Country).all():
        url = row.url

        info = getbirds(browser, url)
        doc.info['selenium'] = []
        doc.info['selenium'].append(info)

        #Pass the country whether completed
        country= map_country(browser.driver.current_url)
        doc.addlog(f"{country} : info = getbirds(browser, url)")
        if country in completed_countries :
            print(f"{country} : Passed")
            doc.addlog(f"{country} : Passed")
            pass
        else :

            # Pre-record if error 
            with open(f'./results/getArticles/{date_extraction}_{filename_prefix}_documentation.json', 'wb') as f:
                f.write(str(doc).encode('utf-8'))
            #Click on sale
            browser.driver.find_element_by_xpath('//option[contains(text(), "FOR SALE / ADOPTION:")]').click()
            doc.addlog(f"{country} : browser.driver.find_element_by_xpath(\'//button[@name=\"login\"]\').click())")
            #Reclick on "Birds"
            browser.driver.find_element_by_xpath('//option[contains(text(), "Birds")]').click()
            doc.addlog(f"{country} : browser.driver.find_element_by_xpath(\'//option[contains(text(), \"Birds\")]\').click()")

            saveData(browser, path+filename_prefix)
            doc.addlog(f"{country} : saveData(browser, path+filename_prefix)")

            #Gather all ads
            getads(browser, session, pages=1)
            doc.addlog(f"{country} : getads(browser, session)")

            # ~~~~~~~~~~~~~~~ Documentation - enregistrement (overwritten) ~~~~~~~~~~~~~~~ #
            with open(f'./results/getArticles/{date_extraction}_{filename_prefix}_documentation.json', 'wb') as f:
                f.write(str(doc).encode('utf-8'))

    # ~~~~~~~~~~~~~~~ Shut down the webdriver ~~~~~~~~~~~~~~~ #

    browser.driver.quit()

