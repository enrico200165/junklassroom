from inspect import CO_VARKEYWORDS
import logging as log
from datetime import datetime
import os
from googleapiclient.errors import HttpError
import googleapiclient.discovery
import classroom_tools as gct
import coursework_wev as cw

import student_wev as std
import students_db as stud_db

import global_defs as gd
import global_vars as gv
import little_utils_generic as lug

import little_utils_generic as lu_g
import coursework_wev as crw


class GCourse_wev:

    STATE_ARCHIVED = "ARCHIVED"
    STATE_ACTIVE   = "ACTIVE"

    def __init__(self, initialized_course_object, classroom_service, gdrive_service, enrico_id, dir_download):

        self._course = initialized_course_object
        self.course_id = self._course['id']

        self.owner_id = self._course['ownerId']
        self.name = self._course['name']
        self.course_state = self._course['courseState']

        classroom_service : googleapiclient.discovery.Resource
        gdrive_service : googleapiclient.discovery.Resource
        self._classroom_service = classroom_service
        self._gdrive_service = gdrive_service

        self.teacher_folder_api_d = self._course['teacherFolder'] if 'teacherFolder' in self._course.keys() else None
        self.students_l = self.students_get()
        self._cworks = self.get_course_works() if self.is_owner(enrico_id) else []

        # dovrebbe riceverlo dal genitore, che ancora non esistre, the classroom root account
        # self.dir_download = os.path.join(course_wev.dir_download, self.title) if dir_download is None else os.path.join(dir_download, self.title)
        if not os.path.isdir(dir_download):
            log.error("exiting, download directory does not exist: {}".format(self.dir_download))
            exit(1)
        else:
            self.dir_download = os.path.join(dir_download, self.name)
            #  glu.create_dir(self.dir_download)



    def students_get(self):
        # log.info("GET students per course id {} course title {}".format(self._course_id, self.name))
        results = self._classroom_service.courses().students().list(pageSize=999, courseId=self._course_id).execute()
        students = results.get('students', [])
        students_wev = []
        for s in students:
            stud = std.Student_wev(s, self._classroom_service)
            students_wev.append(stud)
        return students_wev

    @property
    def course_id(self):
        return self._course_id

    @course_id.setter
    def course_id(self, value):
        self._course_id = value

    @property
    def dir_download(self):
        return self._dir_download

    @dir_download.setter
    def dir_download(self, value):
        self._dir_download = value


    @property
    def owner_id(self):
        return self._owner_id

    @owner_id.setter
    def owner_id(self, owner_id):
        self._owner_id = owner_id

    @property
    def name(self):
        return self._name
    #
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def course_state(self):
        return self._course_state
    #
    @course_state.setter
    def course_state(self, value):
        self._course_state = value

    @property
    def is_active(self):
        return self.course_state == self.STATE_ACTIVE

    @property
    def teacher_folder_api_d(self):
        return self._teacher_folder_api_d
    #
    @teacher_folder_api_d.setter
    def teacher_folder_api_d(self, value):
        self._teacher_folder_api_d = value

    def teacher_folder_triple(self):
        if  self.teacher_folder_api_d is None:
            return None, None, None
        return self.teacher_folder_api_d['id'], self.teacher_folder_api_d['title'], self.teacher_folder_api_d['alternateLink'],

    @property
    def students_l(self):
        return self._students
    #
    @students_l.setter
    def students_l(self, value_l):
        self._students = value_l
        for student in self._students:
            gv.students_database.add_by_id(student.id, student)
        return self._students


    def is_owner(self, user_id):
        return self.owner_id == user_id

    @property
    def teachers_list(self):
        if not hasattr(self, "teachers_l"):
            self._teachers_l = []
            results = self._classroom_service.courses().teachers()
            class_teachers_d = results.get(userId='', courseId=self._course_id).execute()
            class_teachers_l = class_teachers_d['teachers']
            for t in class_teachers_l:
                self._teachers_l.append(t)
        return self._teachers_l



    @property
    def course_works_l(self):
        if not hasattr(self, "_course_works_l"):
            course_works_list = self._classroom_service.courses().courseWork().list(pageSize=999, courseId=self.course_id).execute()
            
            if 'courseWork' not in course_works_list.keys():
                self._course_works_l = []
            else:       
                self._course_works_l = []
                for coursework in course_works_list['courseWork']:
                    log.debug("type of coursework variable is {}".format(type(coursework)))
                    cw_wev = cw.CourseWork_wev(coursework, self, self._classroom_service, 
                    self._gdrive_service, self.dir_download)
                    self.course_works_l.append(cw_wev)
        return self._course_works_l


    def cw_up_to_date_l(self, start_deliv_date_str, end_deliv_date_str):
        log.info("requested courses from string date {} to string date {}".format(start_deliv_date_str, end_deliv_date_str))
        start_deliv_date = datetime.strptime(start_deliv_date_str, gd.DATE_STR_FORMAT_00)
        end_deliv_date = datetime.strptime(end_deliv_date_str, gd.DATE_STR_FORMAT_00)
        return_assignm = []
        for assignm in self.course_works_l:
            if  start_deliv_date < assignm.due_date <= end_deliv_date:
                return_assignm.append(assignm)
        return return_assignm


    def course_works_should_correct(self, days_back = 3):
        ret_l = []
        cwork: cw.CourseWork_wev
        for cwork in self.course_works_l:
            if cwork.should_correct(days_back):
                ret_l.append(cwork)
        # sort based on a property
        result = sorted(ret_l, key = lambda d: d.due_date, reverse=False)
        return result

    def create_coursework_series(self, title_specific, description, start_date, week_days_l, end_date, 
        due_time, work_type = gd.CW_WORK_TYPE_ASSIGNMENT, simulated = True):
        """ creates the coursework
        """
        dates_list =  lug.weekly_appointments(start_date, week_days_l, end_date)

        ret = self.create_coursework_series_det(title_specific, description, dates_list, due_time, 
            work_type, simulated = True)
        go_nogo = int(input("1 to actually create assignments"))
        if go_nogo == 1:
            ret = self.create_coursework_series_det(title_specific, description, dates_list, due_time, 
                work_type, simulated)

        return ret


    def create_coursework_series_det(self, title_specific, description, due_dates_l, due_time, 
        work_type = gd.CW_WORK_TYPE_ASSIGNMENT, simulated = True):
        """ creates the coursework
        """
        
        for due_date in due_dates_l:
            title = lug.datestamp(due_date)+ " - Compiti"
            if title_specific is not None and len(title_specific) > 0:
                title += " - "+title_specific
            title += " - [ ev_id:"+str(lug.second_in_day())+" ]"
            ret = crw.CourseWork_wev.create_api_coursework(self._classroom_service, 
            course_id = self.course_id, title = title, description = description, 
                due_date = due_date, due_time = due_time, work_type = work_type,
                simulated = simulated)
        return ret


    def correct_courseworks(self, days_back = 14, max_nr_to_correct = 3,
        classroom_service = None, gdrive_service = None):
        
        classroom_service = self._classroom_service if classroom_service is None else classroom_service
        gdrive_service =    self._gdrive_service    if gdrive_service     is None else gdrive_service

        cw_must_correct_l = self.course_works_should_correct(days_back)        
        for i, cw in enumerate(cw_must_correct_l):
            cw.correct_submissions(None, gdrive_service, start_explorer= True)
            if max_nr_to_correct != 0 and i >= max_nr_to_correct:                
                break
        return i

    def dump_str(self, verbose = False, newLine = False, separator = "\n"):
        ret = ""
        # ret = gd.dump_class_obj_str(self)
        ret += ""+str(type(self))
        ret += separator+gd.dump_member_str("course_id", self.course_id, newLine)
        ret += separator+gd.dump_member_str("name", self.name, newLine)

        ret += separator+gd.dump_member_str("gdrive id", self.teacher_folder_triple()[0], newLine)
        ret += separator+gd.dump_member_str("gdrive title", self.teacher_folder_triple()[1], newLine)
        ret += separator+gd.dump_member_str("gdrive alternateLink", self.teacher_folder_triple()[2], newLine)

        if verbose:
            ret += separator + " students["
            for student in self.get_students():
                ret += " "+student.email
            ret +=" ]"
        return ret
