

from datetime import datetime, timedelta, date
import subprocess
import os
from pathlib import Path
from shutil import rmtree

import global_defs as gd

log = gd.log



######################## OS FILES ########################

def adjust_4_dir_name(name):
    name = name.replace('"',"")

    name = name.replace('{',"")
    name = name.replace('}',"")

    name = name.replace('[',"")
    name = name.replace(']',"")

    name = name.replace('(',"")
    name = name.replace(')',"")

    name = name.replace(':',"")
    name = name.replace(';',"")

    name = name.replace('+',"")
    name = name.replace('*',"")

    return name

def adjust_4_file_name(name):

    name = adjust_4_dir_name(name)
    name = name.replace("/","-")
    name = name.replace("\\","-")

    return name


    return dir_name

def create_dir(full_path, fail_if_existent = False, rm_rf_all = False):
    if not os.path.isdir(full_path):
        if os.path.isfile(full_path):
            log.error("Exists file with same name, creation of the directory %s failed" % full_path)
            return False
        try:
            cleaned_dir = adjust_4_dir_name(full_path)
            normalized_path = os.path.normpath(cleaned_dir)
            path_components = normalized_path.split(os.sep)
            
            drive = path_components.pop(0)+":\\" # acrobacies because it does not work without this trick
            path = path_components.pop(0)
            while len(path_components) > 0:
                path = os.path.join(path, path_components.pop(0)) 
                trick_path = drive+path
                if not os.path.isdir(trick_path):
                    log.debug("mkdir {}".format(trick_path))
                    os.mkdir(trick_path)
            log.debug("Successfully created the directory %s " % full_path)
            return trick_path # caller must know the evenutally modified path
        except OSError as e:
            log.error(e)
            log.error("Creation of the directory %s failed" % full_path)
            exit(1)
            return False
    else: 
        if fail_if_existent:
            log.error("Directory %s already exists" % full_path)
            return False
    # here directory one way or another  exists
    if rm_rf_all:
        for path in Path(full_path).glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                rmtree(path)


def open_file_explorer(path):

    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])
    else:
        log.warning("non existing dir {} to start explorer".format(path))



######################## DATES ########################

DAY_OF_WEEK = {
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
    "SUNDAY": 0
}
DAY_OF_NUMBER = {}
for k,v in DAY_OF_WEEK.items(): DAY_OF_NUMBER[v] = k


def weekday_sunday0(day_num):
    if day_num == 6:
        return 0
    return day_num+1


def second_in_day(datetime_par = datetime.now()):
    """ which second, among the 24*3600 it is
    created for identifying series of resources created in a single call/session that should
    all be deleted/modified together (ex. coursework)
    """
    # https://stackoverflow.com/questions/15971308/get-seconds-since-midnight-in-python
    since_midnight = datetime_par.hour* 3600 + datetime_par.minute * 60 + datetime_par.second
    return since_midnight


def to_datetime(date_or_string):
    """expects format yyyy-mm-dd"""
    ret_date = date_or_string
    if isinstance(date_or_string, str):
        ret_date = datetime.strptime(date_or_string, '%Y-%m-%d')
    return ret_date


def string2datetime(s):
    # https://stackoverflow.com/questions/27840670/what-is-the-z-ending-on-date-strings-like-2014-01-01t000000-588z
    if s is None: 
        return None
    ret = None
    formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S']
    for i, f in enumerate(formats):
        try:
            if i >= 2:
                log.debug("breakpoint")
            cr_time = datetime.strptime(s, f)
            ret = cr_time
            return ret
        except:
            # rare but possible
            log.debug("{} format  does not parse time string \n{}".format(f, s))
    log.error("unable to manage format of string {}".format(s))
    return ret

def string2date(s):
    dt =  string2datetime(s)
    if dt is not None:
        d = dt.date()
    return dt


def time_delta_to_str(time_delta):
    days = time_delta.days
    hours = time_delta.seconds//3600
    minutes = (time_delta.seconds - hours*3600)//60
    seconds = time_delta.seconds - hours*3600 - minutes*60
    ret = "{} days - {} hours  - {} mins  - {} secs".format(days, hours, minutes, seconds)
    return ret


def datetimestamp(dt = datetime.now()):
    ret =  datetime.strftime(dt, '%Y-%m-%d %H:%M:%S')
    return ret

def datestamp(dt = datetime.now()):
    ret =  datetime.strftime(dt, '%Y-%m-%d')
    return ret

def timestamp(dt = datetime.now()):
    ret =  datetime.strftime(dt, '%H:%M:%S')
    return ret


def weekly_appointments(start_date, week_day_number_l, end_date):
    """generate list of dates for a list of weekly day numbers, 
    where monday = 1, this is different from native numbering 
    where monday = 0
    Keyword arguments:
    start_date -- inclusive, dates generate from that date on
    week_day_number_l -- 1 for monday. [1, 4] = monday, thursday. monday has weekday 0
    """
    dates = []
    start_date = to_datetime(start_date)
    last_date = to_datetime(end_date)
    cur_date = start_date
    while cur_date <= last_date:
        for day_num in week_day_number_l:
            if weekday_sunday0(cur_date.weekday()) == day_num:
                dates.append(cur_date)
        cur_date += timedelta(days=1)
    
    return dates

def dict_get(dict, key, should_be_there = False):
    """ return None of key not present
    """
    if should_be_there and key not in dict.keys():
        log.error("for breakpoint, key not found:", key)
    return None if key not in dict.keys() else dict[key]



if __name__ == '__main__':

    def test_create_dir():

        d =  r"C:\Users\enrico\gclass_loc_download\delete\1L-2021-q2_Inform\2022-02-15 - Compiti\bersabal.anthonythomas.stud"
        create_dir(d)
    
    test_create_dir()
    exit(0)

    def main():

        create_dir('C:\\Users\\enrico\\gclass_loc_download\\delete\\3q-2021-q2_Sis-Reti\\2022-02-17 - Laboratorio SR')

        print(datetimestamp())
        print(datestamp(date.today()))
        print(timestamp(date.today()))

        print(second_in_day())

        dates = weekly_appointments("2022-02-13", [0,2,4,5,6], "2022-06-01")
        # [ log.info(d, glu.weekday_sunday0(d.weekday()), glu.DAY_OF_NUMBER[glu.weekday_sunday0(d.weekday())]) for d in dates]

        # for d in dates: print(d, weekday_sunday0(d.weekday()), DAY_OF_NUMBER[weekday_sunday0(d.weekday())]) 

        log.info(to_datetime("2022-01-31"))

    main()
