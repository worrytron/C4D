# coding: UTF-8

from os.path import join
from espntools import debug

# Global variables for ESPN Animation projects pipeline

__docstring__  = "Backend utilities for ESPN's Cinema4D software pipeline. Intended for use with the ESPNPipelineMenu plug-in."
__author__     = "Mark Rohrer"
__copyright__  = "Copyright 2017, ESPN Productions"
__credits__    = ["Mark Rohrer", "Martin Weber"]
__license__    = "Educational use only, all rights reserved"
__version__    = "1.1.3"
__date__       = "2/22/17"
__maintainer__ = "Mark Rohrer"
__email__      = "mark.rohrer@espn.com"
__status__     = "Soft launch"

#debug.warning("Database is pathed locally. SETTINGS ARE NOT GLOBAL.")
#JSON_DB_PATH = "V:\\dev\\pipeline\\c4d"
JSON_DB_PATH  = "Y:\\Workspace\\SCRIPTS\\pipeline\\database"
PRODUCTION_DB = join(JSON_DB_PATH, "productions_db.json")
PRESETS_PATH  = "preset://espn.lib4d/{0}/{1}"

