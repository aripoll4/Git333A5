#!/usr/bin/env python

#-----------------------------------------------------------------------
# courseoverview.py
# Author: Wangari Karani, Alfred Ripoll
#-----------------------------------------------------------------------

class CourseOverview:
    def __init__(self, clsid, dept, num, area, title, query_type):
        self._clsid = clsid
        self._dept = dept
        self._num = num
        self._area = area
        self._title = title
        self._query_type = query_type

    def get_clsid(self):
        return self._clsid

    def get_dept(self):
        return self._dept

    def get_num(self):
        return self._num

    def get_area(self):
        return self._area

    def get_title(self):
        return self._title

    def get_query_type(self):
        return self._query_type
