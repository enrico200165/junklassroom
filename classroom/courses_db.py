import logging as log

import global_defs as gd
import course_wev as crs
import little_utils_interface as ilt


class Courses_db:
    def __init__(self):
        self._map_id = {}
        pass

    def add_by_id(self, id, course):
        if type(course) != crs.GCourse_wev:
            log.error("type error")
            exit(1)
        else:
            self._map_id[id] = course

    def get_courses(self, classroom_service, gdrive_service, teacher_id):

        courses = classroom_service.courses().list(pageSize=100).execute().get('courses', [])

        courses_list = []

        if teacher_id is None or len(teacher_id) <= 10:
            log.error("teacher ID to filter courses None or no valid, will select all courses")
            log.error("Currentòy, under developmen will select none")
            return courses_list

        for i, c in enumerate(courses):
            course = crs.GCourse_wev(c, classroom_service, gdrive_service, gd.ENRICO_ID, gd.COURSEWORK_LOC_DWLD_ROOT_DIR)
            if not course.is_active:
                # log.info("id: {} ignoring corse not active: {}".format(course.course_id, course.course_state))
                continue
            if not course.is_owner(teacher_id):
                # log.info("id: {} ignoring corse not owned: {}".format(course.course_id, course.name))
                continue
            # if not "test" in course.name:
            #     log.info("id: {} ignoring real course, testing: {}".format(course.course_id, course.name))
            #     continue
            courses_list.append(ilt.ChoiceDescriptor(course.name, course.course_id, course))
        
        return courses_list


    def dump_to_console(self):
        for k in self._map_id.keys():
            course = self._map_id[k]
            log.info("course, id: {}, title: {} ".format(course.id, course.title))
        
