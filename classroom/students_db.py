import logging as log
import global_defs as gd
import student_wev as stud

class Students_db:
    def __init__(self):
        self._map_id = {}
        pass

    def add_by_id(self, id, student):
        if type(student) != stud.Student_wev:
            gd.log.error("type error when inserting: found type {} instead of expected type".format(type(student)))
        self._map_id[id] = student

    def stud_by_id(self, id):
        try:
            student = self._map_id[id]
        except KeyError as e:
            gd.log.error("Not found student with id: {}".format(id))
            student = None
        finally:
            return student

    def dump_to_console(self):
        log.info(" --- Dump Students DB ---")
        for i, k in enumerate(self._map_id.keys()):
            student = self._map_id[k]
            log.info("{} studente, id: {}, email: {} ".format(i, student.id, student.email))
        


