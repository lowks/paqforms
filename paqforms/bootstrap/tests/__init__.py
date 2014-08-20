import re


def clean(string):
    return re.subn(r'\s+', '', string)[0].strip()