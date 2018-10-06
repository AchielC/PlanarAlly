import dbm
import os
import shelve
import sys

SAVE_VERSION = 3

def check_save(save_file):
    try:
        shelf = shelve.open(save_file, 'r')
    except dbm.error:
        print("Provided save file does not exist. Creating a new one.")
        shelf = shelve.open(save_file, 'c')
        shelf['save_version'] = SAVE_VERSION
    else:
        if "save_version" not in shelf:
            print("Save file has no save version. Cannot open.")
            sys.exit(2)
        if shelf['save_version'] != SAVE_VERSION:
            print("Current save version {} does not match the expected save version {}".format(shelf['save_version'], SAVE_VERSION))
            print("If available you can try to convert the save_formats using the conversion scripts. consult the documentation for more information.")
            sys.exit(2)
