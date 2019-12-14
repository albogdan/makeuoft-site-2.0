import datetime

from wtforms.compat import string_types
from wtforms.validators import StopValidation
from flask_wtf.file import FileStorage


class DataRequiredIfOtherFieldEmpty:
    """
    Checks that a given field is "truthy" only if another field specified by
    `other_field` is not
    """

    field_flags = ("required",)

    def __init__(self, other_field, message=None):
        self.other_field = other_field
        self.message = message

    def __call__(self, form, field):
        other_field = getattr(form, self.other_field, None)
        if (
            not field.data
            or isinstance(field.data, string_types)
            and not field.data.strip()
        ):
            if (
                not other_field.data
                or isinstance(other_field.data, string_types)
                and not other_field.data.strip()
            ):
                if self.message is None:
                    message = field.gettext("This field is required.")
                else:
                    message = self.message

                field.errors[:] = []
                raise StopValidation(message)


class DataRequiredIfOtherFieldMatches:
    """
    Checks that a given field is "truthy" only if another field specified by
    `other_field` matches a certain value
    """

    field_flags = ("required",)

    def __init__(self, other_field, other_value, message=None):
        self.other_field = other_field
        self.other_value = other_value
        self.message = message

    def __call__(self, form, field):
        other_field = getattr(form, self.other_field, None)
        if other_field.data != self.other_value:
            return

        if (
            not field.data
            or isinstance(field.data, string_types)
            and not field.data.strip()
        ):
            if self.message is None:
                message = field.gettext("This field is required.")
            else:
                message = self.message

            field.errors[:] = []
            raise StopValidation(message)


class OldestAllowedDate:
    """
    Checks that a given date field is older than the specified date
    """

    def __init__(self, date, message=None):
        """
        :param date: (datetime.date) Minimum allowed date
        """
        self.date = date
        self.message = message

    def __call__(self, form, field):
        data = field.data
        message = self.message
        if message is None:
            message = field.gettext(
                "Date must be older than {}".format(self.date.strftime("%Y-%m-%d"))
            )
        if not data:
            raise StopValidation(message)

        if data > self.date:
            raise StopValidation(message)


class FileSize(object):
    """Validates that the uploaded file is within a minimum and maximum file size (set in bytes).
    :param min_size: minimum allowed file size (in bytes). Defaults to 0 bytes.
    :param max_size: maximum allowed file size (in bytes).
    :param message: error message
    You can also use the synonym ``file_size``.

    Taken from https://github.com/lepture/flask-wtf/pull/365
    """

    def __init__(self, max_size, min_size=0, message=None):
        self.min_size = min_size
        self.max_size = max_size
        self.message = message

    def __call__(self, form, field):
        if not (isinstance(field.data, FileStorage) and field.data):
            return

        file_size = len(field.data.read())
        field.data.seek(0)  # reset cursor position to beginning of file

        if (file_size < self.min_size) or (file_size > self.max_size):
            # the file is too small or too big => validation failure
            raise StopValidation(
                self.message
                or field.gettext(
                    "File must be between {min_size} and {max_size} bytes.".format(
                        min_size=self.min_size, max_size=self.max_size
                    )
                )
            )
