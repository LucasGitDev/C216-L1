class StudentError(Exception):
    pass


class InvalidCourseError(StudentError):
    pass


class InvalidEmailError(StudentError):
    pass


class StudentNotFoundError(StudentError):
    pass
