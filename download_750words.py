#!/usr/bin/env python

import argparse
import os
import sys

import m750

def main():
    parser = get_cmdline_parser()
    args = parser.parse_args(sys.argv[1:])
    if args.all:
        dl_current = False
    else:
        dl_current = True
    text, entries = m750.download_750words(email=args.username, password=args.password, current=dl_current, download=args.path)
    
    
def get_cmdline_parser():
    home = os.path.expanduser('~')
    parser = argparse.ArgumentParser('download 750words writing')
    parser.add_argument('-P', '--path', default=os.path.join(home, 'Downloads'),
                        help='where to download to')
    parser.add_argument('-a', '--all', action='store_true',
                        help='download all months (default is only the current month)')
    parser.add_argument("-u", "--username", default=None)
    parser.add_argument("-p", "--password", default=None)
    return parser    
    
    
if __name__ == '__main__':
    main()