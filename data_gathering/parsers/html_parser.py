from parsers.parser import Parser
from bs4 import BeautifulSoup
import re
import datetime as dt


class AuthorListHtmlParser(Parser):

    def parse(self, data):
        """
        Parses html text and extracts field values
        :param data: html text (page)
        :return: a list of urls with author data
        plus continuation flag
        """
        soup = BeautifulSoup(data, 'html.parser')

        # extract href from
        # <a class=\"arow-name c-black\" href=\"\/author\/30230\">...</a>
        object_list = soup.find_all('a', {'class': 'arow-name c-black'})
        if not object_list:
            raise Parser.IncorrectFormat(data)

        return [x.get('href') for x in object_list]


class AuthorInfoHtmlParser(Parser):

    def parseDate(self, d):
        date, place = '', ''
        if d:
            splitted = list(map(str.strip, d.split(',', 1)))
            if len(splitted) == 2:
                date, place = splitted
            else:
                date, = splitted
            # 15 сентября 1904 г.
            # 1998 г.
            m = re.fullmatch(r"(\d{1,2})?\s*(\w*)\s*(\d{4}).*", date)
            if m:
                day = int(m.group(1)) if m.group(1) else 1
                month = m.group(2)
                if month == 'января':
                    month = 1
                elif month == 'февраля':
                    month = 2
                elif month == 'марта':
                    month = 3
                elif month == 'апреля':
                    month = 4
                elif month == 'мая':
                    month = 5
                elif month == 'июня':
                    month = 6
                elif month == 'июля':
                    month = 7
                elif month == 'августа':
                    month = 8
                elif month == 'сентября':
                    month = 9
                elif month == 'октября':
                    month = 10
                elif month == 'ноября':
                    month = 11
                elif month == 'декабря':
                    month = 12
                else:
                    month = 1

                year = int(m.group(3))
                date = dt.date(day=day, month=month, year=year)
            else:
                # 14 января
                m = re.fullmatch(r"(\d{1,2})?\s*(\w*).*", date)
                if m:
                    day = int(m.group(1)) if m.group(1) else 1
                    month = m.group(2)
                    if month == 'января':
                        month = 1
                    elif month == 'февраля':
                        month = 2
                    elif month == 'марта':
                        month = 3
                    elif month == 'апреля':
                        month = 4
                    elif month == 'мая':
                        month = 5
                    elif month == 'июня':
                        month = 6
                    elif month == 'июля':
                        month = 7
                    elif month == 'августа':
                        month = 8
                    elif month == 'сентября':
                        month = 9
                    elif month == 'октября':
                        month = 10
                    elif month == 'ноября':
                        month = 11
                    elif month == 'декабря':
                        month = 12
                    else:
                        month = 1

                    year = 2000  # default year
                    date = dt.date(day=day, month=month, year=year)
                else:
                    place = date
                    date = ''

        return date, place

    def parse(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        obj = soup.find('span', {'class': "header-profile-login"})
        if not obj:
            raise Parser.IncorrectFormat(data)

        name = obj.text.strip()

        object_list = soup.find_all('a')
        if not object_list:
            raise Parser.IncorrectFormat(data)

        num_books = 0
        for obj in object_list:
            m = re.fullmatch(r"Книги\s*(\d+)\s*", obj.text)
            if m:
                num_books = int(m.group(1))
                break

        object_list = soup.find_all('div', {'class': "group-row-title"})
        if not object_list:
            raise Parser.IncorrectFormat(data)

        birth = None
        death = None
        for obj in object_list:
            if not birth:
                m = re.fullmatch(r"(?:Родился|Родилась):\s*(.*)", obj.text)
                if m:
                    birth = m.group(1)
            if not death:
                m = re.fullmatch(r"(?:Умер|Умерла):\s*(.*)", obj.text)
                if m:
                    death = m.group(1)
            if birth and death:
                break

        birth_date, birth_place = self.parseDate(birth)
        birth_place = re.sub(r'\s+', ' ', birth_place).strip()
        death_date, death_place = self.parseDate(death)
        death_place = re.sub(r'\s+', ' ', death_place).strip()

        obj = soup.find('span', {
                'class': "stats-item marg-right",
                'title': 'Почитатели творчества'
            })

        adepts = int(obj.text if obj is not None else 0)

        obj = soup.find('span', {
                'class': "stats-item marg-right",
                'title': 'Читателей'
            })

        readers = int(obj.text if obj is not None else 0)

        return [
            name, birth_date, birth_place, death_date,
            death_place, num_books, adepts, readers]
