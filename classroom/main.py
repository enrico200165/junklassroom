# RULES AND PRINCIPLES
# Functions/methods return at least types fron the API, named without any suffix
# My wrapper classes use the suffix _wev (wrapper enrico viali)

# https://developers.google.com/classroom/reference/rest/v1/courses.courseWork

import os

from googleapiclient.errors import HttpError


from datetime import datetime, date, time

# --- my imports ---
import global_defs as gd
import config as cfg
import classroom_tools as gct
import course_wev as crs
import courses_db
import coursework_wev as crw
from submission_cl_wev import Submission_wev

import little_utils_generic as lu_g
import little_utils_gdrive as gdrv
import little_utils_interface as ilt

import gmail_tools as gmt

###########################################################################
#                   TODO
# 
# per un dato compito (filtro dei compiti da definire poi)
# check nomi correttezza files consegnati
# download files consegnati in una directory (non Gdrive) 
# <classe>\<compito>\<nome studente>
# apri explorer in tale directory
# se file py o cpp the IDE
# definisci filtro dei compiti


# little adjustents, maybe wrong/silly
courses_database = courses_db.Courses_db() 
log = gd.log


''' ############################### TODO #######################################
evita di scaricare courserwork già corretto
  submissionns già con voto (parametro opzionale, risottmissioni vanno valutate)
'''
courses_filter_ids = [
"3q - codoc. TLC&TPSIT - 2021/22"
, "2c -STA - 2021" 
# , "3q - TPSIT - 2021" 
# , "3q - Sis. Reti - 2021" 
# , "1L - Inform. - 2021" 
# , "1i - Tec. Inf.- 2021" 
#, "1c - Tec. Inf. - 2021" 
]


def init(cfg_file_path):
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    g_edu_config_mgr = cfg.GoogleEducationConfig(cfg_file_path)
    g_edu_config_mgr.get_config_from_file()
    ret = lu_g.create_dir(gd.COURSEWORK_LOC_DWLD_ROOT_DIR, fail_if_existent= False, rm_rf_all= True) 
    # glu.open_file_explorer(gd.COURSEWORK_LOC_DWLD_ROOT_DIR)
    # courses
    return g_edu_config_mgr


def check_attachments_names(courses_l):
    max_emails = 5
    if "y" == ilt.get_y_n("vuoi cambiare max emails mandate? (adesso {})".format(max_emails)):
        max_emails = ilt.get_int("max_emails da mandare: ")
    email_mandate = 0
    for course_triple in courses_l:
        if email_mandate >= max_emails: break
        course = course_triple.object_or_value
        for cw in course.course_works_l:
            if cw.due_days_ago is not None and cw.due_days_ago < -2:
                continue
            email_mandate = cw.check_submissions_attachments_naming(email_mandate, max_emails)
            print("ora le email mandate sono {} per '{}'".format(email_mandate, cw.title))
            if email_mandate >= max_emails: break

def main():

    cfg_mgr = init(gd.config_file_path)
    ENRICO_ID = cfg_mgr.ENRICO_USER_ID 
    # log.info("Enrico ID: "+ENRICO_ID)

    classroom_service = gct.session(gd.gclassroom_credentials_filepath, gd.ALL_SCOPES)
    gdrive_service = gdrv.create_gdrive_service(gd.ALL_SCOPES, gd.glcassroom_oauth_token_filepath, gd.gclassroom_credentials_filepath)
    gmail_service = gmt.get_gmail_service()

    courses_l = courses_database.get_courses(classroom_service, gdrive_service, ENRICO_ID)    
    
    if "y" == ilt.get_y_n("Controllo i nomi degli attachments?"):
        check_attachments_names(courses_l)

    choice_course_descr = ilt.menu_1_choice_autokey(courses_l, start_prompt = "Choose course (return key not needed)")
    course = choice_course_descr.object_or_value
    if course is None:
        log.warning("No course found")
        return
    course.correct_courseworks(days_back = 14, max_nr_to_correct = 5)


if __name__ == '__main__':
    main()
