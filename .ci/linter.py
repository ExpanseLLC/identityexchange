#!/usr/bin/env python3

import subprocess
import sys


def main():
    cmd = ["pycodestyle", "."]
    return subprocess.call(cmd)


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
