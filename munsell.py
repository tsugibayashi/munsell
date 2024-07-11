#!/usr/bin/python3
# -*- coding: utf8 -*-
import sys
import os
import configparser
import subprocess
from decimal import Decimal, getcontext, InvalidOperation

### functions
# def get_rcfile(method :str) -> str: {{{
def get_rcfile(method :str) -> str:
    if method == 'xbacklight':
        rcfile = os.path.expanduser('~') + '/.xbacklightrc'
    elif method == 'light':
        rcfile = os.path.expanduser('~') + '/.lightrc'
    else:
        print('[Error] unknown method:', method)
        print('        Input xbacklight or light')
        quit()

    return rcfile
# }}}
# def read_brightness_from_rcfile(filename :str) -> Decimal: {{{
def read_brightness_from_rcfile(filename :str) -> Decimal:
    config = configparser.ConfigParser()
    config.read(filename)

    brightness = config["DEFAULT"]["brightness"]

    return Decimal(brightness)
# }}}
# def write_brightness_to_rcfile(filename :str, brightness :Decimal) -> None: {{{
def write_brightness_to_rcfile(filename :str, brightness :Decimal) -> None:
    config = configparser.ConfigParser()

    #config.add_section('DEFAULT')
    config["DEFAULT"]["brightness"] = str(brightness)

    with open(filename, 'w') as file:
        config.write(file)

    return None
# }}}
# def adjust_brightness -> Decimal {{{
def adjust_brightness(brightness :Decimal,
                      min_brightness :Decimal,
                      max_brightness :Decimal) -> Decimal:
    if brightness < min_brightness:
        new_brightness = min_brightness
    elif brightness > max_brightness:
        new_brightness = max_brightness
    else:
        new_brightness = brightness

    return new_brightness
# }}}
# def munsell(value :Decimal) -> str: {{{
def munsell(value :Decimal) -> str:
    # value is the Munsell value, between 0.0 and 10.0

    # https://www.munsellcolourscienceforpainters.com/ColourSciencePapers/OpenSourceInverseRenotationArticle.pdf
    percentage = Decimal("1.1914") * value \
                 - Decimal("0.22533") * value ** 2 \
                 + Decimal("0.23352") * value ** 3 \
                 - Decimal("0.020484") * value ** 4 \
                 + Decimal("0.00081939") * value ** 5

    # https://en.wikipedia.org/wiki/Lightness
    #percentage = Decimal("1.2219") * value \
    #             - Decimal("0.23111") * value ** 2 \
    #             + Decimal("0.23951") * value ** 3 \
    #             - Decimal("0.021009") * value ** 4 \
    #             + Decimal("0.0008404") * value ** 5

    # percentage = 0.0 to 100.00000000000004
    return str(percentage)
# }}}

### variables
getcontext().prec  = 6                 # precision for Decimal()
default_brightness = Decimal("3.0")
step_brightness    = Decimal("1.0")
min_brightness     = Decimal("0.3")
max_brightness     = Decimal("10.0")   # DON'T CHANGE THIS VALUE

if len(sys.argv) < 2:
    print('[Error] input $1, method to use')
    print('        ex. xbacklight or light')
    quit()
elif len(sys.argv) < 3:
    print('[Error] input $2, action')
    print('s : Sets brightness')
    print('p : Increases brightness')
    print('m : Decreases brightness')
    quit()

method = sys.argv[1]
action = sys.argv[2]

# configuration filename
# xbacklight : ~/.xbacklightrc
# light      : ~/.lightrc
rcfile = get_rcfile(method)

if action == 's':
    if len(sys.argv) < 4:
        print('[Error] input $3, brightness (0.0 to 10.0)')
        quit()

    try:
        brightness = Decimal(sys.argv[3])
    except InvalidOperation:
        print('[Error]', sys.argv[3], 'is not decimal number.')
        quit()
else:
    # action == "p" or action == "m"
    # Reads brightness from rcfile
    if not os.path.isfile(rcfile):
        brightness = default_brightness
    else:
        brightness = read_brightness_from_rcfile(rcfile)

### main routine
if action == 'p':
    inc_brightness = brightness + step_brightness
    brightness = inc_brightness // step_brightness * step_brightness
elif action == 'm':
    dec_brightness = brightness - step_brightness
    brightness = dec_brightness // step_brightness * step_brightness

# If brightness < min_brightness, brightness is changed to min_brightness.
# If brightness > max_brightness, brightness is changed to max_brightness.
brightness = adjust_brightness(brightness, min_brightness, max_brightness)
#print('brightness', brightness)

# Calculates percentage of the Munsell from brightness
percentage = munsell(brightness)
#print('percentage', percentage)

# Executes the method
if method == 'xbacklight':
    # xbacklight
    subprocess.run([method, "-set", percentage])
else:
    # light
    subprocess.run([method, "-S", percentage])

# Updates the rcfile
write_brightness_to_rcfile(rcfile, brightness)

