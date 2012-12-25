#!/usr/bin/env python2.6
# encoding: utf-8

from BeautifulSoup import BeautifulSoup as BSoup
import urllib2
import re


_opener = urllib2.build_opener()
_opener.addheaders = [('User-agent', 'Mozilla/5.0')]


def _remove_html_tags(html):
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', html)


def load_history(someday):
    formatted_date = someday.strftime("%B_%d")
    html = _opener.open('http://en.wikipedia.org/wiki/'+formatted_date).read()
    history = BSoup(html)
    return history


def _load_ul(li, soup):
    item_dict = {}
    for li in soup.html.body.findAll('ul')[li]:
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
