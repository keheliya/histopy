#!/usr/bin/env python2.6
# encoding: utf-8

from BeautifulSoup import BeautifulSoup as BSoup
import urllib2
import re
import pickle
import logging


_opener = urllib2.build_opener()
_opener.addheaders = [('User-agent', 'Mozilla/5.0')]
_events_calendar = {}
_events_list_file = 'events.data'
_url = 'http://en.wikipedia.org/wiki/'
logging.basicConfig(
    filename='log_histopy.txt', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    with open(_events_list_file) as f:
        _events_calendar = pickle.load(f)
except IOError as e:
    logging.debug(
        'Cache file does not exist. Creating new file as: '+_events_list_file
    )
    pickle.dump(_events_calendar, open(_events_list_file, 'wb'))


def _remove_html_tags(html):
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', html)


def load_history(someday, caching=True):
    formatted_date = someday.strftime("%B_%d")
    if (caching):
        try:
            with open(_events_list_file) as f:
                _events_calendar = pickle.load(f)
        except IOError as e:
            logging.Error('File I/O Error occured: '+e)

        if formatted_date in _events_calendar:
            logging.debug(formatted_date + ' exists in calendar')
            html = _events_calendar[formatted_date]
        else:
            html = _opener.open(_url+formatted_date).read()
            _events_calendar[formatted_date] = html
            pickle.dump(_events_calendar, open(_events_list_file, 'wb'))
    else:
        html = _opener.open(url+formatted_date).read()
    text = BSoup(html).html.body.findAll('ul')
    return text


def _load_ul(li, text):
    item_dict = {}
    for li in text[li]:
        s = _remove_html_tags(str(li))
        try:
            if int(s[0]) > 0:
                line = s.split('\xe2\x80\x93')
                year = line[0].strip()
                event = line[1].strip()
                item_dict[year] = event
        except:
            pass
    return item_dict


def load_events(loaded_history):
    return _load_ul(1, loaded_history)


def load_births(loaded_history):
    return _load_ul(2, loaded_history)


def load_deaths(loaded_history):
    return _load_ul(3, loaded_history)
