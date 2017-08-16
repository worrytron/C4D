# coding: UTF-8

# built-in libraries
from os import makedirs
from functools import wraps
import os.path
# c4d libraries
import c4d
from c4d import gui
# custom libraries
from espntools import core
from espntools import database
from espntools import debug
from espntools.gvars import *

class MetaScene(object):
    ''' MetaScene is an mapper / wrapper for scene files in Cinema 4D's Python API. It consists of convenience functions
    and JSON database integration for ESPN's Motion Graphics pipeline. 

    Mapping direction is as follows:
    User Input --> MetaScene --> Database --> MetaScene --> Cinema 4D Scene --> MetaScene --> Feedback

    The "virtual" scene (i.e. the metadata) consists of transient data from a database or an active scene.
    The "real" scene (i.e. a c4d.BaseDocument object) is the target of most operations.
    The internal naming convention is careful to distinguish these two entities (i.e. "vscene" and "rscene".)

    The JSON databases are currently static, and therefore the mapping is effectively unidirectional. '''

    production   = ''
    project_name = ''
    scene_name   = ''
    file_path    = ''
    prod_data    = {}
    version      = 0
    framerate    = 0
    scene_ctrl   = None
    scene_tag    = None
    cleanup      = []
    previous     = None

    ### Constructors
    def __init__(self, null=False):
        if (self.is_tagged()) and not (null):
            self._get_rscene_data()
            self._set_vscene_path()
        #self.is_sync()

    def __repr__(self):
        _repr  = 'PRODUCTION: {0}\n'
        _repr += 'PROJECT: {1}\n'
        _repr += 'SCENE: {2}\n'
        _repr += 'FRAMERATE: {3}\n'
        _repr += 'VERSION: {4}\n'

        return _repr.format(
            self.production,
            self.project_name,
            self.scene_name,
            self.framerate,
            self.version
            )

    @classmethod
    def from_data(self, data, set_output=False, set_frate=False, set_rdata=False, save=False):
        ''' Create a new scene from a passed dictionary of values (data).
        set_output (bool): set render output paths on the real scene
        set_rdata (bool): apply the default renderdata preset for this production
        save (bool): save the scene after creation.
        data['production'] (str): the production ID. Must match the equivalent entry in the database
        data['project_name'] (str): the name of the container project folder on the server
        data['scene_name'] (str): the descriptive name of this scene
        data['framerate'] (int): the framerate of the new scene 
        data['version'] (int): the version of the new scene '''

        this_scene = self()
        if (this_scene.is_tagged()):
            this_scene._clr_rscene_hook(force=True)

        this_scene.production   = data['production']
        this_scene.project_name = data['project_name']
        this_scene.scene_name   = data['scene_name']
        this_scene.framerate    = data['framerate']
        this_scene.version      = data['version']

        this_scene.prod_data    = database.getProduction(this_scene.production)

        this_scene._bld_rscene_hook()
        this_scene._set_rscene_data()
        this_scene._set_vscene_path()
        this_scene._bld_project_dir()

        if (set_rdata):  this_scene._set_rscene_renderdata()
        if (set_output): this_scene._set_rscene_output_paths()
        if (set_frate):  this_scene._set_rscene_framerate()
        if (save):       this_scene.save()
        
        return this_scene

    ### Public methods
    def is_tagged(self):
        ''' Confirms whether valid pipeline metadata tags are present in the scene. Attaches valid tags to virtual scene.
        Returns: bool. '''
        return self._get_rscene_hook()[0]

    def is_sync(self):
        ''' Confirms whether the loaded "virtual" scene matches the active "real" scene in the user's viewport. '''
        return True

    ## Push/pull synchronization operations
    def pull_from_scene(self):
        self._get_rscene_hook()
        self._get_rscene_data()
        self._set_vscene_path()
        return True

    def push_to_scene(self):
        self._get_rscene_hook()
        self._set_rscene_data()
        self._set_vscene_path()
        return True

    def save(self):
        ''' Save the active scene and make a backup. '''
        def increment(filename):
            ''' This function takes a valid backup file-name and searches the destination folder for the 
            next valid version increment.  Note this is a fairly 'dumb' process, but ensures that a 
            particular backup is never overwriting an existing one. '''
            if not os.path.exists(filename):
                return filename

            file_path = os.path.dirname(filename)
            file_name = os.path.basename(filename)
            file_name = file_name.split('.')
            name      = file_name[0]
            ext       = file_name[len(file_name)-1]

            if len(file_name) == 2:
                cur_vers = 1
            elif len(file_name) == 3:
                cur_vers = int(file_name[1])+1
            else:
                raise debug.FileError(2)

            incr_name = "{0}.{1}.{2}".format(name, str(cur_vers).zfill(4), ext)
            incr_file = os.path.join(file_path, incr_name)

            if os.path.exists(incr_file):
                incr_file = increment(incr_file)
            return incr_file

        # validate before running
        backup_file  = os.path.join(self.backup_folder, self.file_name)
        backup_path  = increment(backup_file)

        if not os.path.exists(self.backup_folder):
            makedirs(self.backup_folder)
        if not os.path.exists(self.file_folder):
            makedirs(self.file_folder)

        try:
            core.saveAs(backup_path)
            core.saveAs(self.file_path)
        except debug.FileError:
            raise debug.FileError(0)

    def rename(self, name=None):
        ''' Rename the active scene without moving it to a new project folder.'''
        old_name = self.scene_name
        if (name == None):
            dlg = c4d.gui.RenameDialog(old_name)
            if (dlg==old_name) or (dlg==None) or (dlg==False):
                return
            else: name = dlg
        # store the old name and update self
        self.scene_name = name
        self._set_vscene_path()
        # check that the new file doesn't already exist
        if os.path.isfile(self.file_path):
            msg = 'Warning: A scene with this name already exists -- proceed anyway? (Existing renders may be overwritten -- check your output version before rendering!)'
            prompt = c4d.gui.MessageDialog(msg, c4d.GEMB_OKCANCEL)
            if (prompt == c4d.GEMB_R_OK):
                pass
            elif (prompt == c4d.GEMB_R_CANCEL):
                # restore the old scene name and exit
                self.scene_name = old_name
                self._set_vscene_path()
                return
        # set clean version, update scene_ctrl with new data, and save
        self.version = 1
        self._set_rscene_data()
        self._set_rscene_output_paths()
        self.save()
        return True

    def version_up(self):
        ''' Increment the scene's render output folder and save. '''
        self.version += 1
        self._set_rscene_data()
        self._set_rscene_output_paths()
        self.save()
        return True

    ## Get operations (real scene)
    def _get_rscene_hook(self):
        ''' Checks for hooks in the active scene. Sets virtual scene status accordingly.
            Returns: (Bool, c4d.Tannotation) '''
        scene_ctrl = core.ls(name='__SCENE__')
        if (scene_ctrl == None) or (scene_ctrl == []):
            return (False, None)

        elif (len(scene_ctrl)>1):
            self.cleanup += scene_ctrl
            return (False, None)

        elif (len(scene_ctrl)==1):
            scene_tag = core.lsTags(name='SCENE_DATA', typ=c4d.Tannotation, obj=scene_ctrl[0])
            if not (scene_tag):
                self.cleanup += scene_ctrl
                return (False, None)
            else:
                self.scene_ctrl = scene_ctrl[0]
                self.scene_tag  = scene_tag[0]
                return (True, self.scene_tag)
        else: 
            debug.warning("Unhandled exception in get_rscene_hook().")
            return (False, None)
    
    def _get_rscene_data(self):
        ''' Retrieve data from active scene hooks. Populate virtual scene with that information. Performs no validation. '''
        def tag_to_dict(tag_data):
            ''' Takes a block of text from an annotation tag field and converts it to a dictionary.'''
            a = tag_data.split('\n')
            b = {}
            for a_ in a:
                kv = a_.split(':')
                b[kv[0]] = kv[1].lstrip()
            return b
        # store a copy of the previous version of this object
        self.previous = self
        # parse the scene tag string into a dictionary
        self._get_rscene_hook()
        scene_data = tag_to_dict(self.scene_tag[c4d.ANNOTATIONTAG_TEXT])
        # populate attributes from dictionary
        self.production   = scene_data['Production']
        self.prod_data    = database.getProduction(self.production)
        self.project_name = scene_data['Project']
        self.scene_name   = scene_data['Scene']
        self.framerate    = int(scene_data['Framerate'])
        self.version      = int(scene_data['Version'])
        self._set_vscene_path()
        return True

    ## Set operations (virtual scene)
    def _set_vscene_path(self):
        ''' Update internal path data for the scene when it is moved or renamed. '''
        try:
            project_folder = self.prod_data['project']
        except KeyError:
            debug.info('', self.prod_data)
            raise debug.FileError(1)
        self.file_name     = '{0}_{1}.c4d'.format(self.project_name, self.scene_name)
        self.file_folder   = os.path.join(self.prod_data['project'], self.project_name, 'c4d')
        self.backup_folder = os.path.join(self.file_folder, 'backup')
        self.file_path     = os.path.join(self.file_folder, self.file_name)

    ## Set operations (real scene)
    def _set_rscene_data(self):
        ''' Push data from the virtual scene to the hooks in the active scene. Performs no safety check prior to running!
            save: saves the scene after setting the data. '''
        def dict_to_tag():
            out_str = ''
            out_str += 'Production: {0}\n'.format(self.production)
            out_str += 'Project: {0}\n'.format(self.project_name)
            out_str += 'Scene: {0}\n'.format(self.scene_name)
            out_str += 'Framerate: {0}\n'.format(self.framerate)
            out_str += 'Version: {0}'.format(self.version)
            return out_str
        #
        if (self.is_tagged()):
            self.scene_tag[c4d.ANNOTATIONTAG_TEXT] = dict_to_tag()
            return True
        else:
            return False

    def _set_rscene_framerate(self):
        ''' Sets the framerate in the project settings as well as the current RenderData'''
        doc = c4d.documents.GetActiveDocument()
        rd  = doc.GetActiveRenderData()
        doc.SetFps(self.framerate)
        rd[c4d.RDATA_FRAMERATE] = self.framerate
        c4d.EventAdd()
        return True

    def _set_rscene_output_paths(self):
        ''' Generate render output paths from metadata and sets them in the active scene. '''
        output_path = os.path.join(
            self.prod_data['project'],
            self.project_name,
            'render_3d',
            self.scene_name,
            'v{0}'.format(str(self.version).zfill(3)),
            '$take',
            '{0}_{1}'.format(self.scene_name, '$take')
            )
        multi_path = os.path.join(
            self.prod_data['project'],
            self.project_name,
            'render_3d',
            self.scene_name,
            'v{0}'.format(str(self.version).zfill(3)),
            '$take_passes',
            '{0}_{1}'.format(self.scene_name, '$take')
            )
        core.setOutputPaths(output_path, multi_path)
        return True

    def _set_rscene_renderdata(self, preset):
        ''' Set the RenderData in the active scene to the passed production preset
            preset (str): the name of a production render preset '''
        doc        = c4d.documents.GetActiveDocument()
        preset_loc = PRESETS_PATH.format(self.production, preset)
        preset_doc = c4d.documents.LoadDocument(preset_loc, c4d.SCENEFILTER_0)
        new_rd     = preset_doc.GetFirstRenderData()

        core.createRenderData(new_rd, preset)
        doc.SetActiveRenderData(new_rd)
        return True

    # Private constructors & deconstructors
    def _bld_project_dir(self):
        ''' Make a complete project directory tree for a new project. (Includes all project folders, not just C4D.)'''
        def mk_dir(path_):
            if not os.path.exists(path_):
                try: 
                    os.mkdir(path_)
                except WindowsError: 
                    debug.FileError(3)

        folder_struct = self.prod_data['folders']
        main_folder   = os.path.join(self.prod_data['project'], self.project_name)

        mk_dir(main_folder)    
        for main, sub in folder_struct.iteritems():
            mk_dir(os.path.join(main_folder, main))
            for s in sub: 
                mk_dir(os.path.join(main_folder, main, s))
        return True

    def _bld_rscene_hook(self):
        ''' Build new hooks in the active scene. Cleanup of existing hooks handled separately (see constructor method documentation.)'''
        doc = c4d.documents.GetActiveDocument()
        doc.StartUndo()

        # create null
        scene_ctrl = c4d.BaseObject(c4d.Onull)
        doc.InsertObject(scene_ctrl)
        doc.AddUndo(c4d.UNDOTYPE_NEW, scene_ctrl)
        scene_ctrl.SetName('__SCENE__')
        # create and populate tag
        scene_tag  = core.tag(scene_ctrl, typ=c4d.Tannotation, name='SCENE_DATA')[0]

        doc.AddUndo(c4d.UNDOTYPE_NEW, scene_tag)
        c4d.EventAdd()
        doc.EndUndo()

        self.scene_ctrl = scene_ctrl
        self.scene_tag = scene_tag
        return True

    def _clr_rscene_hook(self, force=False):
        ''' Clear all hooks from the active scene. 
            force: forces the removal of existing hooks (if any) '''
        no_cleanup = self._get_rscene_hook()[0]
        if (no_cleanup) and (force):
            self.scene_ctrl.Remove()
        elif len(self.cleanup):
            for obj in self.cleanup:
                obj.Remove()
        return True

