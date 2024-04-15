class DetailQuery:

    def __init__(self, classid, query_type):
        self._classid = classid
        self._query = query_type

    def get_classid(self):
        return self._classid

    def get_query_type(self):
        return self._query
