#!/bin/env python

import os, sys, glob, shutil
from optparse import OptionParser

def main(argv = None):

    if argv == None:
        argv = sys.argv[1:]
    
    usage = "usage: %prog [options]\n Create list with sample names for postprocessing"
    
    parser = OptionParser(usage)
    
    parser.add_option("--input", type=str, default='/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21', help="Input directory [default: %default]")
    parser.add_option("--copy", type=str, default='TTGamma', help="Input directory [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

if __name__ == '__main__':

    options = main()

    cdir = os.getcwd()
    
    samples = [os.path.basename(f) for f in glob.glob(options.input+'/*')]

    with open('list.txt', 'w') as fw:
        for s in samples:
            copy = 0
            for v in options.copy.split(','):
                if v in s: copy = 1
            fw.write("%s %s\n" % (s, copy))
        fw.close()
