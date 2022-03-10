import logging
from  logging import handlers
from datetime import datetime, timedelta
import os
from os.path import join

from datetime import datetime

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s %(filename)s %(lineno)s %(levelname)-8s \n%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

frmter = logging.Formatter('{lineno}**{message}** at{asctime}|{name}',style='{')
logfh = handlers.RotatingFileHandler("logging.log", mode='a', maxBytes=1024*4, backupCount=0, 
    encoding=None, delay=False, errors=None)
logfh.setFormatter(frmter)

log = logging.getLogger(__name__)
log.addHandler(logfh)


#####################################################################
#                           DIRECTORIES
#####################################################################
# --- root directories ----
GDRIVE_ROOT = os.environ['GDRIVE_HOME']
if not os.path.isdir(GDRIVE_ROOT):
    log.error("Not found GDrive home directory: {}". format(GDRIVE_ROOT))
    exit(1)

USERPROFILE_DIR = os.environ['USERPROFILE']
# DIR_DOWNLOADS = os.environ['TEMP']
DIR_DOWNLOADS = join(USERPROFILE_DIR, "gclass_loc_download")
COURSEWORK_LOC_DWLD_ROOT_DIR = join(DIR_DOWNLOADS, "delete")



# --- credentials and token paths ---
config_file_path = join(GDRIVE_ROOT, "08_dev_gdrive", "configs", "google_classroom","education.ini")
if not os.path.isfile(config_file_path):
    log.error("Not found config file path: {}". format(config_file_path))
    exit(1)

oauth_token_filedir = join(GDRIVE_ROOT, "08_dev_gdrive", "configs", "google_classroom")
if not os.path.isdir(oauth_token_filedir):
    log.error("Not found tokens directory: {}". format(oauth_token_filedir))
    exit(1)
glcassroom_oauth_token_filepath = join(oauth_token_filedir, "token_gclassroom.json")
gdrive_oauth_token_filepath     = join(oauth_token_filedir, "token_gdrive.json")
gmail_oauth_token_filepath      = join(oauth_token_filedir, "token_gmail.json")
gcalendar_oauth_token_filepath  = join(oauth_token_filedir, "token_gcalendar.json")


credentials_file_dir = oauth_token_filedir
if not os.path.isdir(credentials_file_dir):
    log.error("Not found credentials directory: {}". format(credentials_file_dir))
    exit(1)

enrico200165_credentials   = "client_secret_235502692513-dcc97c4geg6kea8umr8au52eqlqgn6cu.apps.googleusercontent.com.json"

# https://console.developers.google.com/apis/credentials?hl=it&orgonly=true&project=classroom-00&supportedpurview=organizationId
enrico_galilei_credentials = "client_secret_762622398402-3je8ufvkg8hcruniearrnp14nffbk2fm.apps.googleusercontent.com.json"

prj_classroom_00_credentials = enrico_galilei_credentials
# prj_classroom_00_credentials = enrico200165_credentials
gclassroom_credentials_filepath = join(credentials_file_dir, prj_classroom_00_credentials)
if not os.path.isfile(gclassroom_credentials_filepath):
    log.warn("not found {}".format(gclassroom_credentials_filepath))

gdrive_credentials_filepath = join(credentials_file_dir, prj_classroom_00_credentials)
if not os.path.isfile(gdrive_credentials_filepath):
    log.warn("not found {}".format(gdrive_credentials_filepath))

gmail_credentials_filepath = join(credentials_file_dir, prj_classroom_00_credentials)
if not os.path.isfile(gmail_credentials_filepath):
    log.warn("not found {}".format(gmail_credentials_filepath))

gcalendar_credentials_filepath = join(credentials_file_dir, prj_classroom_00_credentials)
if not os.path.isfile(gcalendar_credentials_filepath):
    log.warn("not found {}".format(gcalendar_credentials_filepath))



# If modifying these scopes, delete the file token.json.
CLASSROOM_SCOPES = [
    #'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.courses',

    #'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.rosters',

    #'https://www.googleapis.com/auth/classroom.coursework.students.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.students',

    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/classroom.profile.emails']

GDRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive',
    #'https://www.googleapis.com/auth/drive.metadata',
    ]

GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'
    ,"https://www.googleapis.com/auth/gmail.send" # Send messages only. No read or modify privileges on mailbox.
    ]

ALL_SCOPES = CLASSROOM_SCOPES+GDRIVE_SCOPES+GMAIL_SCOPES



# --------- KEYS ----------
# classi
CL1C_K = "1c"
CL1I_K = "1i"
CL1L_K = "1l"
CL2C_K = "2c"
CL3Q_K = "2c"

GIT_INDIV_ROOT_DIR_K = "git_indiv_root_dir"

DRIVE_FILE_KEY = 'driveFile'

ENRICO_ID = None # should be in a configuration file

EMAIL_VIALI_GALILEI = "viali.enrico@itisgalileiroma.it"
EMAIL_ENRICO200165 = "enrico200165@gmail.com"

DATE_STR_FORMAT_00 = "%Y-%m-%d"
# DATE_NO_DUE_DATE_STR = "2999-12-31"
# DATE_NO_DUE_DATE = datetime.strptime(DATE_NO_DUE_DATE_STR, DATE_STR_FORMAT_00)



def dump_class_obj_str(obj):
    """ to dump with the same format"""
    ret = "<{}>".format(type(obj))
    return ret 

def dump_member_str(field_name, val, newLine = False, first = False):
    """ to dump with the same format"""
    ret = "\n" if newLine else ""
    ret += " .{}='{}'".format(field_name, val)
    if not first and not newLine:
        ret = " "+ret
    return ret


# ------------------ KEYS ------------------
# coursework
CW_STATE_PUBLISHED = 'PUBLISHED'
CW_WORK_TYPE_ASSIGNMENT ='ASSIGNMENT'


# ------------------ Values ----------------

GRADE_NON_DELIVERED = 30
GRADE_NON_FOR_TEST  = 29


TEST_COURSE_ID = '459768814779'

TEACHER_EMAILS = ["enrico200165@gmail.com", "enrico.viali@gmail.com", "armandoitaly1990@gmail.com"]
TEST_USER_EMAILS = TEACHER_EMAILS


# ------------- courses dict ----------------


courses = {
# key: (id, days)
    "3qs": "465615229542",
    "3qt": "465615229420",
    "2c":  "465615229312",
    "1l":  "465610906107",
    "1i":  "458988856391",
    "ic":  "458986835499",
}


# ------------------------ BANNERS ---------------------
BANNER_LEV_1 = "{}######################{}######################{}"
BANNER_LEV_2 = "{}================={}================={}"
BANNER_LEV_3 = "{}---------------{}---------------{}"

GRADE_MINIMUM = 30
GRADE_MAXIMUM = 100

SUBMISSION_DELTA = timedelta(days = 1, hours = 12, minutes = 0)