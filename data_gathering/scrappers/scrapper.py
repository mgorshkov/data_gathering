import logging
import requests
import datetime as dt
import time

from parsers.html_parser import AuthorListHtmlParser, AuthorInfoHtmlParser

logger = logging.getLogger(__name__)


class Scrapper(object):
    USER_AGENT = """Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) """
    """Gecko/20100101 Firefox/62.0"""

    class PageNotAvailable(Exception):
        def __init__(self, url):
            self.url = url

    def __init__(self):
        self.author_list_parser = AuthorListHtmlParser()
        self.authors_parser = AuthorInfoHtmlParser()
        self.author_urls = set()
        self.authors = {}
        self.liveLibId = None

    def scrap_process(self, storage_authors, storage_author_info):
        if storage_authors.exists():
            for line in storage_authors.read_data():
                self.author_urls.add(line)
        else:
            self.scrap_authors(storage_authors)

        if storage_author_info.exists():
            for line in storage_author_info.read_data():
                splitted = line.split('\t')
                url = splitted[0]
                info = splitted[1:]
                self.authors[url] = info
        self.scrap_author_info(storage_author_info)

    def scrap_authors(self, storage):
        self.scrap_start_page(storage)

        date = dt.date(2018, 1, 1)
        while date <= dt.date(2018, 12, 31):
            logger.info("Date {date} started".format(date=date))

            page = 1
            while self.scrap_page(storage, date, page):
                page += 1

            logger.info("Date {date} processed".format(date=date))

            date = date + dt.timedelta(days=1)

    def scrap_start_page(self, storage):
        url = 'https://www.livelib.ru/authors'
        headers = {
            'User-Agent': Scrapper.USER_AGENT,
            'Accept-Encoding': 'utf-8'
        }

        cookies = self.get_cookies()
        response = requests.get(url, headers=headers, cookies=cookies)
        if not response.ok:
            logger.error(response.content)
            raise Scrapper.PageNotAvailable(url)

        self.liveLibId = response.cookies['LiveLibId']

        logger.info("Start page processed")

    def get_cookies(self):
        cookies = {
            'cto_lwid':  '29b43342-f3ec-4102-96ca-c3308977172c',
            'fffix': '1',
            'has_agreed': '1',
            'iwatchyou': 'b323d55fc41c3870496bd18f14aa28db',
            'll_nvis': '1',
            'serviceLLid': 'ptl2b35v3ffun0avq5o6kj38g3',
            'tmr_detect': '0|1537003831707'
        }

        if self.liveLibId:
            cookies.update({'LiveLibId': self.liveLibId})
        return cookies

    def scrap_page(self, storage, date, page):
        url = 'https://www.livelib.ru/author/born'
        headers = {
            'User-Agent': Scrapper.USER_AGENT,
            'Accept-Encoding': 'utf-8',
            'Referer': 'https://www.livelib.ru/authors',
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            'current_date': date.strftime('%Y-%m-%d'),
            'is_new_design': 'll2015b',
            'page_no': page
        }
        assert self.liveLibId
        cookies = self.get_cookies()
        response = requests.post(
            url, data=params, headers=headers, cookies=cookies)
        if not response.ok:
            logger.error(response.content)
            raise Scrapper.PageNotAvailable(url)

        json = response.json()
        author_urls = self.author_list_parser.parse(json["content"])
        end_data = bool(json["end_data"])

        for url in author_urls:
            if url not in self.author_urls:
                self.author_urls.add(url)
                storage.append_data(url)

        logger.info("Page {page} processed".format(page=page))

        return not end_data

    def scrap_author_info(self, storage):
        for url in self.author_urls:
            if url in self.authors:
                continue

            headers = {
                'User-Agent': Scrapper.USER_AGENT,
                'Accept-Encoding': 'utf-8'
            }

            full_url = 'https://www.livelib.ru' + url
            logger.info(full_url)

            cookies = self.get_cookies()
            response = requests.get(full_url, headers=headers, cookies=cookies)
            if not response.ok:
                logger.error(response.content)
                raise Scrapper.PageNotAvailable(url)

            if not self.liveLibId:
                self.liveLibId = response.cookies['LiveLibId']

            author_info = self.authors_parser.parse(response.content)
            self.authors[url] = author_info
            author_info.insert(0, url)
            storage.append_data('\t'.join(map(str, author_info)))

            logger.info("Author {} processed".format(url))
