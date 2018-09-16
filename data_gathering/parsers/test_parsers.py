import unittest
import datetime as dt

from parsers.filter_parser import FilterParser
from parsers.html_parser import AuthorListHtmlParser, AuthorInfoHtmlParser


class TestFilterParser(unittest.TestCase):
    def test_parse(self):
        parser = FilterParser(['1', '3', '5'])
        parsed_data = parser.parse({'1': 1, '2': 2, '3': 3, '4': 4, '5': 5})
        self.assertEqual(len(parsed_data), 1)
        self.assertDictEqual(parsed_data[0], {'1': 1, '3': 3, '5': 5})


class TestHtmlParser(unittest.TestCase):

    def test_author_list_parse(self):
        parser = AuthorListHtmlParser()
        data = '<a class="arow-name c-black" href="/author/30230">Author</a>'
        result = ['/author/30230']
        self.assertEqual(parser.parse(data), result)

    def test_author_info_parse(self):
        parser = AuthorInfoHtmlParser()
        data = """<a href="/author/6602/top-fransua-de-laroshfuko">Книги
<b>43</b></a><span class="stats-item marg-right" title=
Почитатели творчества">
<span class="icon-svg isvg-fav"> <svg style="width:18px;
height:16px;"
viewBox="0 0 18 16" xmlns="http://www.w3.org/2000/svg">
<g fill="none" fill-rule="evenodd"><path class="isvg-inner"
d="m12 7c-.67-1.732-2.547-3-4.5-3-2.543 0-4.5 1.932-4.5 4.5 0
3.529 3.793
6.258 9 11.5 5.207-5.242 9-7.971 9-11.5 0-2.568-1.957-4.5-4.5-
4.5-1.955 0-3.83
1.268-4.5 3" transform="translate(-3-4)"></path> </g> </svg>
</span>1</span>
<span class="stats-item marg-right" title="Читателей"><span
class="icon-svg
isvg-users"> <svg style="width:22px;height:14px;" viewBox="0
0 22 14"
xmlns="http://www.w3.org/2000/svg"> <g fill="none" fill-rule=
evenodd">
<path class="isvg-inner" d="m8 13c-2.333 0-7 1.167-7 3.5v2.499
h14v-2.499c0-2.333
-4.666-3.5-7-3.5m8 0c-.291 0-.617.018-.966.054 1.158.838 1.965
1.963 1.965
3.446v2.499h5.999v-2.499c0-2.333-4.665-3.5-6.998-3.5m-8-8c-1.656
0-3 1.345-3
3 0 1.656 1.344 3 3 3 1.657 0 2.991-1.344 2.991-3 0-1.656-1.334-
3-2.991-3m8
0c-1.658 0-3 1.345-3 3 0 1.656 1.343 3 3 3 1.656 0 2.989-1.344
2.989-3
0-1.656-1.333-3-2.989-3" transform="translate(-1-5)"></path>
</g> </svg>
</span>21</span>
<span class="header-profile-login">Франсуа де Ларошфуко</span>
<div class="group-row-title"><b>Родился: </b>15 сентября 1615 г., Франция</div>
<div class="group-row-title"><b>Умер: </b>1680 г.</div>"""
        result = [
            'Франсуа де Ларошфуко',
            dt.date(1615, 9, 15),
            'Франция',
            dt.date(1680, 1, 1),
            '',
            43,
            0,
            21
        ]
        self.assertEqual(parser.parse(data), result)

if __name__ == '__main__':
    unittest.main()
