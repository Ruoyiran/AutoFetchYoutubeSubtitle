# -*- coding:utf-8 -*-
"""
@version: 1.0
@author: Roy
@contact: ruoyi_ran@foxmail.com
@file: html_parser.py
@time: 2018/7/15 16:01
"""

from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.attrs = list()

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            for attr in attrs:
                attr_name = attr[0]
                attr_value = attr[1]
                self.attrs.append((attr_name, attr_value))


if __name__ == "__main__":
    html_code = """ <a href="www.google.com"> google.com</a> <A Href="www.pythonclub.org"> PythonClub </a> <A HREF = "www.sina.com.cn"> Sina </a> """
    hp = MyHTMLParser()
    hp.feed(html_code)
    hp.close()
