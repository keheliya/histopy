#!/usr/bin/env python2.6
# encoding: utf-8

from histopy import *
import datetime
import random

print 'What happened on this day in history?'
today = datetime.datetime.now()
today_in_history = load_history(today)

events = load_events(today_in_history)
random_year = random.choice(events.keys())
event = events[random_year]
print 'On a day like today but in '+random_year+', '+event

deaths = load_deaths(today_in_history)
random_year = random.choice(deaths.keys())
death = deaths[random_year]
print death+', died on a day like today in '+ random_year
    
births = load_births(today_in_history)
random_year = random.choice(births.keys())
birth = births[random_year]
print 'On a day like today in '+random_year+', '+birth+', was born.'