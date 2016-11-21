# encoding: utf-8

import histopy
import datetime
import random

print ('What happened on this day in history?')
today = datetime.datetime.now()
today_in_history = histopy.load_history(today)

events = histopy.load_events(today_in_history)
random_year = random.choice(list(events))
event = events[random_year]
print ('On a day like today but in '+random_year+', '+event)

deaths = histopy.load_deaths(today_in_history)
random_year = random.choice(list(deaths))
death = deaths[random_year]
print (death+', died on a day like today in '+random_year)

births = histopy.load_births(today_in_history)
random_year = random.choice(list(births))
birth = births[random_year]
print ('On a day like today in '+random_year+', '+birth+', was born.')
