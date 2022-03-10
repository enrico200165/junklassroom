# https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions
# https://developers.google.com/classroom/guides/manage-classwork?hl=it
#
#
from datetime import datetime
from datetime import date
import email
from msilib.schema import PublishComponent
import os
import logging

from logging import StringTemplateStyle
from re import match
from termcolor import colored

import global_defs as gd
import global_vars as gv


import little_utils_gdrive as gdrlu
import little_utils_generic as lu_g
import little_utils_interface as lu_i
import gclass_enrico_pers_utils as gc_u
#import student_wev as stud
import students_db as std_db
import submission_attach_cl_wev as sat

log = gd.log


class Submission_wev:


    def __init__(self, api_submission_initialized, coursework_wev, classroom_service_initialized, 
    gdrive_service_initialized, dir_download = None):

        self._api_submission = api_submission_initialized
        self.user_id = api_submission_initialized['userId']

        self._coursework_wev = coursework_wev
        self.coursework_title = coursework_wev.title
        self.course_title = coursework_wev.course_title

        self.coursework_id = self._coursework_wev.id 
        self.course_id = self._coursework_wev.course_id

        self._classroom_service = classroom_service_initialized
        self._gdrive_service_initialized = gdrive_service_initialized

        self.student = self.user_id
        self.coursework_type = api_submission_initialized['courseWorkType']
        self.id = api_submission_initialized['id']
        self.state = lu_g.dict_get(api_submission_initialized,'state')

        self.creation_time =None
        self.first_turned_in = None
        self.last_turned_in = None

        self.assigned_grade = lu_g.dict_get(api_submission_initialized,'assignedGrade')
        self.late = lu_g.dict_get(api_submission_initialized,'Late')
        if 'submissionHistory' in api_submission_initialized.keys():
            self.set_submission_history(api_submission_initialized)
        try: 
            gd.log.debug("subm id: {} userId: {} creationTime: {} updateTime: {}".format(
                lu_g.dict_get(api_submission_initialized,'id'), 
                lu_g.dict_get(api_submission_initialized,'userId'),
                lu_g.dict_get(api_submission_initialized,'creationTime'),
                lu_g.dict_get(api_submission_initialized,'updateTime')))
        except KeyError as e:
            gd.log.error(e)

        attachments = []        
        for k in api_submission_initialized['assignmentSubmission'].keys():
            if k == "attachments":
                for attachment in api_submission_initialized['assignmentSubmission']['attachments']:
                    if 'driveFile' not in attachment.keys():
                        log.warning("attachment key not found IGNORING\nstudent: {}\ncoursework: {}"
                        .format(self.student,self.coursework_title))
                        continue
                    attachments.append(attachment)
        self.attachments_l = attachments

        if dir_download is None:
            dir_download = self._coursework_wev.dir_download
        
        self.dir_download = os.path.join(dir_download, self.student.email.split("@")[0])
        # glu.create_dir(self.dir_download)
        # log.info("dumping the IDs to check I did not get them mixed up"+"\ncourse: {}\ncwork:  {}\nsubmi:  {}".format(self.id, self.coursework_id, self.course_id ))


    def set_submission_history(self, api_submission_initialized):
        """
        Not interested in replicating the structure
        Extract, as simple members: 
        latest points, delay in days,
        first_turned_in: to detect who was too fast and has probably copied from a colleague 
        """
        assert 'submissionHistory' in api_submission_initialized.keys()

        # list with elements of two types, states and grades
        self.submission_history_l = api_submission_initialized['submissionHistory']
        for submission_history in self.submission_history_l:
            if 'stateHistory' in submission_history.keys():
                state_history = submission_history['stateHistory']
                tmsp = state_history['stateTimestamp']                    
                state = state_history['state']
                if state =='TURNED_IN':
                    if self.first_turned_in is None:
                        self.first_turned_in = tmsp
                    self.last_turned_in = tmsp
                elif state == 'CREATED':
                    self.creation_time =  tmsp
                else:
                    gd.log.debug("ignoring history state: {} - {} - '{}'".format(state, self.student_email, self.coursework_title))
                    pass
            elif 'gradeHistory' in submission_history.keys():
                grade_history = submission_history['gradeHistory']
                grade_change_type = grade_history['gradeChangeType']
                self._max_points = lu_g.dict_get(submission_history,'maxPoints')
                self._points_earned = grade_history['pointsEarned'] if 'pointsEarned' in grade_history.keys() else None
                if grade_change_type == "":
                    pass
                else:
                    # gd.log.info("no specific processing for grade_change_type: "+grade_change_type)
                    pass
            else:
                gd.log.error("expected keys not found in submission history")

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def course_id(self):
        return self._course_id
    @course_id.setter
    def course_id(self, value):
        self._course_id = value

    @property
    def coursework_id(self):
        return self._coursework_id
    @coursework_id.setter
    def coursework_id(self, value):
        self._coursework_id = value

    @property
    def user_id(self):
        return self._user_id
    @user_id.setter
    def user_id(self, value):
        self._user_id = value


    @property
    def student(self):
        return self._student
    #
    @student.setter
    # note that we pass the id not the course object
    def student(self, student_id):
        student = gv.students_database.stud_by_id(self.user_id)
        if student is None:
            log.error("student not found in students DB, setting it to None")
            gv.students_database.dump_to_console()
        self._student = student

    @property
    def coursework_type(self):
        return self._coursework_type
    @coursework_type.setter
    def coursework_type(self, value):
        self._coursework_type = value

    @property
    def coursework_title(self):
        return self._coursework_title
    @coursework_title.setter
    def coursework_title(self, value):
        self._coursework_title = value

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, value):
        self._state = value


    @property
    def due_date(self):
        return self._coursework_wev.due_date

    @property
    def creation_time(self):
        return self._creation_time
    #
    @creation_time.setter
    def creation_time(self, value):
        # self._creation_time = gd.DATE_NO_DUE_DATE if value is None else glu.string2date(value)
        self._creation_time = None if value is None else lu_g.string2date(value)

    @property
    def dir_download(self):
        return self._dir_download

    @dir_download.setter
    def dir_download(self, value):
        self._dir_download = value

    @property
    def first_turned_in(self):
        return self._first_turned_in
    #
    @first_turned_in.setter
    def first_turned_in(self, value):
        self._first_turned_in = lu_g.string2date(value)

    @property
    def last_turned_in(self):
        return self._last_turned_in
    #
    @last_turned_in.setter
    def last_turned_in(self, value):
        self._last_turned_in = lu_g.string2date(value)

    @property
    def is_turned_in(self):
        return self._first_turned_in != None

    @property
    def late(self):
        # misleading given that I anticipate the due date of gd.SUBMISSION_DELTA
        return self._late
    #
    @late.setter
    def late(self, value):
        self._late = value

    @property
    def days_late(self):

        if not self.is_turned_in:
            dates_delta = datetime.today().date()      - self._coursework_wev.due_date
        else:
            dates_delta = self.first_turned_in.date()  - self._coursework_wev.due_date
        # I anticipated the delivery date of a delta, here I must ... put it back
        days_late = (dates_delta - gd.SUBMISSION_DELTA).days
        
        if days_late < 0: 
            days_late = 0

        return days_late


    @property
    def assigned_grade(self):
        return self._assigned_grade
    @assigned_grade.setter
    def assigned_grade(self, value):
        self._assigned_grade = value


    @property
    def should_evaluate(self):
        """ == must be given a grade, even if not submitted"""
        if self.assigned_grade is not None:
            return False  # already graded
        if self._coursework_wev.has_expired:
            return True
        return False

    @property
    def should_correct(self):
        """ has been handed in, must be examined bz teacher, and grader"""
        if not self.should_evaluate:
            return False  # redundant with upper level, for safety
        if not self.is_turned_in:
            return False # nothing to examine, will get automatic grade for missed hand-in
        if self.assigned_grade is not None:
            return False  # already graded
        return True


    @property
    def assignment_submission(self):
        return self._assignment_submission
    @assignment_submission.setter
    def assignment_submission(self, value):
        self._assignment_submission = value

    @property
    def submission_student(self):
        if self._student is None:
            self._student = gv.students_database.stud_by_id(self.user_id)
        return self._student

    @submission_student.setter
    def submission_student(self, value):
        self._student = value

    @property
    def student_email(self):
        if self.student is None:
            return "sudentIsNone@dummy.none.com" 
        return self.student.email


    def check_attach_naming(self, penalty_points_first = 5, penalty_points_next = 2):
        
        found_errors = False; penalty_points = 0; messages_all_l = []        
        if self.has_attachments:
            for attachment in self.attachments_l:
                ok, msgs_l = gc_u.check_attachment_filename(attachment)
                if not ok:
                    found_errors = True
                    penalty_points = penalty_points_first if penalty_points == 0 else (penalty_points+penalty_points_next)
                    messages_all_l += msgs_l

        return found_errors, penalty_points, messages_all_l


    def check(self):
        messages = []
        ret = True
        if self.first_turned_in is None and self.assigned_grade is not None:
            messages.append("not turned in but has grade")
            ret = False

        if not ret:
            log.error("status not ok")
        
        return ret, messages

    @property
    def attachments_l(self):
        return self._attachments_l

    @attachments_l.setter
    def attachments_l(self, value):
        self._attachments_l = value

    @property
    def has_attachments(self):
        return len(self._attachments_l) > 0


    def download_attachments(self, destination_dir = None, gdrive_service_initialized = None, 
        fail_if_existent = False, rm_rf_all = False):
 
        if self.attachments_l is None or len(self.attachments_l) <= 0:
            print('No attachments for <{}> for "{}"'.format(self.student_email, self.coursework_title))
            return False, None

        if destination_dir is not None:
            destination_dir = os.path.join(destination_dir, self.student_email.split("@")[0])
        else:
            dir = self._coursework_wev.dow
            destination_dir = os.path.join(self.download_in, destination_dir, self.student_email.split("@")[0])

        lu_g.create_dir(destination_dir, fail_if_existent = False, rm_rf_all = False)
        downloaded = False
        for attachment in self.attachments_l:
            if  not gd.DRIVE_FILE_KEY in attachment.keys():
                log.error("not found "+gd.DRIVE_FILE_KEY+" in attachment, ignoring")
                return False
            att = sat.SubmissionAttachment_wev(attachment)
            print(att.dump_short())
            log.debug(attachment[gd.DRIVE_FILE_KEY])
            gdrlu.download_file_submission_entry(attachment, dest_dir = destination_dir, gdrive_service_initialized = gdrive_service_initialized, 
            remove_if_present = False)
            downloaded = True
        
        return downloaded, destination_dir


    def download_in(self, mother_dir, gdrive_service_initialized, start_explorer = False):
        
        if len(self.attachments_l) <= 0:
            log.info("nothing to download for: {}".format(self.student_email.split("@")[0]))
            return False
        
        full_dir_path = os.path.join(mother_dir, self.student_email.split("@")[0])
        lu_g.create_dir(full_dir_path, fail_if_existent=False, rm_rf_all= False)

        if self.download_attachments(full_dir_path, gdrive_service_initialized):
            if start_explorer:
                lu_g.open_file_explorer(full_dir_path)


    def examine_submission(self):
        """ IDEE BUTTATE LI """
        comments_list = [] # commenti su violazione regole naming, ritardo consegna Etc
        vote_adjustment = 0 # decrease because of violation of naming rules, delayed submission Etc.

        return comments_list, vote_adjustment


    def publish_comments(self, comments_l):
        """ created to publish comments generated automatically """
        log.warning("publish_comments() not yet implemented, comments would be:\n"+str(comments_l))


    def write_grade(self, grade, grade_type = 0, gclassroom_service = None, gdrive_service = None):
        """
        grade_type: 0 draftGrade, 1 assignedGrade
         if grade < min grade it will not be written
        """
        if grade < gd.GRADE_MINIMUM or grade > gd.GRADE_MAXIMUM:
            log.warning("not writing grade outside range: {}".format(grade))
            return

        studentSubmission = {
            'assignedGrade': grade,
            'draftGrade'   : grade
        }

        # if not self.student_email in gd.TEST_USER_EMAILS:
        #     log.warning("Until fully tested not actually writing grade of {}".format(self.student_email))
        #     return

        try:
            if gclassroom_service is None:
                gclassroom_service = self._classroom_service
            ret = gclassroom_service.courses().courseWork().studentSubmissions().patch( 
                courseId     = self.course_id,
                courseWorkId = self.coursework_id, 
                id           = self.id, 
                updateMask='assignedGrade,draftGrade',
                body=studentSubmission).execute()
            # log.info(ret)
        except Exception as e:
            log.warning("writing grade refused (normal if coursework not created by API):\ncourse: {}\ncoursework: {}\nstudent: {}, normal for coursework created manually and not by the API"
            .format(self.course_title, self.coursework_title, self.student_email))
            log.debug(e)
            # https://stackoverflow.com/questions/69098186/how-to-fixed-project-permission-denied-problem-for-update-draft-grade-and-assign"+
            # DA url DI SOPRA: ... if the resource you are trying to modify has been created manually for instance, 
            # this means that it is not associated with any developer project, hence the error you are receiving. ...")


    def correction_banner(self, prompt_left = None, prompt_right = None):
       
        if prompt_left is None: prompt_left = ""; 
        if prompt_right is None: prompt_right = ""

        print("\n"+ gd.BANNER_LEV_3.format(prompt_left, " "+colored(self.student_email, 'green')+" ", prompt_right))
        print('"{}" - due: {} - submitted: {}'.format(self.coursework_title, self.due_date, 
            str(self.first_turned_in)[:16]))
        if self.days_late > 0: print(colored("### LATE, days: {}".format(self.days_late),"red"))
        print("previous grade: "+str(self.assigned_grade))


    def correct_submission(self, dir_cw_download, gdrive_service_initialized, start_explorer = True,
        message = None):

        self.correction_banner(prompt_left = message)

        ret, student_dir =  self.download_attachments(dir_cw_download, gdrive_service_initialized)
        if ret and start_explorer: lu_g.open_file_explorer(student_dir)

        comments_l, grade_djustment = self.examine_submission()
        content_grade = lu_i.get_int("insert the grade (solely based on content),"+
            " < {} not to grade, 0 to exit correction: ".format(gd.GRADE_MINIMUM))
        grade = content_grade - grade_djustment
        # comments planned but NOT yet AVAILABLE in the API, see classroom support and SO
        # comment = input("insert comment to the grade:\n")
        # merge automatic comments and comment and grade and grade_adjustment
        # self.publish_comments(comments_l)
        self.write_grade(grade) # if grade < min grade it will not be written

        return grade


    def dump_str(self, verbose = False):
        dump = "\nsubmission: of {}".format(self.student_email)
        dump += "\nfor c.work: "+self._coursework_wev.title
        if verbose:
            dump += "\nfor Course: "+self.course_title
        dump += "\ndue date:      "+str(self.due_date)
        if self.due_date > date.today():
            dump += "\nFUTURA"
        dump += "\ncreated:       "+str(self.creation_time)
        dump += "\n1st submitted: "+str(self.first_turned_in)
        dump += "\nlast subm:     "+str(self.last_turned_in)
        if self.first_turned_in != self.last_turned_in:
            after = self.last_turned_in - self.first_turned_in
            after_str = lu_g.time_delta_to_str(after)
            dump += "\nRISOTTOMESSA, da prima sottomissione a ultima: "+after_str
        dump += "\nassigned_grade: "+str(self.assigned_grade)

        return dump