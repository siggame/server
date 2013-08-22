import re

def command(function):
    function.is_command = True
    return function

def is_command(function):
    return getattr(function, 'is_command', False)

#Copied from http://stackoverflow.com/a/1176023/1430838
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def uncamel(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()
