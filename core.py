# coding: UTF-8

#    Core wrapper for Cinema 4d Python API
#    - This wraps C4D functionality of a broad range of object operations with common conditionals
#      and error handling.  These functions have no other dependencies besides Maxon's c4d module.

import os.path
# internal libraries
import c4d
from c4d import gui
from c4d.modules import render

OVERRIDE_GROUPS = [
    #'bty',
    'pv_off',
    'black_hole',
    'disable',
    'enable'
    ]

# SIMPLE OPERATIONS ###############################################################################
def new():
    ''' Create a new empty document. '''
    c4d.CallCommand(12094, 12094)
    return

def open( file_=None ):
    ''' Open the specified scene.  If no file is specified, open a dialog. '''
    if (file_):
        c4d.documents.LoadFile(file_)
    else:
        c4d.CallCommand(12095, 12095)

def save( file_=None ):
    ''' Saves the current scene. '''
    c4d.CallCommand(12098, 12098)
    return

def saveAs( file_ ):
    ''' Saves the current scene with a new name. '''
    # Explicit output path / name
    if (file_):
        save_path = os.path.dirname(file_)
        save_file = os.path.basename(file_)

        doc().SetDocumentPath(save_path)
        doc().SetDocumentName(save_file)

        c4d.CallCommand(12098, 12098)

    # Dialog
    else: pass
    return

def close():
    ''' Closes the current scene. '''
    c4d.CallCommand(12664, 12664)
    return

def doc():
    ''' Returns the active document. '''
    return c4d.documents.GetActiveDocument()

def merge( file_=None ):
    ''' Imports a file into the scene. '''
    doc = c4d.documents.GetActiveDocument()
    if (file_):
        c4d.documents.LoadFile(file_)
    else:
        c4d.CallCommand(12096, 12096)
    return

def lookupID( id ):
    for k in c4d.__dict__.keys():
        if c4d.__dict__[k] == id:
            print k

# OBJECT-PARSING / SELECTION UTILITIES ############################################################
def ls( obj=None, typ=c4d.BaseObject, name=None ):
    ''' Returns a list of BaseObjects of specified type that are either currently selected,
        or passed by object reference. Both types are validated before being returned as a list.'''
    # Get selection if no object reference is passed
    if not (name or obj):
        obj = doc().GetSelection()

    # If a string is passed to name, the command will attempt to locate it by exact name.
    # Since C4D allows objects to have the same name, it will always return a list
    elif (isinstance(name, str)):
        start = doc().GetFirstObject()
        obj   = []
        for o in ObjectIterator(start):
            if o.GetName() == name:
                obj.append(o)

    # If a passed object is not already a list, we force the recast
    if not (isinstance(obj, list)):
        obj = [obj]
    
    # Cull any selected elements that don't match the specified object type
    for o in obj:
        if not (isinstance(o, typ)):
            obj.remove(o)
        else: continue

    # Returns a list of the specified object type, or none for an empty list
    if obj == []:
        obj = None
    return obj

def lsTags( obj=None, name=None, typ=None ):
    ''' Returns a list of tags in the scene.  Search parameters based on tag type or tag name.  At
    least one must be included in the command. '''
    if (name==None) and (typ==None):
        return
    return_tags = []
    # If an object reference is passed, search only its heirarchy
    if not (obj): obj = doc().GetFirstObject()

    for o in ObjectIterator(obj):
        # Search each object for tags
        for tag in TagIterator(o):
            # Compare the tag to requirements
            if (tag.GetName() == name) and (tag.GetType() == typ):
                return_tags.append(tag)
            elif (tag.GetName() == None) and (tag.GetType() == typ):
                return_tags.append(tag)
            elif (tag.GetName() == name) and (tag.GetType() == None):
                return_tags.append(tag)

    return return_tags

# REFERENCING & ASSET MANAGEMENT ##################################################################
def xref( namespace, ref, proxy=None ):
    doc = c4d.documents.GetActiveDocument()
    op  = c4d.BaseObject(c4d.Oxref)
    doc.InsertObject(op)
    op.SetParameter(c4d.ID_CA_XREF_FILE, ref, c4d.DESCFLAGS_SET_USERINTERACTION)
    op.SetParameter(c4d.ID_CA_XREF_NAMESPACE, namespace, c4d.DESCFLAGS_SET_USERINTERACTION)
    if proxy:
        op.SetParameter(c4d.ID_CA_XREF_PROXY_FILE, proxy, c4d.DESCFLAGS_SET_USERINTERACTION)
    c4d.EventAdd()
    return op

