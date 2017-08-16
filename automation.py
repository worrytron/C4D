# Automation tools for ESPN Animation projects pipeline

import c4d
import os.path
import shutil
from c4d import gui

from espntools import core
from espntools import scene
from espntools import database

# TEAM AUTOMATION #################################################################################
def assignTeamColors( tricode, location, swap=False ):
    scene_data    = scene.getSceneData()
    color_vectors = database.getTeamColors(scene_data['Production'], tricode)

    core.changeColor('{0}_PRIMARY'.format(location.upper()), color_vectors['primary'], exact=False)
    core.changeColor('{0}_SECONDARY'.format(location.upper()), color_vectors['secondary'], exact=False)
    core.changeColor('{0}_TERTIARY'.format(location.upper()), color_vectors['tertiary'], exact=False)

    return True

def sortTagObject( name=None ):
    if not (name):
        name = c4d.RenameDialog('')
    if not (name == ''):
        tags = core.tag(typ=c4d.Tannotation, name=name)
    core.visibility(tags, v=False, r=False)

def relinkTextures( migrate=False ):
    ''' Searches the scene for all referenced textures.  If any texture found already exists in the
        production's main texture repository, it changes the link to the production version instead.
        Optional migrate flag will prompt the user to select which remaining textures they would like
        moved & relinked to production folders.'''
    doc          = c4d.documents.GetActiveDocument()
    scn          = scene.Scene()
    doc_tex_dir  = os.path.join(doc.GetDocumentPath(), 'tex')
    prod_tex_dir = os.path.join(scn.prod_data['assets'], 'TEXTURES')
    # container dictionary of textures that have been relinked
    '''relinked_tex = {}'''
    # container for textures that haven't been checked in yet
    new_tex      = []
    # Build an array with all textured channels in the scene
    textures     = core.getSceneTextures()
    doc.StartUndo()
    for tex in textures:
        # Extrapolating texture information
        shd, tex_path = tex
        if tex_path == None: continue
        if not (os.path.isfile(tex_path)): continue
        tex_dir       = os.path.dirname(tex_path)
        tex_name      = os.path.basename(tex_path)

        # split the texture name and see if it contains a team tricode prefix
        tricode_      = tex_name.split('_')[0]
        is_team_tex   = database.isTricode(scn.production, tricode_)
        # if it does contain a tricode prefix, we search for the texture in an asset folder instead
        if (is_team_tex): 
            team_tex_dir = os.path.join(scn.prod_data['teams'], tricode_, 'tex')
        else: 
            tricode_ = None

        # Build a texture search path for an existing texture
        if not (is_team_tex):
            existing_tex = os.path.join(prod_tex_dir, tex_name)
        elif (is_team_tex):
            existing_tex = os.path.join(team_tex_dir, tex_name)

        # If an existing texture is found in the project folders:
        if (os.path.isfile(existing_tex)):
            # RELINK THE TEXTURE
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, shd)
            shd[c4d.BITMAPSHADER_FILENAME] = str(existing_tex)
            # Tag the original for possible deletion
            '''
            if not (tex_path in relinked_tex):
                relinked_tex[tex_path] = []
            relinked_tex[tex_path].append((tricode_, shd))
            '''
        # Otherwise it must be a new (or possibly scene-unique) texture...
        #    "new_tex" is a list of new textures that have not yet been migrated into project folders.
        #    tuple[0] is the current path of the texture on the server
        #    tuple[1] is the tricode of the team the texture belongs to (otherwise None for generic)
        # This list then gets passed to the UI function (the if-statement below) for the user to control
        else:
            new_tex.append((tex_path, tricode_))
    doc.EndUndo()
    
    if (migrate) and (len(new_tex) > 0):
        # We pass the list of "new" textures to a UI for users to select which to migrate
        # This UI will copy the textures into project folders, and re-run this func to link them
        test = TextureMigrateWindow(set(new_tex))
        test.Open(dlgtype=c4d.DLG_TYPE_MODAL, defaultw=800, defaulth=50)

### UI OBJECTS ###################################################################################
class TextureMigrateWindow(gui.GeDialog):
    def __init__(self, texture_list):
        # Texture migration UI values
        self.INSTRUCTIONS = 90000
        self.CHKBOX_START = 10000
        self.CHKBOX_DATA  = {}
        self.BUTTON_OK    = 20000
        self.BUTTON_CANCEL= 20001

        self.TEX_DATA = texture_list

        i = self.CHKBOX_START
        for texture_path in texture_list:
            # keys of this dictionary are texture paths
            self.CHKBOX_DATA[i] = texture_path
            i+=1

        self.left   = c4d.BFH_LEFT
        self.center = c4d.BFH_CENTER
        self.right  = c4d.BFH_RIGHT

    def CreateLayout(self):
        self.SetTitle('Migrate Textures')
        self.GroupBegin(1000, flags=c4d.BFH_SCALEFIT, rows=1, cols=1, title="Instructions")
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(5,5,5,5)
        msg = """Select the textures you would like to move into production global folders.
All moved textures will be relinked in your scene.  Textures left unchecked
will remain where they are.

NOTE: Team textures (identified by TRICODE_ prefix) will be moved to the 
team's asset /tex/ folder.
"""
        self.AddMultiLineEditText(self.INSTRUCTIONS, c4d.BFH_SCALEFIT, c4d.BFV_SCALEFIT, inith=60, style=c4d.DR_MULTILINE_READONLY)
        #self.Enable(self.INSTRUCTIONS, False)
        self.SetString(self.INSTRUCTIONS, msg)
        self.GroupEnd()

        self.GroupBegin(1001, c4d.BFH_SCALE, 2, 0, initw=800, title='Textures to check-in')
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(5,5,5,5)
        for i in range(len(self.CHKBOX_DATA)):
            i += self.CHKBOX_START
            name = self.CHKBOX_DATA[i][0]
            self.AddCheckbox(i, self.left, name='', initw=20, inith=0)
            self.AddStaticText(1002, self.left, name=name)
        self.GroupEnd()

        self.GroupBegin(1002, c4d.BFH_RIGHT, 2, 1)
        self.AddButton(self.BUTTON_OK, c4d.BFH_RIGHT, inith=30, name='Migrate Textures')
        self.AddButton(self.BUTTON_CANCEL, c4d.BFH_RIGHT, inith=30, name='Cancel')
        self.GroupEnd()
        return True

    def Command(self, id, msg):
        if (id==self.BUTTON_OK):
            self.run()
            self.Close()
            relinkTextures()
        return True

    def run(self):
        ''' Iterates over all selected checkboxes in the UI, copying the checked textures into the correct
            folder for that production.'''
        scn = scene.Scene()
        global_texture_path = os.path.join(scn.prod_data['assets'], 'TEXTURES')
        team_texture_path   = scn.prod_data['teams']

        for i in range(len(self.CHKBOX_DATA)):
            #CHKBOX_DATA (path & tricode) is a parallel array to CHKBOX_START (UIIDs)
            i += self.CHKBOX_START
            # is the box checked
            chk = self.GetBool(i)
            if (chk):
                # pull the data from the parallel array
                tex_path, tricode = self.CHKBOX_DATA[i]
                if not (tricode):
                    print 'copying', tex_path, 'to ', global_texture_path
                    shutil.copy2(tex_path, global_texture_path)
                elif (tricode):
                    print 'copying', tex_path, 'to ', tricode, ' folder'
                    shutil.copy2(tex_path, os.path.join(team_texture_path, tricode, 'tex'))


