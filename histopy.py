# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib.request as urllib2
import re
import pickle
import logging
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

_opener = urllib2.build_opener()
_opener.addheaders = [('User-agent', 'Mozilla/5.0')]
_events_calendar = {}
_events_list_file = 'events.data'
_url = 'https://en.wikipedia.org/wiki/'
logging.basicConfig(
    filename='log_histopy.txt', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    with open(_events_list_file, 'rb') as f:
        _events_calendar = pickle.load(f)
except IOError as e:
    logging.debug(
        'Cache file does not exist. Creating new file as: ' + _events_list_file
    )
    pickle.dump(_events_calendar, open(_events_list_file, 'wb'))


def _remove_html_tags(html):
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', html)


def load_history(someday, caching=True):
    formatted_date = someday.strftime("%B_%d")
    if caching:
        try:
            with open(_events_list_file, 'rb') as f:
                _events_calendar = pickle.load(f)
        except IOError as e:
            logging.Error('File I/O Error occured: ' + e)

        if formatted_date in _events_calendar:
            logging.debug(formatted_date + ' exists in calendar')
            html = _events_calendar[formatted_date]
        else:
            html = _opener.open(_url + formatted_date).read().decode('utf-8', 'ignore').encode('ascii', 'ignore')
            _events_calendar[formatted_date] = html
            pickle.dump(_events_calendar, open(_events_list_file, 'wb'))
    else:
        html = _opener.open(_url + formatted_date).read().decode('utf-8', 'ignore').encode('ascii', 'ignore')
    uls = BeautifulSoup(html, "html.parser").html.body.findAll('ul')
    result = {}

    for i in [1, 2, 3]:
        item_dict = {}
        for li in uls[i].findAll('li'):
            res = li.text.split(" ", 1)
            item_dict[str(res[0].strip().encode('utf-8').decode("utf-8"))] = str(
                res[1].strip().encode('utf-8').decode("utf-8"))
        result[i] = item_dict
    return result


def load_events(loaded_history):
    return loaded_history[1]


def load_births(loaded_history):
    return loaded_history[2]


def load_deaths(loaded_history):
    return loaded_history[3]
