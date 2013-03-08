#-*- coding: utf-8 -*-

#from babel import Locale

#from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

from django.utils import translation
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget

from phonenumber_field.phonenumber import to_python, PhoneNumber

from brilliant.utils import COUNTRIES_WITH_COUNTRY_CODE, COUNTRY_BY_COUNTRY_CODE, COUNTRY_CODE_BY_COUNTRY


class PhonePrefixSelect(Select):

    initial = None

    def __init__(self, initial=None):
        choices = [('', '---------')]
        for db_name, country, prefix in COUNTRIES_WITH_COUNTRY_CODE:
            if initial and initial == db_name:
                self.initial = initial
            choices.append((db_name, u'%s %s' % (country, prefix)))

#        locale = Locale(translation.get_language())
#        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
#            prefix = '+%d' % prefix
#            if initial and initial in values:
#                self.initial = prefix
#            for country_code in values:
#                print prefix, country_code
#                country_name = locale.territories.get(country_code)
#                if country_name:
#                    choices.append((prefix, u'%s %s' % (country_name, prefix)))
        return super(PhonePrefixSelect, self).__init__(choices=sorted(choices, key=lambda item: item[1]))

    def render(self, name, value, *args, **kwargs):
        if value and (not self.initial or COUNTRY_CODE_BY_COUNTRY[self.initial] != value) and value in COUNTRY_BY_COUNTRY_CODE:
            self.initial = COUNTRY_BY_COUNTRY_CODE[value]
        return super(PhonePrefixSelect, self).render(name, self.initial or value, *args, **kwargs)

    def value_from_datadict(self, data, files, name):
        value = super(PhonePrefixSelect, self).value_from_datadict(data, files, name)
        if not value: return ''
        return COUNTRY_CODE_BY_COUNTRY[value]

class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - a country select box for phone prefix
    - an input for local phone number
    """
    def __init__(self, attrs=None, initial=None):
        widgets = (PhonePrefixSelect(initial),TextInput(),)
        if not attrs:
            attrs = {}
        attrs['class'] = 'phone_number_multi_widget'
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if value.__class__ is PhoneNumber:
                return (u"+%s" % value.country_code, value.national_number)
            return value.split('.')
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super(PhoneNumberPrefixWidget, self).value_from_datadict(data, files, name)
        if not values[1]:
            return ''
        return '%s.%s' % tuple(values)
