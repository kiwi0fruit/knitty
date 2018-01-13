"""
CLI wrapper for stitch_preprosess function:
(source: str, lang: str=None) -> str
First argument is optional file extension.
"""
import sys
import os
from .preprocess_filter import knitty_preprosess


def main():
    ext = (os.path.splitext(os.path.basename(sys.argv[1]))[1].lstrip('.')
           if len(sys.argv) > 1
           else None)
    sys.stdout.write(knitty_preprosess(sys.stdin.read(), ext))


if __name__ == '__main__':
    main()
