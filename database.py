# JSON Database operations for ESPN Animation projects pipeline

import c4d
import json
import os.path
#
from espntools import debug

__schema__     = [1.0, 1.0]
__platform__   = "c4d"
__dashboard__  = None
__nasroot__    = "Y:\\Workspace"
__pubroot__    = "Y:\\PublishData"
__logdir__     = "Y:\\Workspace\\SCRIPTS\\ESPNTools\\.logs\\{0}"
__globaldb__   = "Y:\\Workspace\\SCRIPTS\\ESPNTools\\.json\\productions.json"
__assetsdb__   = "Y:\\Workspace\\SCRIPTS\\ESPNTools\\.json\\global_assets.json"
__c4dpresets__ = "preset://espn.lib4d/{0}/{1}"

# GETTERS ##########################################################################################
def getProduction(prod_):
    ''' Gets a production's global variables from the database. '''
    def merge(src,dest):
        for k,v in src:
            dest[k] = v

    merged_prod = {}
    with open(__globaldb__, 'r') as stream:
        full_db = json.load(stream)

        try:
            prod_db = full_db[prod_]
        except KeyError:
            raise debug.DatabaseError(1)
        # The project dictionaries only store the delta of data in the default dictionary
        # Therefore we merge the requested project dictionary over top of the default to create
        # a complete data set.
        return prod_db

def getFolderStructure():
    with open(__globaldb__, 'r') as stream:
        return json.load(stream)["FOLDER_TEMPLATE"]

def getPlatformData(prod_):
    ''' Gets the platform (C4D-specific) data for a particular production.'''
    with open(getProduction(prod_)['json']['c4d']) as stream:
        return json.load(stream)
        

def getAllProductions():
    ''' Gets a list of all available / valid productions from the database. '''
    productions = []
    with open(__globaldb__, 'r') as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            if (k == 'NULL' or k == 'ESPN_META' or k == 'FOLDER_TEMPLATE'):
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
        dirs = os.listdir(prod['folder_lookup']['animroot'])
        for d in dirs:
            if (os.path.isdir(os.path.join(prod['folder_lookup']['animroot'], d))):
                proj_list.append(d)
    except WindowsError:
        pass
    return sorted(proj_list)


def getAllPresets(prod_):
    ''' Gets all render presets associated with a production.'''
    return sorted(getPlatformData(prod_)["presets"])

    
def getTeamDatabase(prod_):
    ''' Gets the team database for a production. '''
    prod_db  = getProduction(prod_)
    with open(prod_db['json']['teams'], 'r') as stream:
        return json.load(stream)

def getTeam(prod_, lookup, squelch=False):
    ''' Gets a team from a production using its key.'''
    team_db = getTeamDatabase(prod_)
    for k,v in team_db.iteritems():
        if (k == lookup):
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

def getTeamColors(prod_, lookup, squelch=False):
    team = getTeam(prod_, lookup, squelch=squelch)
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

"""
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
"""

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