def swapXref( ref, new_ref_path ):
    try:
        ref.SetParameter(c4d.ID_CA_XREF_FILE, new_ref_path, c4d.DESCFLAGS_SET_USERINTERACTION)
        c4d.EventAdd()
    except: 
        debug.warning('The passed object is not a reference, or an invalid path was specified.')
    return True

# FLAGS & TAGS ####################################################################################
def visibility( obj_=None, v=None, r=None ):
    ''' Sets the visibility of an object. 'v' for viewport, and 'r' for rendering. '''
    doc = c4d.documents.GetActiveDocument()
    vis = {
        True:  c4d.MODE_ON,
        False: c4d.MODE_OFF,
        None:  c4d.MODE_UNDEF
    }
    # Get selection if no object is passed
    if not (obj_):
        obj_ = ls()
    # If a flag is passed, set it
    doc.StartUndo()
    for o in obj_:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, o)
        o.SetEditorMode(vis[v])
        o.SetRenderMode(vis[r])
    doc.EndUndo()
    return

def isVisible( obj_=None ):
    ''' Check an object (and its parents) for visibility. '''
    # get the selected object if none is passed
    if not obj_:
        obj_ = ls()[0]
    # first, check if the object is simply turned off
    if obj_.GetRenderMode() == 1.0:
        return False
    # second, check it for a compositing tag that might do so
    for tag in TagIterator(obj_):
        if tag.GetType() == c4d.Tcompositing:
            if tag[c4d.COMPOSITINGTAG_MATTEOBJECT] == 1:
                return False
            elif tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] == 0:
                return False
    # we must also iterate over the parents of the object
    parent = obj_.GetUp()
    while parent:
        if not isVisible(parent):
            return False
        else:
            parent = parent.GetUp()
    # all the parents must be visible
    return True

def tag( obj_=None, typ=None, name=None ):
    ''' Creates a tag on the selected (or specified) object. For tag types, see:
    https://developers.maxon.net/docs/Cinema4DPythonSDK/html/types/tags.html '''
    # Parse the passed object, or get the current selection
    doc = c4d.documents.GetActiveDocument()
    obj = ls(obj=obj_)
    # Empty return container
    tags = []
    # Make a tag for each object
    doc.StartUndo()
    for o in obj:
        tag = o.MakeTag(typ)
        # Add the tag to the return list
        tags.append(tag)
        # Name the tag
        if name:
            tag.SetName(name)
        doc.AddUndo(c4d.UNDOTYPE_NEW, tag)

    c4d.EventAdd()
    doc.EndUndo()
    return tags

# MATERIALS & TEXTURES ############################################################################
def changeTexture( mat, tex_path, channel=c4d.MATERIAL_COLOR_SHADER ):
    ''' Changes the texture on a material's specified channel.  Defaults to the color channel.
    C:\Program Files\MAXON\CINEMA 4D R17\resource\modules\c4dplugin\description\mmaterial.h '''
    doc = c4d.documents.GetActiveDocument()
    if isinstance(mat, str):
        for mat_ in MaterialIterator(doc()):
            if mat_.GetName() == mat:
                mat = mat_
                break

    if not isinstance(mat, c4d.Material):
        return

    doc.StartUndo()
    if type(channel) == int:
        tex = c4d.BaseList2D(c4d.Xbitmap)
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, tex)
        tex[c4d.BITMAPSHADER_FILENAME] = tex_path
        mat[channel] = tex
        mat.InsertShader(tex)
    elif channel == ('refl' or 'reflection'):
        refl_shd = mat.GetAllReflectionShaders()
        for rs in refl_shd:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, rs)
            rs[c4d.BITMAPSHADER_FILENAME] = tex_path

    mat.Message(c4d.MSG_UPDATE)
    mat.Update(1,1)
    c4d.EventAdd()
    c4d.EndUndo()
    return True

