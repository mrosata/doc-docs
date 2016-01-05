"""
Doc Docs >> 2015 - 2016
    by: Michael Rosata << doc_doc/public/creator/doc_scraper.py

------
This module uses beautifulsoup4 to scrape preview information from websites for display as news.
Important information includes the og:image and any description

Installed `lxml` which required `libxml2`

"""

import requests
import html5lib
from bs4 import BeautifulSoup

# url = "http://www.onethingsimple.com/some-article-with-a$"
# bs = BeautifulSoup(urllib2.urlopen(url))


def empty_ogmeta():
    og_data = {
        "image": '',
        "title": '',
        "url": '',
        "site_type": '',
        "locale": '',
        "locale_alternate": '',
        "site_name": '',
        "description": '',
        "determiner": '',
        "video": '',
        "audio": ''
    }
    return og_data


def fetch_meta(url):
    """
    Gets the meta values from a url so that we can have an image and description for the page.
    In the future the url from this might replace the one in the database. I want to look into the pros and cons of
    that strategy though.
    :param url:
    :return:
    """
    og_data = empty_ogmeta()
    page_request = requests.get(url)
    if page_request.ok is not True:
        return og_data

    soup = BeautifulSoup(page_request.content, 'html.parser')
    for tag in og_data:
        html_page = page_request.content
        _tag = tag.replace("locale_alternate", "locale:alternate")
        _tag = tag.replace("site_type", "type")
        meta = soup.find("meta", {"property": "og:{0}".format(_tag)})

        # If the meta tag is present in the page then we'll use that for the db
        if meta is not None:
            og_data[tag] = meta["content"]
        else:
            if tag == 'title' and soup.title is not None:
                og_data[tag] = soup.title.get_text()
            if tag == 'description':
                meta = soup.find("meta", {"property": "description"})
                if meta is None:
                    meta = soup.find("meta", {"property": "keywords"})
                if meta is not None:
                    og_data[tag] = meta["content"]

    return og_data

