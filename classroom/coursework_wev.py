#
# https://developers.google.com/classroom/guides/manage-classwork?hl=it
# https://developers.google.com/classroom/reference/rest/v1/courses.courseWork
#
import json 
import logging as log
from datetime import datetime, date, timedelta, time
import os
import webbrowser
from termcolor import colored

import global_defs as gd
import classroom_tools as gct
import submission_cl_wev as sbm
import gclass_enrico_pers_utils as geu
import little_utils_generic as lu_g
import little_utils_interface as lu_i
import gclass_enrico_pers_utils as gc_u

import gmail_tools as gmt


class CourseWork_wev:


    def __init__(self, api_coursework_initialized, course_wev, service_initialized, 
    gdrive_service_initialized, dir_download = None):
        self._course_work = api_coursework_initialized
        self._course = course_wev  # course it belongs to, can belong to many but for now
        # we try to associate only to one
        self._classroom_service = service_initialized
        self._gdrive_service = gdrive_service_initialized

        self.id = self._course_work['id']
        self.course_id = self._course.course_id
        self.course_ev_id = geu.course_id_from_title(self._course.name)

        self.max_points = lu_g.dict_get(self._course_work,'maxPoints')
        self.state = self._course_work['state']
        self.title = self._course_work['title']
        self.description = lu_g.dict_get(self._course_work, 'description')
        self.work_type = self._course_work['workType']

        self.due_datetime = lu_g.dict_get(self._course_work,'dueDate')
        self.course_title = course_wev.name
        self.submissions_l = None

        if dir_download is None:
            log.warning("received None dir downlowad, defaulting to current work dir\n{}".format(os.getcwd()))
            dir_download = os.getcwd()
        if False and not os.path.isdir(dir_download): # disabled wrong check
            log.error("exiting, download directory does not exist: {}".format(dir_download))
            exit(1)
        else:
            self.dir_download = os.path.join(course_wev.dir_download, self.title) if dir_download is None else os.path.join(dir_download, self.title)
            # glu.create_dir(self.dir_download)

        # add to global DB
        coursework_db.add(self)


    @staticmethod
    def create_api_coursework(service, course_id, title, description, due_date, due_time = None,
        work_type = gd.CW_WORK_TYPE_ASSIGNMENT, simulated = True):
        """ NOT a factory method, does not create objects of this class """
        body_d ={ 
            "title": title, 
            "description": description, 
            "materials": [],
            "workType": work_type,
            "maxPoints": 100,
            "state": "PUBLISHED"
            }
       
        day_before = due_date - timedelta(days=1)
        body_d['dueDate'] = { "year": day_before.year, "month": day_before.month, "day": day_before.day }
        body_d['dueTime'] = { "hours": 17, "minutes": 45, "seconds": 0, "nanos": 0}

        if simulated:
            log.info("would create with:\ntitle: {}\ndescription: {}\ndue date: {}\nday: {}\ndue time: {}\nwork type: {}"
                .format(title, description, body_d['dueDate'], due_date.strftime('%A'), body_d['dueTime'], work_type))
            return "simulated"
        try:
            coursework = None
            coursework = service.courses().courseWork().create(courseId=course_id, body=body_d).execute()
            log.info('Assignment created with ID {%s}' % coursework.get('id'))
        except Exception as e:
            log.error(e)
            log.error("breakpoint")
        finally:
            return coursework

    @property
    def alternate_link(self):
        return self._course_work['alternateLink']

    @property
    def id(self):
        return self._id
    #
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def title(self):
        return self._title
    #
    @title.setter
    def title(self, value):
        self._title = value

    @property
    def description(self):
        return self._description
    #
    @description.setter
    def description(self, value):
        self._description = value


    @property
    def work_type(self):
        return self._work_type
    #
    @work_type.setter
    def work_type(self, value):
        self._work_type = value

    @property
    def course_id(self):
        return self._course_id
    #
    @course_id.setter
    def course_id(self, value):
        self._course_id = value


    @property
    def course_ev_id(self):
        """not the real ID, one defined by me and not unique"""
        return self._course_ev_id
    #
    @course_ev_id.setter
    def course_ev_id(self, value):
        """not the real ID, one defined by me and not unique"""
        self._course_ev_id = value

    @property
    def course_title(self):
        return self._course_title
    #
    @course_title.setter
    def course_title(self, value):
        self._course_title = value

    @property
    def dir_download(self):
        return self._dir_download

    @dir_download.setter
    def dir_download(self, value):
        self._dir_download = value

    @property
    def state(self):
        return self._state
    #
    @state.setter
    def state(self, value):
        self._state = value

    @property
    def max_points(self):
        return self._max_points
    #
    @max_points.setter
    def max_points(self, value):
        if value is None: 
            self._max_points = 0
        else:            
            self._max_points = int(value)


    @property
    def due_datetime(self):
        return self._due_datetime
    #
    @due_datetime.setter
    def due_datetime(self, valore):
        if valore is None:
            # self._due_date = gd.DATE_NO_DUE_DATE
            self._due_datetime = None
        elif type(valore) == str:
            valore = "da implementare"
            log.error("trovata {} course non implementa ancora la gestione delle stringhe, imposto data farlocca".format(valore))
            self._due_datetime = datetime.strptime(valore, gd.DATE_STR_FORMAT_00)
            exit(1)
        elif isinstance(valore, dict):
            # 'dueDate': {'year': 2021, 'month': 11, 'day': 4}, 'dueTime': {'hours': 13, 'minutes': 20},
            y, m, d = int(valore['year']), int(valore['month']), int(valore['day'])
            self._due_datetime = datetime(y,m,d)
        else: # normally it's a dictionary
            log.error("parameter of unexpected tzpe passed: {}".format(type(valore)))
            log.error("BREAK parameter of unexpected tzpe passed: {}".format(type(valore)))

    @property
    def due_date(self):
        return self._due_datetime.date()


    @property
    def has_due_date(self):
        return self.due_datetime is not None


    @property
    def days_to_due_date(self):
        if self.due_datetime is None:
            return None
        days_to_go = (self.due_datetime.date() - date.today()).days
        return days_to_go

    @property
    def due_days_ago(self):
        if self.days_to_due_date is None:
            return None
        ret = -1*self.days_to_due_date
        return ret


    @property
    def has_expired(self):
        return self.days_to_due_date < 0


    def should_correct(self, days_back = 3):
        if (self.state != gd.CW_STATE_PUBLISHED):
            return False
        if  (self.work_type != gd.CW_WORK_TYPE_ASSIGNMENT):
            return False
        if not self.has_due_date:
            return False
        if self.due_days_ago < 0:  # negative = future
            return False
        if self.due_days_ago > days_back:
            return False
        return True


    @property
    def submissions_l(self):
        if self._submissions_l is None:
            self._submissions_l = []
            # get API submissions list       
            api_submissions = [] # get API submissions
            page_token = None
            while True:
                coursework = self._classroom_service.courses().courseWork()
                response = coursework.studentSubmissions().list(pageToken=page_token, courseId=self._course.course_id,
                                                                courseWorkId=self.id, pageSize=10).execute()
                api_submissions.extend(response.get('studentSubmissions', []))
                page_token = response.get('nextPageToken', None)
                if not page_token:
                    break
            # create member list of submissions from API submissions
            for api_subm in api_submissions:
                subm_wev = sbm.Submission_wev(api_subm, coursework_wev=self, 
                classroom_service_initialized=self._classroom_service,
                gdrive_service_initialized=self._gdrive_service, dir_download=self.dir_download)
                self._submissions_l.append(subm_wev)
        return self._submissions_l
    #
    @submissions_l.setter
    def submissions_l(self, value):
        self._submissions_l = value
    

    @property
    def check_submissions_for_correction_l(self):
        """ analyzes submissions and produces 3 lists"""

        subm_correct_l, subm_autograde_l, subm_ignore_l = [], [], []
        for subm in self.submissions_l:
            if subm.should_evaluate:
                if subm.should_correct: subm_correct_l.append(subm)
                else:subm_autograde_l.append(subm)
            else: subm_ignore_l.append(subm)

        return subm_correct_l, subm_autograde_l, subm_ignore_l


    def check_submissions_attachments_naming(self, email_mandate, max_email = 25):
        
        gmail_service = gmt.get_gmail_service()

        students_mistakes_dic = {}
        for s in self.submissions_l:
            if s.has_attachments:
                for a in s.attachments_l:
                    ok, msgs_l = gc_u.check_attachment_filename(a)
                    if s.student_email not in students_mistakes_dic.keys():
                        students_mistakes_dic[s.student_email] = msgs_l # firs entry
                    else:
                        students_mistakes_dic[s.student_email] += msgs_l # add messages

        if email_mandate >= max_email:
            return email_mandate

        for email, msgs in students_mistakes_dic.items():
            if True or "y" == lu_i.get_y_n("email about naming to {}".format(s.student_email)):
                body = "mail automatica per {}".format(s.student_email)
                body += "\nPossibili errori nei files consegnati"
                body += "\nper assignment '{}'\n".format(self.title)
                body += "\nurl/link {}\n".format(self.alternate_link)
                body += "\n\n".join(msgs)
                msg = gmt.build_message(gd.EMAIL_VIALI_GALILEI, gd.EMAIL_ENRICO200165, 
                    obj = "Possibili errori nei nomi degli attachments (email automatica)"
                    ,body = body, attachments=[])
                # gmt.send_message(service = gmail_service, user_id = "me", message = msg)
                print(" ----- mail body (inveced di inviare) -----\n",body)
                email_mandate += 1
            if email_mandate >= max_email:
                break
            continue # just to breakpoint
        
        return email_mandate

    def correct_submissions(self, force_dir_root_download, gdrive_service_initialized, 
        start_explorer = False, prompt_single = False):

        if prompt_single:
            log.error("prompt_single not yet implemented")
            exit(0)

        dir_download = force_dir_root_download if force_dir_root_download is not None else self.dir_download
        if start_explorer:
            dir_download = lu_g.create_dir(dir_download) # may be modified if illegal characters
            lu_g.open_file_explorer(dir_download)

        print(gd.BANNER_LEV_2.format("",' coursework: "'+colored(self.title, 'yellow')+'" ',""))
        print(self.alternate_link) # to see it in browser
        
        print("----- Description -----")
        if self.description is not None:
            print(self.description)
        print("-----------------------\n")
        webbrowser.open(self.alternate_link)

        should_examine_l, subm_autograde_l, subm_ignore_l = self.check_submissions_for_correction_l
        print(" --- To Correct ---")
        for subm in should_examine_l: print("{}".format(subm.student_email)) 
        print(" --- To Autogr. ---")
        for subm in subm_autograde_l:  print("{:<48} first turned in: {}".format(subm.student_email, subm.first_turned_in))
        print(" --- To Ignore  ---")
        for subm in subm_ignore_l:    print("{:<48} first turned in: {}".format(subm.student_email, subm.first_turned_in))

        for subm in should_examine_l: # [0] list 
            # subm.download_attachments(dir_download, gdrive_service_initialized)
            ret = subm.correct_submission(dir_download, gdrive_service_initialized)
            if ret == 0:
                log.info("asked to exit correction")
                break
        
        grade_4_autograding = gd.GRADE_MINIMUM
        ask_for_each  = True
        for subm in subm_autograde_l: # [1] list 
            cur_grade = grade_4_autograding # if in future want to personalize
            prompt = "autograde: {}".format(cur_grade)
            subm.correction_banner(prompt_left = prompt)
            if lu_i.get_y_n("do you confirm "+prompt) != "y":
                cur_grade = lu_i.get_int("grade for autograding (0 to exit this cw)", 0, gd.GRADE_MAXIMUM)
                if cur_grade == 0:
                    break
            subm.write_grade(cur_grade, grade_type = 0)
        

    def dump_str(self, verbose = False, newLine = False):
        ret = ""
        #ret += gd.dump_class_obj_str(self)
        ret += ""+str(type(self))
        ret += gd.dump_member_str("id", self.id, newLine)
        ret += gd.dump_member_str("title", self.title, newLine)
        ret += gd.dump_member_str("state", self.state, newLine)
        ret += gd.dump_member_str("maxPoints", self.max_points, newLine)
        ret += gd.dump_member_str("alternateLink", self.alternate_link)
        # if verbose:
        #     ret +=" students["
        #     for student in self.get_students():
        #         ret += " "+student.email
        #     ret +=" ]"
        return ret




class CourseworkDB:
    
    by_id = {}

    def __init__(self, service_initialized):
        pass

    def add(self, cw):
        if not isinstance(cw, CourseWork_wev):
            log.error("ignoring, expexted CourseWork_wev object cannot add {}".format(type(cw)))
            return
        self.by_id[cw.id] = cw


    def dump_str(self):
        ret = ""
        ret += "nr. courseworks in db: {}".format(len(self.by_id.keys()))
        return ret



# gclassroom_service e' gestito in modo fragile, qui si assume gia' inizializzato
coursework_db = CourseworkDB(gct.gclassroom_service)