def changeColor( mat, vector, channel=c4d.MATERIAL_COLOR_COLOR, exact=True ):
    ''' Changes the color on a material's specified channel.  Defaults to the diffuse color channel.'''
    mats = []
    doc  = c4d.documents.GetActiveDocument()
    if isinstance(mat, str):
        for mat_ in MaterialIterator(doc()):
            if (exact):
                if mat_.GetName() == mat:
                    mats.append(mat_)
            elif not (exact):
                if mat in mat_.GetName():
                    mats.append(mat_)

    elif isinstance(mat, c4d.Material):
        mats = list(mat)

    if type(channel) == int:
        doc.StartUndo()
        for mat_ in mats:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, mat_)
            mat_[channel] = vector
            mat_.Message(c4d.MSG_UPDATE)
            mat_.Update(1,1)
    c4d.EventAdd()
    doc.EndUndo()
    return True

def createMaterial(name=None, color=None):
    ''' Create a new material. '''
    doc = c4d.documents.GetActiveDocument()
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    doc.StartUndo()
    doc.InsertMaterial(mat)
    if (name):
        mat.SetName(name)
    if (color):
        changeColor(mat, color)
    doc.AddUndo(c4d.UNDOTYPE_NEW, mat)
    c4d.EventAdd()
    doc.EndUndo()
    return mat

def getSceneTextures():
    ''' An object-based version of doc.GetAllTextures() -- i.e., returns an array of BaseList2D
        instead of a useless string tuple. 
        returns: Shader/channel (as BaseShader), path to bitmap (as str)'''
    # A list of shaders (channels) where textures may be found
    shaders = [
        c4d.MATERIAL_COLOR_SHADER,
        c4d.MATERIAL_DIFFUSION_SHADER,
        c4d.MATERIAL_LUMINANCE_SHADER,
        c4d.MATERIAL_TRANSPARENCY_SHADER,
        c4d.MATERIAL_REFLECTION_SHADER,
        c4d.MATERIAL_ENVIRONMENT_SHADER,
        c4d.MATERIAL_BUMP_SHADER,
        c4d.MATERIAL_ALPHA_SHADER,
        c4d.MATERIAL_SPECULAR_SHADER,
        c4d.MATERIAL_DISPLACEMENT_SHADER,
        c4d.MATERIAL_NORMAL_SHADER
        ]
    # output container
    output = []
    # iterate over all materials in the scene
    for mat in MaterialIterator(doc()):
        # the standard list of channels / shaders (including legacy reflection/specular)
        for shd in shaders:
            # test material for active shader
            shd = mat[shd]
            if (shd):
                # test that active shader for a bitmap 
                tex_path = shd[c4d.BITMAPSHADER_FILENAME]
                if (tex_path):
                    # get the path and add it to the list
                    tex_path = c4d.GenerateTexturePath(doc().GetDocumentPath(), tex_path, '')
                    output.append([shd, tex_path])
        # the new-style of reflection/specular channels
        for shd in mat.GetAllReflectionShaders():
            tex_path = shd[c4d.BITMAPSHADER_FILENAME]
            if (tex_path):
                tex_path = c4d.GenerateTexturePath(doc().GetDocumentPath(), tex_path, '')
                output.append([shd, tex_path])
    return output

def getGlobalTexturePaths():
    ''' Generates a list of all the user's global texture paths locations. '''
    paths = []
    for i in range(10):
        path = c4d.GetGlobalTexturePath(i)
        if path is not '':
            paths.append(path)
    return paths

# TAKE / RENDER LAYER / RENDERDATA UTILITIES ######################################################
def take( name=None, set_active=False ):
    ''' Create a new take / render layer. '''
    # TakeData is a singleton container for all the takes in the scene
    doc = c4d.documents.GetActiveDocument()
    td  = doc.GetTakeData()

    # Iterate over all takes to see if one with that name already exists
    main = td.GetMainTake()
    for take in ObjectIterator(main):
        if (take.GetName() == name):
            return take

    doc.StartUndo()
    # Otherwise add the take and name it
    take = td.AddTake(name, parent=None, cloneFrom=None)
    # Add the default override groups to the take
    doc.AddUndo(c4d.UNDOTYPE_NEW, take)
    for og_ in OVERRIDE_GROUPS:
        if og_ == 'bty':
            continue
        og = override(take, og_)
        mat = createMaterial()
        # Add the compositing tag for overriding
        tag = og.AddTag(td, c4d.Tcompositing, mat=mat)
        tag.SetName('VISIBILITY_OVERRIDE')
        # ... and set the default values
        setCompositingTag( tag, og_ )
        mat.Remove()
    # If flagged, set the current take as active
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, take)
    if (set_active): td.SetCurrentTake(take)
    take.SetChecked(True)

    c4d.EventAdd()
    doc.EndUndo()
    return take

