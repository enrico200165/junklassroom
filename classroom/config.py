#!/usr/bin/env python

import logging as log

import os
import configparser

import global_defs as gd


class GoogleEducationConfig(object):


    classes_info = {
        gd.CL1C_K : { gd.GIT_INDIV_ROOT_DIR_K: None },
        gd.CL1I_K : { gd.GIT_INDIV_ROOT_DIR_K: None },
        gd.CL1L_K : { gd.GIT_INDIV_ROOT_DIR_K: None },
        gd.CL2C_K : { gd.GIT_INDIV_ROOT_DIR_K: None },
        gd.CL3Q_K : { gd.GIT_INDIV_ROOT_DIR_K: None },
   }

    def __init__(self, cfg_file_path):
        if not os.path.isfile(cfg_file_path):
            log.error(cfg_file_path, "not found")
            exit(1)
        self._cfg_file_path = cfg_file_path

    def read_config_file(self, pathname):
        '''' just read (and parse file) '''
        config = configparser.ConfigParser()
        config.read(self._cfg_file_path)
        return config

    def get_config_from_file(self, pathname=None):
        ''' extract values from parsed config'''

        pathname = self._cfg_file_path if pathname is None else pathname
        log.debug("reading config file: " + pathname)
        self._config = self.read_config_file(pathname)
        # old debug: for section in config: print(section)

        self.ENRICO_USER_ID = self._config['galilei']['ENRICO_CLASSROOM_USER_ID']

        return self._config

    @property
    def ENRICO_USER_ID(self):
        return self._ENRICO_USER_ID

    @ENRICO_USER_ID.setter
    def ENRICO_USER_ID(self, value):
        self._ENRICO_USER_ID = value



def printHelpCmdParams():
    ''' if present should override file '''
    s = ""
    s += "--url <interact API URL>"
    s += " --channel <interact channel>"
    s += " --aud_lev <audience level>"
    s += " --aud_fname <name of field containing audience ID>"
    s += " --sess_id <session ID> used for testing, may be overridden, see code"
    s += " --aud_id <audicence ID value> used for testing, may be overridden, see code"
    print(s)


if __name__ == '__main__':
    pass
