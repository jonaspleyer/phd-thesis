#!/usr/bin/env python3
"""Filter output of pdflatex.

Usage: filter.py <latex engine> <options> <file>
"""

import os
import subprocess
import sys

import colorama
from colorama import Fore, Style

colorama.init()


def main(cmd):
    # Disable pdflatex line wrap (where possible)
    env = dict(os.environ, max_print_line="1000000000")

    # Run pdflatex and filter/colour output
    pdflatex = subprocess.Popen(
        cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in iter(pdflatex.stdout.readline, b""):
        try:
            line = line.decode("utf8").strip()
            if line.startswith("(/") or line.startswith("(./"):
                # Start loading file
                pass
            elif line.startswith(")"):
                # Finish loading file
                pass
            elif line.startswith("!"):
                # Error
                print(Fore.RED + line + Style.RESET_ALL)
            elif (
                line.startswith("Overfull")
                or line.startswith("Underfull")
                or "warning" in line.lower()
                or "missing" in line.lower()
                or "undefined" in line.lower()
            ):
                # Warning
                print(Fore.YELLOW + line + Style.RESET_ALL)
            else:
                print(line)
        except:
            print(line)


if __name__ == "__main__":
    assert len(sys.argv) > 1
    main(sys.argv[1:])
