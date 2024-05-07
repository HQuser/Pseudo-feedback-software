import datetime
import re
import time
from urllib.parse import urlparse

import dateutil
from bs4 import BeautifulSoup


def get_words_from_url(str):
    # url = urlparse(str)
    # words = re.sub('.+(\/)', '', url.path)  # remove domain
    # words = re.split('-', words) # split words
    splits = str.split('/')
    s = splits.pop()  # Get last part of domain
    if s == "":  # if empty get second last
        s = splits.pop()

    words = re.split('-', s)  # split words
    return " ".join(words)


def normalize_encoded_chars(text):
    # normalized = text.encode('UTF-8', errors='replace')
    normalized = str(text)
    normalized = BeautifulSoup(normalized).get_text()
    return normalized


def remove_pre_hyphen_text(text):
    text = text.strip(" ")  # Remove trailing whitespaces
    removed_date = re.sub('.*\s-\s', '', text)  # Remove date from snippet
    return removed_date


def remove_turncated_dots(text):
    stripped_text = text[:-4]
    return stripped_text


def remove_nonwords(text):
    tokens = text.strip().split()
    clean_tokens = [t for t in tokens if re.match(r'[^\W\d]*$', t)]
    return ' '.join(clean_tokens)


def convert_date(date_time):
    d = dateutil.parser.parse(date_time)
    return d.strftime('%d-%b-%Y')  # ==> '24-Sep-2019'


def convert_date_epoc(date_time):
    return time.strftime('%d-%b-%Y', time.localtime(date_time))
