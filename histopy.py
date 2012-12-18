#!/usr/bin/env python2.6
# encoding: utf-8

from BeautifulSoup import BeautifulSoup as BSoup
import urllib2
import re
import datetime
import unicodedata

# soup = {}
# now = datetime.datetime.now()
# today = now.strftime("%B_%d")

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

 
def remove_html_tags(html):
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', html)

def load_history(someday):
    formatted_date = someday.strftime("%B_%d")
    html = opener.open('http://en.wikipedia.org/wiki/'+formatted_date).read()
    soup = BSoup(html)
    return soup

def load_ul(li,soup):
    item_dict = {}
    for li in soup.html.body.findAll('ul')[li]:
        s = remove_html_tags(str(li))        
        try:
            if int(s[0]) > 0:                
                line = s.split('\xe2\x80\x93')
                year = line[0].strip()
                event = line[1].strip()
                item_dict[year] = event
                # events_dict[year] = event.decode('utf-8')
                # nText = unicodedata.normalize( "NFKD", events_dict[year] )
                # print nText
                # print events_dict[year]                
        except:
            pass
    return item_dict



def load_events(soup):
    return load_ul(1,soup)

def load_births(soup):
    return load_ul(2,soup)

def load_deaths(soup):
    return load_ul(3,soup)