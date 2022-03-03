

class Student_wev:

    def __init__(self, student_initalized, service_initialized):
        self._student = student_initalized
        self._profile = self._student['profile']
        self.id = self._profile['id']
        self.email = self._profile['emailAddress']

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, value):
        self._email = value