def clearAllMultipasses():
    ''' Clear all multipass objects from the current RenderData '''
    doc = c4d.documents.GetActiveDocument()
    rdata = doc.GetActiveRenderData()
    doc.StartUndo()
    for mpass in core.ObjectIterator(rdata.GetFirstMultipass()):
        mpass.Remove()
    c4d.EventAdd()
    doc.EndUndo()
    return True

def clearObjectBuffers():
    ''' Clear all object buffers from the current RenderData '''
    doc = c4d.documents.GetActiveDocument()
    rdata = doc.GetActiveRenderData()
    doc.StartUndo()
    for mpass in core.ObjectIterator(rdata.GetFirstMultipass()):
        if (mpass.GetTypeName() == 'Object Buffer'):
            doc.AddUndo(c4d.UNDOTYPE_DELETE, mpass)
            mpass.Remove()
    c4d.EventAdd()
    doc.EndUndo()
    return True

def enableObjectBuffer(obid):
    ''' Insert an object buffer into the active render data, with the passed id'''
    doc = c4d.documents.GetActiveDocument()
    rd = doc.GetActiveRenderData()
    ob = c4d.BaseList2D(c4d.Zmultipass)
    ob.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = c4d.VPBUFFER_OBJECTBUFFER
    ob[c4d.MULTIPASSOBJECT_OBJECTBUFFER] = obid
    rd.InsertMultipass(ob)
    c4d.EventAdd()

