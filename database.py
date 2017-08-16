# JSON Database operations for ESPN Animation projects pipeline

import c4d
import json
import os.path
#
from espntools import debug
from espntools.gvars import *

PRODUCTION_DB    = "Y:\\Workspace\\Scripts\\ESPNTools\\.json\\productions.json"
GLOBALASSETS_DB  = "Y:\\Workspace\\Scripts\\ESPNTools\\.json\\global_assets.json"

PRESETS_PATH  = "preset://espn.lib4d/{0}/{1}"

# GETTERS ##########################################################################################
def getProduction(prod_):
    ''' Gets a production's global variables from the database. '''
    def merge(src,dest):
        for k,v in src:
            dest[k] = v

    merged_prod = {}
    with open(PRODUCTION_DB, 'r') as stream:
        full_db = json.load(stream)

        try:
            prod_db = full_db[prod_]
        except KeyError:
            raise debug.DatabaseError(1)
        # The project dictionaries only store the delta of data in the default dictionary
        # Therefore we merge the requested project dictionary over top of the default to create
        # a complete data set.
        return prod_db
"""
def getProductionDirty():
    ''' Infers the project based on where the current scene is located. '''
    scene_path = core.doc().GetDocumentPath()
    scene_path = scene_path.split('\\')
    prod_      = scene_path[3]

    try:
        prod   = PRODUCTIONS[proj_]
        return prod
    except KeyError:
        raise debug.PipelineError(3)
"""
def getAllProductions():
    ''' Gets a list of all available / valid productions from the database. '''
    productions = []
    with open(PRODUCTION_DB, 'r') as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            if (k == 'DEFAULT'):
                continue
            else:
                productions.append(k)
    return sorted(productions)

def getAllProjects(prod_):
    ''' Gets all projects associated with a production.'''
    prod = getProduction(prod_)
    #return [p for p in os.listdir(prod['project']) if os.path.isdir(os.path.join(prod['project'], p))]
    proj_list = []
    try:
        dirs = os.listdir(prod['project'])
        for d in dirs:
            if (os.path.isdir(os.path.join(prod['project'], d))):
                proj_list.append(d)
    except WindowsError:
        pass
    return sorted(proj_list)

def getAllPresets(prod_):
    ''' Gets all render presets associated with a production.'''
    prod = getProduction(prod_)
    return sorted(prod["presets"])
    
def getTeamDatabase(prod_):
    ''' Gets the team database for a production. '''
    prod_db  = getProduction(prod_)
    if (prod_db['is_default'] == True):
        raise debug.DatabaseError(1)

    team_db_ = prod_db['team_db']
    db_path  = os.path.join(JSON_DB_PATH, '{0}.json'.format(team_db_))

    with open(db_path, 'r') as stream:
        full_db = json.load(stream)

    return full_db

def getTeam(prod_, tricode, squelch=False):
    ''' Gets a team from a production, based on tricode or full name.'''
    team_db = getTeamDatabase(prod_)
    for k,v in team_db.iteritems():
        if (tricode == k):
            return team_db[k]
        elif ('{0} {1}'.format(team_db[k]['city'], team_db[k]['nick']) == tricode):
            return team_db[k]
    # if it gets this far, the team wasn't found in the database.
    #raise debug.DatabaseError(2, alert=1-squelch)

def getAllTeams(prod_, name='tricode'):
    ''' Gets a list of all teams for a given production. '''
    team_db = getTeamDatabase(prod_)
    team_ls = []
    if name == 'tricode':
        for k in team_db:
            team_ls.append(k)
        return sorted(team_ls)
    elif name == 'full':
        for k,v in team_db.iteritems():
            team_ls.append('{0} {1}'.format(team_db[k]['city'], team_db[k]['nick']))
        return sorted(team_ls)
    elif name == 'city':
        for k,v in team_db.iteritems():
            team_ls.append('{0}'.format(team_db[k]['city']))
        return sorted(team_ls)
    elif name == 'nick':
        for k,v in team_db.iteritems():
            team_ls.append('{0}'.format(team_db[k]['nick']))
        return sorted(team_ls)

def getTeamColors(prod_, tricode, squelch=False):
    team = getTeam(prod_, tricode, squelch=squelch)
    ret_colors = {
        'primary': c4d.Vector(*convertColor(team['primary'])),
        'secondary': c4d.Vector(*convertColor(team['secondary'])),
        'tertiary': c4d.Vector(*convertColor(team['tertiary']))
        }
    return ret_colors

def isTricode(prod_, tricode):
    try:
        team = getTeam(prod_, tricode)
        return True
    except:
        return False

def makeTeamFolders(prod_):
    team_folder = getProduction(prod_)['teams']
    for t in getAllTeams(prod_):
        tri_folder = os.path.join(team_folder, t)
        tex_folder = os.path.join(tri_folder, 'tex')
        if not os.path.isdir(tri_folder):
            os.makedirs(tri_folder)
        if not os.path.isdir(tex_folder):
            os.makedirs(tex_folder)
    return True

def convertColor(colorvec, to='float'):
    ''' Converts a color vector from 0-255 (int) to 0-1 (float) or back again. '''
    def _clamp(value):
        if value < 0: return 0
        if value > 255: return 255
    if (to == 'float'):
        r_ = (1.0/255) * colorvec[0]
        g_ = (1.0/255) * colorvec[1]
        b_ = (1.0/255) * colorvec[2]
        return (r_, g_, b_)
    if (to == 'int'):
        r_ = _clamp(int(255 * colorvec[0]))
        g_ = _clamp(int(255 * colorvec[1]))
        b_ = _clamp(int(255 * colorvec[2]))
        return (r_, g_, b_)
