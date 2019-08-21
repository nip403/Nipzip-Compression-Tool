#!/usr/bin/env python3

r"""
VERSION 3
======================================================================================

============\
-|-|-|-|-|-|-> "py /nipzip.py -h"
============/

Usage: nipzip.py [options]

Options:
  -h, --help            show this help message and exit
  -o, --override        Automatically overrides existing file if destination
                        file has content instead of prompting
  --source=SOURCE_FILE  Full path to source file (e.g. C:\Users\file.txt,
                        ..\tmp\binary.bin)
  --dest=DEST_FILE      Full path to destination file - if not provided, will
                        create a file with the same name as source file in the
                        same directory

  Debug Options:
    -v, --verbose       Verbose mode: display compressed and uncompressed data
    -d, --debug         Debug mode: display logging info

======================================================================================
"""

import huffman_engine as engine
from optparse import OptionParser, OptionGroup
import os.path
import sys

class BasicLogger:
    def __init__(self, debug=False, logs=[]):
        self.logs = logs
        self.debug = debug

        self.levels = {
            "fatal": True, # True = die
            "error": True,
            "warn": False,
            "info": False,
            "debug": False,
            "trace": False
        }

    def log(self, level, *content):
        if level.lower() not in self.levels:
            raise ValueError(f"Invalid logger level: '{level}'")

        self.logs.append((level, *content))

        if self.levels[level.lower()]:
            print("LOGGER."+level.upper()+":", *content)
            sys.exit()

        elif self.debug:
            print("LOGGER."+level.upper()+":", *content)

    def forcelog(self, *args):
        self.tmp_debug = self.debug
        self.debug = True
        self.log(*args)
        self.debug = self.tmp_debug

    def silentlog(self, level, *args): # doesn't raise error
        self.logs.append((level, *args))
        
def init_parser():
    parser = OptionParser("""py nipzip.py [options]

    Notes:
        - Can only use one option at a time.""")

    fileopts = OptionGroup(parser, "File Options")
    stringopts = OptionGroup(parser, "String Options")
    debugopts = OptionGroup(parser, "Debug Options")

    ####
    stringopts.add_option(
        "--compress",
        dest="text",
        default=False,
        help="Encodes a string and outputs binary string"
    )
    stringopts.add_option(
        "--decompress",
        dest="bin",
        default=False,
        help="Decodes a string and outputs decompressed string"
    )
    ####
    debugopts.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Verbose mode: display compressed and uncompressed data"
    )
    debugopts.add_option(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="Debug mode: display logging info"
    )
    ####
    fileopts.add_option(
        "-o",
        "--override",
        action="store_true",
        dest="override",
        default=False,
        help="Automatically overrides existing file if destination file has content instead of prompting"
    )
    fileopts.add_option(
        "--source",
        dest="source",
        help="Full path to source file (e.g. C:\\Users\\file.txt, ..\\tmp\\binary.bin)"
    )
    fileopts.add_option(
        "--dest",
        dest="dest",
        help="Full path to destination file - if not provided, will create a file with the same name as source file in the same directory"
    )
    ####
    parser.add_option_group(fileopts)
    parser.add_option_group(stringopts)
    parser.add_option_group(debugopts)

    return parser

def parse_cmd(argv):
    parser = init_parser()
    opts,args = parser.parse_args()

    verbose = opts.verbose
    debug = opts.debug
    override = opts.override

    source = opts.source
    dest = opts.dest

    c_string = opts.text
    d_string = opts.bin

    logger = BasicLogger(debug)
    engine.logger = logger

    for arg in args:
        logger.log("warn", f"'{arg}' is not a valid argument")

    if source:
        if c_string or d_string:
            logger.log("error", "Can't provide both string and filename")

        if not os.path.exists(source):
            logger.log("error", "Source file does not exist - try checking if its the correct full path")

        
        engine.verbose = verbose
        engine.debug = debug
        engine.override = override

        if os.path.splitext(source)[1] == ".bin":
            if dest and not os.path.splitext(dest)[1] == ".txt":
                logger.log("error", "Invalid destination file extension")

            return "d", source, dest, logger
        
        elif os.path.splitext(source)[1] in [".txt", ".py"]:
            if dest and not os.path.splitext(dest)[1] == ".bin":
                logger.log("error", "Invalid destination file extension")
            
            return "e", source, dest, logger

        else:
            logger.log("error", "Error not caught, program exiting")

    else:
        if c_string == d_string == False:
            logger.log("error", "Must include provide source file or string - 'nipzip -h' for help on usage")

        if c_string and d_string:
            logger.log("error", "Only one mode can be used at a time")

        if c_string:
            return "e", c_string, "STRING_MODE"

        elif d_string:
            return "d", d_string, "STRING_MODE"

def main(mode, infile, outfile):
    logger.log("info", "Command parsed, executing program")
    
    if outfile == "STRING_MODE":
        {"e":engine.string_compress,
         "d":engine.string_decompress}[mode](infile)
    else:
        {"e":engine.compress,
         "d":engine.decompress}[mode](infile, outfile)

    logger.forcelog("info", f"{'Compression' if mode == 'e' else 'Decompression'} successful, program has exited.")
    sys.exit()

if __name__ == "__main__":
    main(*parse_cmd(sys.argv))