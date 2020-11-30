#!/usr/bin/env python
# coding=utf-8
# author: T. Pineau
# adapte par: Danny Kohler, Luisa Rodrigues, Jasmin Wyss
# creation: 06.10.2020


import datetime, json
from sqlalchemy import create_engine #pip install sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData, JSON, Table


#~~~~~~~~~~~~~~~~~~~~~Create de base~~~~~~~~~~~~~~~~~~~~~
Base = declarative_base()



#~~~~~~~~~~~~~~~~~~~~~PROJET~~~~~~~~~~~~~~~~~~~~~

class Country(Base) :
    __tablename__ = 'countries'
    id=Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    def insertCountry(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()


class Urls_ads(Base):
    __tablename__ = 'urls_ads'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ad_id = Column(String, unique=True)
    ad_number=Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    status = Column(Integer, default=0)
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    date_updated = Column(DateTime, onupdate=datetime.datetime.now())
    country_id= Column(Integer, ForeignKey("countries.name"))

    #code = relationship("Ads_Codes_tmp", back_populates="urls_ads_tmp", uselist=False)
    country=relationship("Country", backref="urls_ads")
    def insertURL(self, session):
        session.add(self)
        session.commit()

    def urls_ads_update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

class Ads_Codes(Base):
    __tablename__='ads_codes'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    ad_id = Column(String, ForeignKey("urls_ads.ad_id"), unique=True)
    ad_number = Column(Integer, nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    date_updated = Column(DateTime, onupdate=datetime.datetime.now())
    client_code = Column(String, nullable=False)
    status = Column(Integer, default=0)#Parsing yes=1,no=0
    status_image_taken = Column(Integer, default=0)#Image extrait: yes=1, no=0
    status_vendeur_taken = Column(Integer, default=0)#Vendeur extrait: yes=1, no=0


    urls_ads_tmp = relationship("Urls_ads", backref="ads_codes")
    def insertCode(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()




class Parse_ads(Base):
    __tablename__='parse_ads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    date_updated = Column(DateTime, onupdate=datetime.datetime.now())
    ad_id = Column(String, ForeignKey("ads_codes.ad_id"), unique=True)
    ad_number = Column(Integer, nullable=False)
    category = Column(String)
    description = Column(String)
    breed = Column(String)
    age = Column(Integer)
    sex = Column(String)
    primary_color = Column(String)
    secondary_color = Column(String)
    advertiser = Column(String)
    price = Column(Integer)
    payment_forms = Column(String)
    estimated_shipping = Column(String)
    pseudo = Column(String)
    contact_information = Column(String)
    name = Column(String)
    company=  Column(String)
    zip = Column(Integer)
    city = Column(String)
    state = Column(String)
    county = Column(String)
    country = Column(String)
    region = Column(String)
    province = Column(String)
    email = Column(String)
    phone = Column(Integer)
    redirect_website= Column(String)
    status_vendeur_taken = Column(Integer, default=0)

    ads_codes = relationship("Ads_Codes", backref="parse_ads")
    def insertParse_ads(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session) :
        session.delete(self)
        session.commit()

class Parsing_bird_or_no(Base):
    __tablename__ = 'classification_1_parse_bird_or_no'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String, unique=True) #ForeignKey("parse_ads.ad_id")
    status_bird = Column(Integer, default=0)#0: not classified 1: classified

    #parse_ads = relationship("Parse_ads", backref="parse_bird_or_no")
    def insertParse_bird(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()

class MentionedCage(Base):
    __tablename__ = 'classification_1_cage'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String, unique=True) #ForeignKey("parse_ads.ad_id")
    status_cage = Column(Integer, default=0)#0: not classified 1: classified
    status_alerte = Column(Integer, default=0)#0:alright 1: contains words with waarant recheck of classification

    #parse_ads = relationship("Parse_ads", backref="cage")
    def insertCage(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()

class Parsing_Psittaciformes_or_no(Base):
    __tablename__ = 'classification_1_psittaciformes_or_no'
    #H: une même annonce ne match pas plus que 10 noms d'oiseaux différents
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String, unique=True) #ForeignKey("parse_ads.ad_id")
    match_cites_parrot = Column(Integer, default=0)#0: not classified 1: classified
    match_common_parrot = Column(Integer, default=0)#0: not classified 1: classified
    mapping_match = Column(String) #en gros les differents matches_regex separée par ;

    #parse_ads = relationship("Parse_ads", backref="psittaciformes_or_no")
    #mapping_cites = relationship("Mapping", backref="psittaciformes_or_no")
    def insertPsittaciformes(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()

class Mapping(Base):
    __tablename__ = 'mapping_cites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    scientific_name_cites = Column(String)
    common_name = Column(String)
    region = Column(String)
    danger_status_UCIN = Column(String)
    slang = Column(String)
    annex_number_CITES = Column(Integer)
    order = Column(String)
    family = Column(String)
    #pas de relation avec une autre table
    #parse_ads = relationship("Parse_ads", backref="psittaciformes_or_no")

    def insert(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()

class Regex(Base):
    __tablename__ = 'classification_1_regex'
    id = Column(Integer, primary_key=True, autoincrement=True)
    reg = Column(String)
    word = Column(String)


    def insertregex(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()


class Match_Regex_IdMap(Base):
    __tablename__ = 'classification_1_reg_map_match'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_re = Column(Integer) #ForeignKey("classification_1_regex.id")
    id_map = Column(Integer) #ForeignKey("mapping_cites.id")
    #pas de relation avec une autre table
    #mapping_cites = relationship("Mapping", backref="reg_map_match")
    #regex = relationship("Regex", backref="reg_map_match")

    def insertMatch(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()

class Classification_2_Ads(Base):
    __tablename__ = 'classification_2_matching_ads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String,  unique=True)#ForeignKey("parse_ads.ad_id")
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    date_updated = Column(DateTime, onupdate=datetime.datetime.now())
    ids_matching = Column(String)
    parrot=Column(Integer)
    regex = Column(JSON)
    nb_species_matches= Column(Integer)
    #Presence or not
    cage= Column(Integer)
    egg=Column(Integer)
    cites_paper=Column(Integer)
    cites_appendice=Column(Integer)
    status=Column(Integer, default=0)

    def insert(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()

class Classification_3_Ads(Base):
    __tablename__ = 'classification_3_matching_ads'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String,  unique=True)#ForeignKey("parse_ads.ad_id")
    date_created = Column(DateTime, default=datetime.datetime.now(), nullable=False)
    date_updated = Column(DateTime, onupdate=datetime.datetime.now())
    ids_matching = Column(String)
    parrot=Column(Integer)
    regex = Column(JSON)
    nb_species_matches= Column(Integer)
    #Presence or not
    cage= Column(Integer)
    egg=Column(Integer)
    cites_paper=Column(Integer)
    cites_appendice=Column(Integer)
    status=Column(Integer, default=0)

    def insert(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session):
        session.delete(self)
        session.commit()


class Vendor_analyse(Base):
    __tablename__='vendor_analyse'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pseudo = Column(String)
    contact_information = Column(String)
    name = Column(String)
    company=  Column(String)
    zip = Column(Integer)
    city = Column(String)
    state = Column(String)
    county = Column(String)
    country = Column(String)
    region = Column(String)
    province = Column(String)
    email = Column(String)
    email_description = Column(String)
    phone = Column(Integer)
    phone_description = Column(Integer)
    redirect_website= Column(String)
    website_deviate = Column(String)
    status_vendeur_taken = Column(Integer, default=0)
    status_bird = Column(Integer)

    def insertVendor_analyse(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status_bird = newStatus
        session.commit()

    def deleteEntry(self, session) :
        session.delete(self)
        session.commit()


class Ads_clean(Base):
    __tablename__='ads_clean'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String, unique=True)
    ad_number = Column(Integer, nullable=False)
    id_vendor=Column(Integer)
    title = Column(String)
    description = Column(String)
    breed = Column(String)
    age = Column(Integer)
    sex = Column(String)
    primary_color = Column(String)
    secondary_color = Column(String)
    price = Column(Integer)
    currency = Column(String)
    price_in_dollar = Column(String)
    payment_forms = Column(String)

    def insertAds_clean(self, session):
        session.add(self)
        session.commit()

    def update(self, session, newStatus=1):
        self.status = newStatus
        session.commit()

    def deleteEntry(self, session) :
        session.delete(self)
        session.commit()



#~~~~~~~~~~~~~~~~~~~~~Connect the database~~~~~~~~~~~~~~~~~~~~~


engine = create_engine('sqlite:///DATABASES/project.db')
    #j'ai changé ../ pour que ça crée la DB sinon ça marchait pas car pas dans le même dossier [a faire entre Luisa&autres]
    #engine = create_engine('sqlite:///C:\\Users\\Jasmin\\Documents\\GitHub\\IVI-Project\\DATABASES\\project.db') #, echo=True pour les log
    #pour luisa la path est: 'sqlite:////Users/pintorodriguesanaluisa/Desktop/Docs/ESC/4.3/IVI/Projet/IVI-Project/DATABASES/project.db'
    #engine = create_engine('sqlite:///DATABASES/project.db') #, echo=True pour les log
Base.metadata.create_all(engine) #Create the database if it does not exist
Session = sessionmaker(bind=engine)
session = Session()

#~~~~~~~~~~~~~~~Create a table~~~~~~~~~~~~~~~~
#meta = MetaData()
#parse_bird_or_no = Table('parse_bird_or_no', meta,
#                         Column('id', Integer, primary_key = True, nullable=False, autoincrement=True),
#                         Column('ad_id', String(32)),
#                         Column('status_bird', Integer, default=0))
#meta.create_all(engine)