def setOutputPaths( rgb_path, multi_path ):
    doc = c4d.documents.GetActiveDocument()
    rd  = doc.GetActiveRenderData()
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, rd)
    rd[c4d.RDATA_PATH] = str(rgb_path)
    rd[c4d.RDATA_MULTIPASS_FILENAME] = str(multi_path)
    doc.EndUndo()
    c4d.EventAdd()
    return True

def setOutputFiletype( filetype, depth=None, primary=True, multipass=True, rd=None ):
    doc = c4d.documents.GetActiveDocument()
    if (rd == None):
        rd = doc.GetActiveRenderData()

    filetype = filetype.lower()

    format_lookup = {
        'png': 1023671,
        'exr': 1016606
    }
    depth_lookup = {
        8: 0,
        16: 1,
        32: 2
    }
    doc.StartUndo()
    if (primary == True):
        rd[c4d.RDATA_FORMAT] = format_lookup[filetype]
        if ((depth != None) and (filetype != 'exr')):
            rd[c4d.RDATA_FORMATDEPTH] = depth_lookup[depth]

    if (multipass == True):
        rd[c4d.RDATA_MULTIPASS_SAVEFORMAT] = format_lookup[filetype]
        if ((depth != None) and (filetype != 'exr')):
            rd[c4d.RDATA_MULTIPASS_SAVEDEPTH] = depth_lookup[depth]

    c4d.EventAdd()
    doc.EndUndo()
    return True

def override( take, name=None ):
    ''' Adds an override group to a specified take. '''
    og = take.AddOverrideGroup()
    if (name): og.SetName(name)

    c4d.EventAdd()
    return og

def getCheckedTakes():
    ''' Gets a list (BaseTake) of all checked takes in the scene.'''
    checked_takes = []
    doc = c4d.documents.GetActiveDocument()
    td = doc.GetTakeData()
    for take in ObjectIterator(td.GetMainTake()):
        if take.IsChecked():
            checked_takes.append(take)
    return checked_takes

def setCompositingTag( tag, preset, reset=False ):
    ''' Sets a compositing tag with preset values for primary visibility, etc.'''
    # Some overrides take place on the override group, so we store tha
    og = tag.GetObject()
    # In the event that this isn't called at creation, we first reset the affected values to default
    if (reset):
        og.SetEditorMode(c4d.MODE_UNDEF)
        og.SetRenderMode(c4d.MODE_UNDEF)
        tag[c4d.COMPOSITINGTAG_CASTSHADOW] = True
        tag[c4d.COMPOSITINGTAG_RECEIVESHADOW] = True
        tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = True
        tag[c4d.COMPOSITINGTAG_SEENBYRAYS] = True
        tag[c4d.COMPOSITINGTAG_SEENBYGI] = True
        tag[c4d.COMPOSITINGTAG_SEENBYTRANSPARENCY] = True
        tag[c4d.COMPOSITINGTAG_MATTEOBJECT] = False
        tag[c4d.COMPOSITINGTAG_MATTECOLOR] = c4d.Vector(0,0,0)

    # Now the business
    if (preset) == 'bty':
        pass
    elif (preset) == 'pv_off':
        tag[c4d.COMPOSITINGTAG_CASTSHADOW] = True
        tag[c4d.COMPOSITINGTAG_RECEIVESHADOW] = False
        tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = False
        tag[c4d.COMPOSITINGTAG_SEENBYRAYS] = True
        tag[c4d.COMPOSITINGTAG_SEENBYGI] = True
    elif (preset) == 'black_hole':
        tag[c4d.COMPOSITINGTAG_MATTEOBJECT] = True
        tag[c4d.COMPOSITINGTAG_MATTECOLOR] = c4d.Vector(0,0,0)
    elif (preset) == 'disable':
        og.SetEditorMode(c4d.MODE_OFF)
        og.SetRenderMode(c4d.MODE_OFF)
        tag[c4d.COMPOSITINGTAG_CASTSHADOW] = False
        tag[c4d.COMPOSITINGTAG_RECEIVESHADOW] = False
        tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = False
        tag[c4d.COMPOSITINGTAG_SEENBYRAYS] = False
        tag[c4d.COMPOSITINGTAG_SEENBYGI] = False
        tag[c4d.COMPOSITINGTAG_SEENBYTRANSPARENCY] = False
    elif (preset) == 'enable':
        og.SetEditorMode(c4d.MODE_ON)
        og.SetEditorMode(c4d.MODE_ON)

    c4d.EventAdd()
    return