def createObjectBuffers(consider_takes=False):
    ''' Parse the scene for all compositing tags with object buffers enabled, then creates them.'''    
    doc = c4d.documents.GetActiveDocument()
    td = doc.GetTakeData()
    # clear all existing object buffers
    clearObjectBuffers()
    # "simple" mode -- takes are not considered, existing render data is modified
    if not (consider_takes):
        _buildObjectBuffers()
    # "complicated" mode -- creates child RenderData for each take, enabling only object buffers
    # belonging to visible objects in the take
    elif (consider_takes):
        # Operates only on "checked" takes -- those flagged in the scene
        take_list = core.getCheckedTakes()
        # if no takes are checked, escape
        if len(take_list) == 0:
            return
        # Get the active render data -- this will be the primary RenderData from which the chilrden
        # will inherit
        parent_rdata = doc.GetActiveRenderData()
        if parent_rdata.GetUp():
            raise debug.PipelineError(4)
            return
        # Create a child renderdata for each take
        for take in take_list:
            # Change the take -- this will affect all the necessary visibility flags
            td.SetCurrentTake(take)
            # Create the child data
            child_rdata = core.createChildRenderData(parent_rdata, suffix=take.GetName(), set_active=True)
            # Set up Object Buffers for the objects visible in the current take
            _buildObjectBuffers()
            # Assign the RenderData to the take
            take.SetRenderData(td, child_rdata)
            c4d.EventAdd()

