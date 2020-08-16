import os


def sanitize_input_variable(var):
    var = os.path.expanduser(var)
    var = os.path.expandvars(var)
    return var
