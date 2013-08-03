def command(function):
    function.is_command = True
    return function

def is_command(function):
    return getattr(function, 'is_command', False)
