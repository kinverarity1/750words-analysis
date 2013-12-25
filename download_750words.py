#!/usr/bin/env python

import argparse
import os
import sys

import m750

def main():
    parser = get_cmdline_parser()
    args = parser.parse_args(sys.argv[1:])
    text, entries = m750.download_750words(current=~args.all, download=args.path)
    
    
def get_cmdline_parser():
    home = os.path.expanduser('~')
    parser = argparse.ArgumentParser('download 750words writing')
    parser.add_argument('-p', '--path', default=os.path.join(home, 'Downloads'),
                        help='where to download to')
    parser.add_argument('-a', '--all', action='store_true',
                        help='download all months (default is only the current month)')
    return parser    
    
    
if __name__ == '__main__':
    main()