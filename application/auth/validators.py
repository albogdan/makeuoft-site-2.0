import datetime

from wtforms.compat import string_types
from wtforms.validators import StopValidation


class DataRequiredIfOtherFieldEmpty:
    """
    Checks that a given field is "truthy" only if another field specified by
    `other_field` is not
    """
    field_flags = ('required', )

    def __init__(self, other_field, message=None):
        self.other_field = other_field
        self.message = message

    def __call__(self, form, field):
        other_field = getattr(form, self.other_field, None)
        if not field.data or isinstance(field.data, string_types) and not field.data.strip():
            if not other_field.data or isinstance(other_field.data, string_types) and not other_field.data.strip():
                if self.message is None:
                    message = field.gettext('This field is required.')
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
            message = field.gettext("Date must be older than {}".format(self.date.strftime("%Y-%m-%d")))
        if not data:
            raise StopValidation(message)

        if data > self.date:
            raise StopValidation(message)