def createUtilityPass(take=None):
    ''' Create a utility pass version of the passed take. If no take is passed, it will create one
        for the main take.'''
    doc = c4d.documents.GetActiveDocument()
    td  = doc.GetTakeData()
    parent_rdata = doc.GetActiveRenderData()
    # use the main take if none is passed
    if (take == None):
        take = td.GetMainTake()

    # make the take active and create a child render data to attach to it
    new_take = core.take('{}_util'.format(take.GetName()), set_active=True)
    child_rdata = core.createChildRenderData(parent_rdata, suffix='UTIL', set_active=True)
    new_take.SetRenderData(td, child_rdata)
    self.clearAllMultipasses()

    # modify renderdata for 32-bit exr w/ data passes
    render_data = database.getProduction('DEFAULT')

    for multipass_id in render_data['passes_util']:
        mp_obj = c4d.BaseList2D(c4d.Zmultipass)
        mp_obj.GetDataInstance()[c4d.MULTIPASSOBJECT_TYPE] = eval(multipass_id)
        child_rdata.InsertMultipass(mp_obj)
    for attribute in render_data['image_settings_util']:
        child_rdata[eval(attribute)] = render_data['image_settings_util'][attribute]

    return (take, child_rdata)

def _getObjectBufferIDs():
    ''' Private. Get a set of all unique Object Buffer ids set in compositing tags in the scene. '''
    ids = []
    channel_enable = 'c4d.COMPOSITINGTAG_ENABLECHN{}'
    channel_id     = 'c4d.COMPOSITINGTAG_IDCHN{}'
    doc = c4d.documents.GetActiveDocument()
    td = doc.GetTakeData()

    for obj in core.ObjectIterator(doc.GetFirstObject()):
        if core.isVisible(obj):
            for tag in core.TagIterator(obj):
                if tag.GetType() == c4d.Tcompositing:
                    for i in range(12):
                        if tag[eval(channel_enable.format(i))] == 1:
                            id_ = tag[eval(channel_id.format(i))]
                            ids.append(id_)
    return sorted(list(set(ids)), reverse=True)

def _buildObjectBuffers():
    ''' Private. '''
    # Get the object buffer IDs assigned to compositing tags in the scene
    # this operation also checks for objects that are invisible (dots) or flagged as matted  |
    # invisible to camera, and ignores them.
    ids = _getObjectBufferIDs()
    for id_ in ids:
        # enable the passed object buffers 
        enableObjectBuffer(id_)

