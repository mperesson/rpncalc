from rpncalc.enums import bcolors


def colored(text, color):
    return '{}{}{}'.format(color, text, bcolors.ENDC)


def text(text):
    return colored(text, bcolors.OKBLUE)


def green_text(text):
    return colored(text, bcolors.OKGREEN)


def error_text(text):
    return colored(text, bcolors.FAIL)
