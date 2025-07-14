#!/usr/bin/python3
# -*- coding: utf8 -*-
import sys
import os
#import configparser
import tomllib
import subprocess
from decimal import Decimal, getcontext, InvalidOperation

### functions
# def write_brightness_to_file(filename :str, brightness :Decimal) -> None: {{{
def write_brightness_to_file(filename :str, brightness :Decimal) -> None:
    with open(filename, 'w') as file:
        file.write('brightness = ' + str(brightness) + '\n')

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
# def munsell(value :Decimal) -> Decimal: {{{
def munsell(value :Decimal) -> Decimal:
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
    #return str(percentage)
    return Decimal(percentage)
# }}}

def main():
    ### Variables
    getcontext().prec  = 6                 # precision for Decimal()
    default_brightness = Decimal("4.0")

    # Configuration filename
    dirname = os.path.expanduser('~/.config/munsell')
    rcfile  = dirname + '/config.toml'
    # The filename containing the current brightness value
    brightness_file = dirname + '/brightness.toml'

    # Create an initial configuration file
    os.makedirs(dirname, exist_ok=True)
    if not os.path.isfile(rcfile):
        with open(rcfile, "w") as f:
            f.write('method          = "brightnessctl" #xbacklight, light, or brightnessctl\n')
            f.write('step_brightness = 1.0\n')
            f.write('min_step_brightness = 1.0\n')
            f.write('max_step_brightness = 10.0    #DON\'T CHANGE THIS VALUE\n')
            f.write('min_brightness = 1.0\n')
            f.write('max_brightness = 100.0\n')
    if not os.path.isfile(brightness_file):
        with open(brightness_file, "w") as f:
            f.write('brightness = ' + str(default_brightness) + '\n')
        sys.exit(0)

    # Read rcfile and brightness_file
    with open(rcfile, "rb") as f:
        rc = tomllib.load(f)
    with open(brightness_file, "rb") as f:
        bri = tomllib.load(f)

    method              = rc["method"]
    step_brightness     = Decimal(rc["step_brightness"])
    min_step_brightness = Decimal(rc["min_step_brightness"])
    max_step_brightness = Decimal(rc["max_step_brightness"])
    min_brightness      = Decimal(rc["min_brightness"])
    max_brightness      = Decimal(rc["max_brightness"])
    brightness          = Decimal(bri["brightness"])

    if len(sys.argv) < 2:
        print('[Error] input $1, action')
        print('s : Sets brightness')
        print('p : Increases brightness')
        print('m : Decreases brightness')
        #quit()
        sys.exit(1)
    action = sys.argv[1]

    if action == 's':
        if len(sys.argv) < 3:
            print('[Error] input $2, brightness step (0.0 to 10.0)')
            sys.exit(1)
        try:
            brightness = Decimal(sys.argv[2])
        except InvalidOperation:
            print('[Error]', sys.argv[2], 'is not decimal number.')
            sys.exit(1)
    elif action == 'p':
        inc_brightness = brightness + step_brightness
        brightness = inc_brightness // step_brightness * step_brightness
    elif action == 'm':
        dec_brightness = brightness - step_brightness
        brightness = dec_brightness // step_brightness * step_brightness
    else:
        print('[Error] unknown action:', action)
        sys.exit(1)

    # If brightness < min_step_brightness, brightness is changed to min_step_brightness.
    # If brightness > max_step_brightness, brightness is changed to max_step_brightness.
    brightness = adjust_brightness(brightness, min_step_brightness, max_step_brightness)
    print('brightness:', brightness)
    
    # Calculates percentage of the Munsell from brightness
    percentage = munsell(brightness)
    #print('percentage:', percentage)

    # If percentage < min_brightness, percentage is changed to min_brightness.
    # If percentage > max_brightness, percentage is changed to max_brightness.
    percentage = adjust_brightness(percentage, min_brightness, max_brightness)
    print('percentage:', percentage)

    # Executes the method
    if method == 'xbacklight':
        # xbacklight
        subprocess.run([method, "-set", str(percentage)])
    elif method == 'light':
        # light
        subprocess.run([method, "-S", str(percentage)])
    elif method == 'brightnessctl':
        # brightnessctl
        subprocess.run([method, "s", str(percentage) + '%'])
    else:
        print('[Error] unknown method:', method)
        sys.exit(1)
    
    # Updates the brightness_file
    write_brightness_to_file(brightness_file, brightness)

if __name__ == "__main__":
    main()

