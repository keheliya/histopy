# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests # Added requests
# import urllib.request as urllib2 # Commented out
import re
import pickle
import logging
import ssl

# This is a workaround for potential SSL verification issues when fetching data
# from Wikipedia. It disables SSL certificate verification, which might pose
# security risks. Ideally, SSL verification should be properly configured.
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# _opener = urllib2.build_opener() # Commented out
# _opener.addheaders = [('User-agent', 'Mozilla/5.0')] # Commented out
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
            headers = {'User-agent': 'Histopy/1.0 (https://example.com/histopy; histopy@example.com)'}
            response = requests.get(_url + formatted_date, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            html = response.content # Use response.content to get bytes
            _events_calendar[formatted_date] = html
            pickle.dump(_events_calendar, open(_events_list_file, 'wb'))
    else:
        headers = {'User-agent': 'Histopy/1.0 (https://example.com/histopy; histopy@example.com)'}
        response = requests.get(_url + formatted_date, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        html = response.content # Use response.content to get bytes
    
    soup = BeautifulSoup(html, "html.parser")
    result = {}
    section_details = {
        "Events": {"id": "Events", "text_match": "Events"},
        "Births": {"id": "Births", "text_match": "Births"},
        "Deaths": {"id": "Deaths", "text_match": "Deaths"}
    }

    for key, detail in section_details.items():
        item_dict = {}
        ul_tag = None
        
        # Try finding by <span id="..."> first
        header_span_by_id = soup.find('span', id=detail["id"])
        if header_span_by_id:
            logging.info(f"Found header span by ID '{detail['id']}' for section '{key}'.")
            h_tag = header_span_by_id.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if h_tag:
                ul_tag = h_tag.find_next_sibling('ul')
                if not ul_tag:
                    logging.warning(f"Found h_tag for ID '{detail['id']}' but no next sibling ul. h_tag: {h_tag.prettify()}")
            else:
                logging.warning(f"Found span by ID '{detail['id']}' but it's not within an H tag.")
        
        # If not found by ID, try finding by H2 text content
        if not ul_tag:
            logging.info(f"Span ID '{detail['id']}' method failed or didn't find UL for '{key}'. Trying H2 text match '{detail['text_match']}'.")
            all_h2s = soup.find_all('h2')
            for h2 in all_h2s:
                # Check direct text of H2 or text of a span directly within H2
                h2_text_content = h2.get_text(strip=True)
                # Sometimes the text is inside a span like <span class="mw-headline">Events</span>
                # Or <span class="mw-headline" id="Events">Events</span>
                # Or just <h2>Events</h2>
                # So we check h2.get_text() and also if a span inside has the ID.
                
                headline_span = h2.find('span', class_='mw-headline')
                span_text = headline_span.get_text(strip=True) if headline_span else ""

                if detail["text_match"] in h2_text_content or detail["text_match"] in span_text :
                    # More specific check: ensure the found text is likely the main title, not a sub-mention.
                    # For example, the span text should be exactly the target, or the h2 text starts with it.
                    if span_text == detail["text_match"] or h2_text_content.startswith(detail["text_match"]):
                        logging.info(f"Found section '{key}' by H2 text match: '{h2.get_text(strip=True)}'.")
                        # ul_tag = h2.find_next_sibling('ul') # OLD LINE
                        
                        # NEW LOGIC to find the next UL, not necessarily an immediate sibling
                        found_ul_for_h2 = None
                        for sibling in h2.find_next_siblings():
                            if sibling.name == 'ul':
                                found_ul_for_h2 = sibling
                                break # Found the first UL sibling
                            # Optional: if another H2 is encountered before a UL, stop for this section
                            if sibling.name == 'h2':
                                logging.warning(f"Encountered another H2 before finding UL for section '{key}' after H2: {h2.prettify()}")
                                break
                        ul_tag = found_ul_for_h2
                        
                        if ul_tag:
                            logging.info(f"Found ul_tag for section '{key}' via H2 text match (flexible sibling search).")
                        else:
                            logging.warning(f"Found H2 for '{key}' by text, but no UL found among next siblings. H2: {h2.prettify()}")
                        break # Found and processed (or failed to process) the H2 for this section
                    else:
                        logging.debug(f"H2/Span text '{h2_text_content}'/'{span_text}' contains but not exact match for '{detail['text_match']}'. Skipping.")
            if not ul_tag:
                 logging.warning(f"Section '{key}' (text: '{detail['text_match']}') not found via H2 text search either.")


        if ul_tag:
            for li in ul_tag.find_all('li', recursive=False):
                res = li.text.split(" ", 1)
                if len(res) > 1:
                    year = res[0].strip()
                    description = res[1].strip()
                    if re.match(r'^\d+(?:[ ]?BC)?$', year, re.IGNORECASE) or year.lower() == "unknown":
                        item_dict[str(year.encode('utf-8').decode("utf-8"))] = str(
                            description.encode('utf-8').decode("utf-8"))
                    else:
                        logging.debug(f"Skipping line in {key} - year format invalid: '{li.text}'")
                else:
                    logging.debug(f"Skipping line in {key} - unexpected format: '{li.text}'")
        else:
            logging.warning(f"No ul_tag found for section '{key}' by any method.")
            
        result[key] = item_dict

    return result


def load_events(loaded_history):
    return loaded_history.get('Events', {}) # Use .get for safety


def load_births(loaded_history):
    return loaded_history.get('Births', {}) # Use .get for safety


def load_deaths(loaded_history):
    return loaded_history.get('Deaths', {}) # Use .get for safety
