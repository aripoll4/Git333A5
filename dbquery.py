#!/usr/bin/env python

#----------------------------------------------------
# dbquery.py
# Authors: Author: Wangari Karani, Alfred Ripoll               
#----------------------------------------------------

import sys
import sqlite3
import contextlib
import coursedetails
import courseoverview

DATABASE_URL = 'file:reg.sqlite?mode=ro'

class DBQuery:
    @staticmethod
    def a1reg(dept, num, area, title):
        try:
            with sqlite3.connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
                with contextlib.closing(connection.cursor()) as cursor:
                    class_info = []
                    stmt_str = "SELECT classid, dept, coursenum, area, title"
                    stmt_str += " FROM classes, courses, crosslistings"
                    stmt_str += " WHERE classes.courseid = courses.courseid"
                    stmt_str += " AND classes.courseid = crosslistings.courseid"

                    if dept != None:
                        dept = '%' + dept.replace("%", "/%").replace("_", "/_").lower() + '%'
                        stmt_str += " AND crosslistings.dept LIKE ? "
                        class_info.append(dept)
                    if num != None:
                        num = '%' + num.replace("%", "/%").replace("_", "/_").lower() + '%'
                        stmt_str += " AND crosslistings.coursenum LIKE ? "
                        class_info.append(num)
                    if area != None:
                        area = '%' + area.replace("%", "/%").replace("_", "/_").lower() + '%'
                        stmt_str += " AND courses.area LIKE ?"
                        class_info.append(area)
                    if title != None:
                        title = '%' + title.replace("%", "/%").replace("_", "/_").lower() + '%'
                        stmt_str += " AND courses.title LIKE ? "
                        class_info.append(title)

                    if dept == None and num == None and area == None and title == None:
                        stmt_str += " ORDER by dept, coursenum, classid"
                    else:
                        stmt_str += " ESCAPE '/' ORDER by dept, coursenum, classid"

                    cursor.execute(stmt_str, class_info)
                    row = cursor.fetchone()
                    overviews = []

                    while row != None:
                        course  = courseoverview.CourseOverview(row[0], row[1], row[2], row[3], row[4])
                        overviews.append(course)
                        row = cursor.fetchone()
                    
                    return True, overviews
                    # returns true, and a list of overviews

        except Exception as ex:
            print(ex, file=sys.stderr)
            return False, ex

    #----------------------------------------------------------------------

    @staticmethod
    def a1regdetails(classid):
        print(classid)
        try:
            with sqlite3.connect(DATABASE_URL, isolation_level=None,uri=True) as connection:
                with contextlib.closing(connection.cursor()) as cursor:
                    stmt_str = "SELECT classes.courseid, days, starttime, endtime, bldg, roomnum,"
                    stmt_str += " dept, coursenum, area, title, descrip, prereqs"
                    stmt_str += " FROM classes, courses, crosslistings"
                    stmt_str += " WHERE classes.courseid = courses.courseid"
                    stmt_str += " AND classes.courseid = crosslistings.courseid"
                    stmt_str += " AND classid = ?"

                    cursor.execute(stmt_str, [classid])
                    row = cursor.fetchone()
                    print('made it here 1')
                    
                    if row == None:
                        print('row is none')
                        err_str = "Non-existing classid"
                        print(err_str, file=sys.stderr)
                        return False, err_str 
                        #returns false, and an error string

                                           
                    crsid = str(row[0])
                    days = str(row[1])
                    sttime = str(row[2])
                    endtime = str(row[3])
                    bldg = str(row[4])
                    rm = str(row[5])

                    print('made it here 2')
                    

                    dept_str = 'SELECT dept, coursenum, courses.courseid'
                    dept_str += ' FROM classes, crosslistings, courses'
                    dept_str += ' WHERE classes.courseid = courses.courseid'
                    dept_str += ' AND courses.courseid = crosslistings.courseid'
                    dept_str += ' AND classes.classid LIKE ?'
                    dept_str += ' ORDER BY dept, coursenum'
                    cursor.execute(dept_str, [classid])
                    dept_row = cursor.fetchone()
                    depts_crsnum = []

                    print('made it here 3')

                    while dept_row is not None:
                        dept = dept_row[0] + " "
                        dept += str(dept_row[1])
                        depts_crsnum.append(dept)
                        dept_row = cursor.fetchone()

                    area = str(row[8]) 
                    title = str(row[9]) 
                    description = str(row[10]) 
                    prereqs = str(row[11])

                    profs_str = 'SELECT profname, coursesprofs.profid, classes.courseid'
                    profs_str += ' FROM profs, coursesprofs, classes '
                    profs_str += ' WHERE coursesprofs.profid = profs.profid '
                    profs_str += ' AND coursesprofs.courseid = classes.courseid'
                    profs_str += ' AND classes.classid LIKE ?'
                    profs_str += ' ORDER by profname'

                    cursor.execute(profs_str, [classid])
                    profs_row = cursor.fetchone()
                    profs = []

                    while profs_row is not None:
                        profs.append(str(profs_row[0]))
                        profs_row = cursor.fetchone()

                    #make changes for multiple depts
                    crsdetails = coursedetails.CourseDetails(crsid, days, sttime, 
                        endtime, bldg, rm , depts_crsnum, area, title, description, prereqs, profs)

                    return True, crsdetails
                    # returns true, and a list of details
        except Exception as ex:

            print(ex, file=sys.stderr)
            return False, ex
