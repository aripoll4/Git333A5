class Course:
    def __init__(self, course_desc, classid):
        self._course_desc = course_desc
        self._classid = classid

    def get_course_desc(self):
        return self._course_desc

    def get_classid(self):
        return self._classid