def createRenderData( rd, name ):
    ''' Inserts a RenderData document into the scene, overwriting any other document with the same
    name.  Seriously, fuck C4D sometimes. '''
    doc   = c4d.documents.GetActiveDocument()
    start = doc.GetFirstRenderData()
    doc.StartUndo()
    for rd_ in ObjectIterator(start):
        if rd_.GetName() == name:
            doc.AddUndo(c4d.UNDOTYPE_DELETE, rd_)
            rd_.Remove()
    rd.SetName(name)
    doc.InsertRenderData(rd)
    doc.AddUndo(c4d.UNDOTYPE_NEW, rd)
    doc.SetActiveRenderData(rd)
    c4d.EventAdd()
    doc.EndUndo()
    return

def createChildRenderData( rd, suffix=False, set_active=False ):
    ''' Inserts a new RenderData as a child to an existing one, including a name suffix.'''
    if rd.GetUp():
        msg = 'Warning: This Render Data is already a child of an existing one. Canceling operation...'
        gui.MessageDialog(msg)
        return False
    doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    child_rdata = c4d.documents.RenderData()
    child_rdata.SetData(rd.GetData())
    doc.InsertRenderData(child_rdata, pred=rd)
    doc.AddUndo(c4d.UNDOTYPE_NEW, rd)
    child_rdata.InsertUnder(rd)

    for multipass in ObjectIterator(rd.GetFirstMultipass()):
        new_mpass = c4d.BaseList2D(c4d.Zmultipass)
        new_mpass.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = multipass.GetType()
        new_mpass.SetData(multipass.GetData())
        child_rdata.InsertMultipass(new_mpass)
    for videopost in ObjectIterator(rd.GetFirstVideoPost()):
        new_vpost = c4d.BaseList2D(videopost.GetType())
        new_vpost.SetData(videopost.GetData())
        child_rdata.InsertVideoPost(new_vpost)

    if (type(suffix) == str):
        name = '{} {}'.format(child_rdata.GetName(), suffix)
        child_rdata.SetName(name)
    if (set_active): doc.SetActiveRenderData(child_rdata)

    c4d.EventAdd()
    doc.EndUndo()
    return child_rdata
        
### The following iterators were borrowed directly from Martin Weber via cgrebel.com.
### All credit goes to him -- thank you Martin! -- I could not find any license usage for this code.
### http://cgrebel.com/2015/03/c4d-python-scene-iterator/
class ObjectIterator:
    ''' Iterates over all BaseObjects below the input object in the hierarchy, including children. '''
    def __init__(self, baseObject):
        self.baseObject = baseObject
        self.currentObject = baseObject
        self.objectStack = []
        self.depth = 0
        self.nextDepth = 0

    def __iter__(self):
        return self

    def next(self):
        if self.currentObject == None :
            raise StopIteration

        obj = self.currentObject
        self.depth = self.nextDepth

        child = self.currentObject.GetDown()
        if child :
            self.nextDepth = self.depth + 1
            self.objectStack.append(self.currentObject.GetNext())
            self.currentObject = child
        else :
            self.currentObject = self.currentObject.GetNext()
            while( self.currentObject == None and len(self.objectStack) > 0 ) :
                self.currentObject = self.objectStack.pop()
                self.nextDepth = self.nextDepth - 1
        return obj

class TagIterator:
    ''' Iterates over all tags on a given object. '''
    def __init__(self, obj):
        currentTag = None
        if obj :
            self.currentTag = obj.GetFirstTag()

    def __iter__(self):
        return self

    def next(self):
        tag = self.currentTag
        if tag == None :
            raise StopIteration

        self.currentTag = tag.GetNext()
        return tag

class MaterialIterator:
    ''' Iterates over all materials in a given document. '''
    def __init__(self, doc):
        self.doc = doc
        self.currentMaterial = None
        if doc == None : return
        self.currentMaterial = doc.GetFirstMaterial()

    def __iter__(self):
        return self

    def next(self):
        if self.currentMaterial == None :
            raise StopIteration

        mat = self.currentMaterial
        self.currentMaterial = self.currentMaterial.GetNext()
        return mat

