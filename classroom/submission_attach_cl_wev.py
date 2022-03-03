# https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions
#
from datetime import datetime, date
import logging

import global_defs as gd
import global_vars as gv


import little_utils_gdrive as gdrlu
import little_utils_generic as lu_g

log = gd.log


class SubmissionAttachment_wev:

    def __init__(self, api_subm_attach_obj):

        obj = api_subm_attach_obj['driveFile']
        self.id = obj['id']
        self.title = obj['title']
        self.alternate_link  = obj['alternateLink']
        self.thumbnail_url  = obj['thumbnailUrl']

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        self._title = value

    @property
    def alternate_link(self):
        return self._alternate_link
    @alternate_link.setter
    def alternate_link(self, value):
        self._alternate_link = value

    @property
    def thumbnail_url(self):
        return self._thumbnail_url
    @thumbnail_url.setter
    def thumbnail_url(self, value):
        self._thumbnail_url = value


# {'driveFile': 
# {'id': '1crtillqMhb8HA5D2v1oOfSHCRDCplg1t', 'title': '1punto.txt', 
# 'alternateLink': 'https://drive.google.com/file/d/1crtillqMhb8HA5D2v1oOfSHCRDCplg1t/view?usp=drive_web', 
# 'thumbnailUrl': 'https://lh3.googleusercontent.com/QjOzHLsVDkOPJ7YGPw8obwmUit_aC84jWHy-I9ZxQO5kWtXaRWdIRwM9zNpSSOOvrIPZeCMgghQsI_I=s200'}}


    def dump_str(self, verbose = False):
        dump =  "\nid:       {}".format(self.id)
        dump += "\ntitle:    {}".format(self.title)
        dump += "\nlink:     {}".format(str(self.alternate_link))
        dump += "\nthumbnail:{}".format(str(self.thumbnail_url))
        return dump

    def dump_short(self, verbose = False):
        dump = "file: {}".format(self.title)
        dump += " -> {}".format(str(self.alternate_link))
        return dump