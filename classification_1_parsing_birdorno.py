#!/usr/bin/env python
# coding=utf-8

"""
Ce script fait partie de la première classification. Le but est de classer les annonces selon
si elles mentionnent la présence d'oiseaux ou non. Selon des termes majoritairement anglais. Les
résults sont stockés dans la table "classification_1_parse_bird_or_no"
"""

import time, json, re, datetime
from sqlalchemy.sql import exists
from ressources.documentation import Documentation
from ressources.db import session, Parse_ads, Parsing_bird_or_no
from ressources.regex_tools import word_to_regex


#Goal 1: Decide if ad contains bird
#Strategy: Look in title for words describing birds with regular expressions
def create_regex_for_birds(list_of_birds_test):
    list_of_birds = []
    for i in range(len(list_of_birds_test)):
        a = word_to_regex(list_of_birds_test[i])
        print(a)
        list_of_birds.append(a)
    #print(list_of_birds)
    return(list_of_birds)

if __name__ == '__main__':
    list_of_birds_test = ["bird", "brd", "amazon", "amazona", "parot", "prot", "african grey", "macaw", "mcw", "macw",
                          "mcaw", "macow", "cockato", "winged", "paraket", "lovebird", "canary",
                          "cnry"]  # Global variable which contains re to match
    list_of_birds = create_regex_for_birds(list_of_birds_test)
    print(list_of_birds)
    #Documentation
    cT = datetime.datetime.now()
    date_parsing = f"{str(cT.year)}-{str(cT.month)}-{str(cT.day)}_{str(cT.hour)}-{str(cT.minute)}"
    doc = Documentation()
    path_result = './results/classification/'
    #parse database
    c = 0 #counter to trace vow many ads have status 1 = classified as bird
    for row in session.query(Parse_ads):
        #print('start')
        if session.query(Parsing_bird_or_no.ad_id).filter_by(ad_id=row.ad_id).scalar() == None:
            #print('no entry')
            # step 1 search in title
            for expression in list_of_birds:
                # For each defined regular expression
                res = re.search(str(expression), row.title)  # search in title
                if res != None:  # if there is a match, go on
                    if session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar() == None:  # if there isn't already an entry
                        entry = Parsing_bird_or_no(ad_id=row.ad_id, status_bird=1)
                        entry.insertParse_bird(session)
                        session.commit()
                        c += 1
                        pass
            # step 2 search in description
            for expression in list_of_birds:
                if row.description != None:
                    try:
                        res = re.search(str(expression), row.description)
                    except:
                        print('unknown error')
                        print(row.ad_id)
                        res = None
                if res != None:
                    if session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar() == None:
                        #print('description')
                        entry = Parsing_bird_or_no(ad_id=row.ad_id, status_bird=1)
                        entry.insertParse_bird(session)
                        session.commit()
                        pass
                # last step if no match add status 0
                # if session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar()
            if session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar() == None:
                entry = Parsing_bird_or_no(ad_id=row.ad_id, status_bird=0)
                entry.insertParse_bird(session)
                session.commit()
            #print('before')
        else:
            #print('entry exists')
            #print(session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar(), type(session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar()))
            if session.query(Parsing_bird_or_no.status_bird).filter_by(ad_id=row.ad_id).scalar()==0:
                #print('change')
                status_change = True
                # step 1 search in title
                for expression in list_of_birds:
                    # For each defined regular expression
                    res = re.search(str(expression), row.title)  # search in title
                    if res != None:  # if there is a match, go on
                        if status_change:
                            #print('change stat')
                            Parsing_bird_or_no(ad_id=row.ad_id).update(session)
                            session.commit()
                            c += 1
                            status_change = True
                            pass
                    try:
                        res_des = re.search(str(expression), row.description)
                    except:
                        res_des = None
                    if res_des != None:
                        if status_change:
                            #print('change des')
                            Parsing_bird_or_no(ad_id=row.ad_id).update(session)
                            session.commit()
                            c += 1
                            status_change = True
                            pass
        #print('here')
        with open(f'./results/classification/documentation/bird_{date_parsing}_documentation.json', 'wb') as f:
            f.write(str(doc).encode('utf-8'))