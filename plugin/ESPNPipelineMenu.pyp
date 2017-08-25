# coding: UTF-8

""" ESPNPipelineMenu.pyp: A Python plugin for Cinema 4D housing various pipeline utilities. """

# internal libraries
import c4d
import os
from c4d import gui, bitmaps, plugins
# custom libraries
from espntools import core 
from espntools import scene
from espntools import debug
from espntools import database
from espntools import submit
from espntools import automation

from espntools import __version__, __date__

reload(core)
reload(scene)
reload(debug)
reload(database)
reload(submit)
reload(automation)

debug.info(
    "Loaded ESPN frontend plug-in for C4D", 
    "Version {0} : {1}".format(__version__, __date__)
    )

PLUGIN_ID = 1037160
BUTTON_ID = 1037183

ID_STATIC            = 99999
ESPNPipelineMenu     = 10000
ESPNHelpMenu         = 99998
CLOSE                = 99997
MAIN_DIALOG          = 10001

FIRST_TAB            = 10002
LBL_PROD_NAME        = 10004
DRP_PROD_NAME        = 10005
LBL_PROJ_NAME        = 10006
CHK_EXISTING         = 10007
DRP_PROJ_NAME        = 10008
TXT_PROJ_NAME        = 10009
LBL_SCENE_NAME       = 10010
TXT_SCENE_NAME       = 10011
LBL_FRAMERATE        = 10012
RDO_FRAMERATE        = 10013
RDO_FRAMERATE_24     = 10024
RDO_FRAMERATE_30     = 10030
RDO_FRAMERATE_60     = 10060
FIRST_TAB_SEP_01     = 10017
LBL_PREVIEW          = 10018
LBL_PREVIEW_NULL     = 10118
LBL_PREVIEW_PROJ     = 10019
TXT_PREVIEW_PROJ     = 10020
LBL_PREVIEW_FILE     = 10021
TXT_PREVIEW_FILE     = 10022
BTN_NEWPROJ_EXEC     = 10023
BTN_HELP_EXEC        = 10024
HELP_IMAGE           = 10029

SECOND_TAB           = 20000
BTN_SETOUTPUT        = 20001
BTN_PNG_OUTPUT       = 20002
BTN_EXR_OUTPUT       = 20003
BTN_NEWTAKE          = 20004
BTN_VERSIONUP        = 20005
BTN_SUBMIT           = 20006
LBL_OUTPUT_PATHS     = 20007
LBL_TAKE_UTILS       = 20008
BTN_CREATE_OBJBUFFERS= 20009
DRP_PRES_NAME        = 20010
BTN_SET_PRESET       = 20011
LBL_PRESET_BOX       = 20012

THIRD_TAB            = 30000
LBL_HOME_TRICODE     = 30001
TXT_HOME_TRICODE     = 30002
VEC_HOME_COLOR_P     = 30003
VEC_HOME_COLOR_S     = 30004
VEC_HOME_COLOR_T     = 30005
LBL_AWAY_TRICODE     = 30006
TXT_AWAY_TRICODE     = 30007
VEC_AWAY_COLOR_P     = 30008
VEC_AWAY_COLOR_S     = 30009
VEC_AWAY_COLOR_T     = 30010
THIRD_TAB_INSTRUCTION= 30011
IS_MATCHUP           = 30012
TEAM_SWITCH_EXEC     = 30013
HOME_PRIMARY_EXEC    = 30014
HOME_SECONDARY_EXEC  = 30015
HOME_TERTIARY_EXEC   = 30016
AWAY_PRIMARY_EXEC    = 30017
AWAY_SECONDARY_EXEC  = 30018
AWAY_TERTIARY_EXEC   = 30019
AUTOMATION_HELP_EXEC = 30020

SAVE_RENAME_TAB      = 40000
SAVE_BACKUP_EXEC     = 40001
RENAME_EXEC          = 40002
SAVE_RENAME_HELP_EXEC= 40003
RELINK_TEXTURES_EXEC = 40004

DRP_PRES_NAME_START_ID=70000
DRP_PROJ_NAME_START_ID=80000
DRP_PROD_NAME_START_ID=90000

class ESPNMenu(gui.GeDialog):
    def __init__(self):
        pass

    ### GeDialog Overrides ###################################################
    def CreateLayout(self):
        # attach MetaScene and BaseDocument
        self.live_scene = scene.MetaScene()
        # initialize UI
        self.LoadDialogResource(ESPNPipelineMenu)
        self.setEmptyDropdowns(
            prod=True, 
            proj=True, 
            pres=True
            )

        self.setDefaultState()
        self.pullProductionList()
        self.setLiveDocument()
        self.SetTimer(500)
        return True

    def Timer(self, msg):
        if not (self.live_doc.IsAlive()):
            self.setLiveDocument()
        elif not (c4d.documents.GetActiveDocument() == self.live_doc):
            self.setLiveDocument()
        else: pass

    def Command(self, id, msg):
        # "Use existing project" checkbox
        if (id == CHK_EXISTING):
            self.toggleProjectSelected()
        # "Production" dropdown
        elif (id == DRP_PROD_NAME):
            self.onChangedProduction()
            #self.refresh_preview()
        # Text fields or "project" dropdown
        elif (id == TXT_PROJ_NAME or
              id == TXT_SCENE_NAME):
            self.setPreviewText()
        elif (id == DRP_PROJ_NAME):
            self.onChangedProject()
        # Render presets dropdown
        elif (id == DRP_PRES_NAME):
            self.onChangedPreset()
        elif (id == BTN_SET_PRESET):
            self.buildPresetRenderData()
        # "Create new" button
        elif (id == BTN_NEWPROJ_EXEC):
            print self.buildNewScene()
        elif (id == BTN_HELP_EXEC):
            self.help('tab1')
        # tab 2 buttons
        elif (id == BTN_SETOUTPUT):
            self.pushOutputPaths()
        elif (id == BTN_SUBMIT):
            self.submitToFarm()
        elif (id == BTN_NEWTAKE):
            self.buildTake()
        elif (id == BTN_PNG_OUTPUT):
            self.pushPngOutput()
        elif (id == BTN_EXR_OUTPUT):
            self.pushExrOutput()
        # tab 3
        elif (id == IS_MATCHUP):
            self.toggleMatchup()
        elif (id == TXT_HOME_TRICODE or
              id == TXT_AWAY_TRICODE):
            self.populateSwatches()
        elif (id == HOME_PRIMARY_EXEC):
            self.buildTeamColorMaterial('home', 'primary')
        elif (id == HOME_SECONDARY_EXEC):
            self.buildTeamColorMaterial('home', 'secondary')
        elif (id == HOME_TERTIARY_EXEC):
            self.buildTeamColorMaterial('home', 'tertiary')
        elif (id == AWAY_PRIMARY_EXEC):
            self.buildTeamColorMaterial('away', 'primary')
        elif (id == AWAY_SECONDARY_EXEC):
            self.buildTeamColorMaterial('away', 'secondary')
        elif (id == AWAY_TERTIARY_EXEC):
            self.buildTeamColorMaterial('away', 'tertiary')
        elif (id == TEAM_SWITCH_EXEC):
            self.pushTeamColors()
        elif (id == AUTOMATION_HELP_EXEC):
            self.help('tab3')
        elif (id == SAVE_BACKUP_EXEC):
            self.save()
        elif (id == RENAME_EXEC):
            self.rename()
        elif (id == BTN_VERSIONUP):
            self.versionUp()
        elif (id == SAVE_RENAME_HELP_EXEC):
            self.help('save_rename')
        elif (id == RELINK_TEXTURES_EXEC):
            auto.relinkTextures(migrate=True)
        elif (id == BTN_CREATE_OBJBUFFERS):
            self.createObjectBuffers()
        return True

    ### INTERFACE SCRIPTING FUNCTIONS ########################################
    ### UI Setters ###########################################################
    def setDefaultState(self):
        self.Enable(TXT_PREVIEW_PROJ, False)
        self.Enable(TXT_PREVIEW_FILE, False)

        self.toggleProductionSelected(False)
        self.toggleProjectSelected()
        self.setFramerate(30)

        self.populateProductions()
        return True

    def setProduction(self, idx):
        if not (idx == DRP_PROD_NAME_START_ID):
            self.SetInt32(DRP_PROD_NAME, idx)
            self.onChangedProduction()
            return True
        else: return False

    def setProject(self, idx):
        if not (idx == DRP_PROJ_NAME_START_ID):
            self.SetInt32(DRP_PROJ_NAME, idx)
            self.onChangedProject()
            return True
        else: return False

    def setScene(self, scene_name):
        if not (scene_name == ''):
            self.SetString(TXT_SCENE_NAME, scene_name)
            self.onChangedTextField()
            return True
        else: return False

    def setFramerate(self, frate):
        if not (frate == 24) and not (frate == 30) and not (frate == 60):
            return False
        self.SetInt32(RDO_FRAMERATE, 10000+frate)
        return True

    def setPreset(self, idx):
        if not (idx == DRP_PRES_NAME_START_ID):
            self.SetInt32(DRP_PRES_NAME, idx)
            self.onChangedPreset()
            return True
        else: return False

    def setEmpty(self, field):
        self.SetString(field, '')
        return True

    def setPreviewText(self):
        if self.GetBool(CHK_EXISTING):
            proj_name = self.projects[self.proj_id]
        else:
            proj_name = self.GetString(TXT_PROJ_NAME)
        scene_name    = self.GetString(TXT_SCENE_NAME)

        # Don't allow spaces as the user types
        proj_name     =  proj_name.replace(' ', '_') 
        scene_name    = scene_name.replace(' ', '_')

        prod_name     = self.productions[self.prod_id]
        #prod_folder   = database.getProduction(prod_name)['folder_lookup']['c4d_project'].format(proj_name)
        prod_folder   = self.live_scene.prod_data['folder_lookup']['c4d_project'].format(proj_name)
        # Generate preview paths
        scene_prev = '{0}_{1}.c4d'.format(proj_name, scene_name)
        proj_prev  = os.path.relpath(
            prod_folder,
            self.live_scene.prod_data['folder_lookup']['animroot']#"Y:\\Workspace\\MASTER_PROJECTS\\"
            )

        self.SetString(TXT_PROJ_NAME, proj_name)
        self.SetString(TXT_SCENE_NAME, scene_name)
        self.SetString(TXT_PREVIEW_PROJ, proj_prev)
        self.SetString(TXT_PREVIEW_FILE, scene_prev)
        return True

    def setEmptyDropdowns(self, prod=False, proj=False, pres=False):
        if (prod):
            self.FreeChildren(DRP_PROD_NAME)
            self.prod_selected = False
            self.productions   = {}
            self.prod_id       = DRP_PROD_NAME_START_ID
        if (proj):
            self.FreeChildren(DRP_PROJ_NAME)
            self.proj_existing = False
            self.projects      = {}
            self.proj_id       = DRP_PROJ_NAME_START_ID
        if (pres):
            self.FreeChildren(DRP_PRES_NAME)
            self.pres_selected = False
            self.presets       = {}
            self.pres_id       = DRP_PRES_NAME_START_ID
        return True

    def setLiveDocument(self):
        self.populateFromScene()
        self.live_doc = c4d.documents.GetActiveDocument()

    ### UI Getters ###########################################################
    def getInvalidFields(self):
        prd = self.getProduction()
        prj = self.getProject()
        scn = self.getScene()
        fra = self.getFramerate()
        # validate Production entries
        if (self.prod_id == DRP_PROD_NAME_START_ID):
            return 0
        elif (prd.lstrip() == '') or (prd == None):
            return 0
        # validate Project entries
        exists = self.GetBool(CHK_EXISTING)
        if (exists) and (self.proj_id == DRP_PROJ_NAME_START_ID):
            return 1
        elif (not exists) and ((prj.lstrip() == '') or (prj == None)):
            return 1
        # validate Scene entries
        if (not scn) or (scn == ''):
            return 2
        # validate Framerate selection
        if (not fra) or (fra == RDO_FRAMERATE):
            return 3
        return None

    def getProduction(self):
        self.prod_id = self.GetInt32(DRP_PROD_NAME)
        return self.productions[self.prod_id]

    def getProject(self):
        if (self.GetBool(CHK_EXISTING)):
            self.proj_id = self.GetInt32(DRP_PROJ_NAME)
            return self.projects[self.proj_id]
        else:
            return self.GetString(TXT_PROJ_NAME)

    def getScene(self):
        self.scene = self.GetString(TXT_SCENE_NAME)
        return self.scene

    def getPreset(self):
        self.pres_id = self.GetInt32(DRP_PRES_NAME)
        return self.presets[self.pres_id]

    def getFramerate(self):
        return (self.GetInt32(RDO_FRAMERATE)-10000)

    ### UI Togglers ##########################################################
    def toggleProductionSelected(self, flag):
        ''' Since the UI defaults to not having a production selected, most
        fields are disabled. When a production *is* selected, this method
        enables the dependent fields.'''
        self.Enable(CHK_EXISTING, flag)
        #self.Enable(DRP_PROJ_NAME, flag)
        self.Enable(TXT_PROJ_NAME, flag)
        self.Enable(TXT_SCENE_NAME, flag)
        self.Enable(RDO_FRAMERATE, flag)
        self.prod_selected = flag
        return True

    def toggleProjectSelected(self, flag=None):
        if (flag == None):
            flag = self.GetBool(CHK_EXISTING)
        else:
            self.SetBool(CHK_EXISTING, flag)
        self.Enable(TXT_PROJ_NAME, 1-flag)
        self.Enable(DRP_PROJ_NAME, flag)
        return True

    def toggleMatchup(self, flag=None):
        if (flag == None):
            flag = self.GetBool(IS_MATCHUP)
        if (flag):
            self.Enable(TXT_AWAY_TRICODE, True)
            self.Enable(VEC_AWAY_COLOR_P, True)
            self.Enable(VEC_AWAY_COLOR_S, True)
            self.Enable(VEC_AWAY_COLOR_T, True)
        else:
            self.Enable(TXT_AWAY_TRICODE, False)
            self.Enable(VEC_AWAY_COLOR_P, False)
            self.Enable(VEC_AWAY_COLOR_S, False)
            self.Enable(VEC_AWAY_COLOR_T, False)
        self.matchup_selected = flag
        return True

    ### UI Refreshers ########################################################
    def onChangedProduction(self):
        if not (self.getProduction() == DRP_PROD_NAME_START_ID):
            print self.getProduction()
            # clear dependent dropdowns / text fields
            self.toggleProjectSelected(flag=False)
            self.setEmptyDropdowns(proj=True, pres=True)
            self.setEmpty(TXT_PROJ_NAME)
            # update metascene
            self.live_scene.production = self.getProduction()
            self.live_scene.prod_data = database.getProduction(self.live_scene.production)
            # repopulate depdendent fields
            self.populateProjects()
            self.populatePresets()
            self.setPreviewText()
            # enable dependent fields
            self.toggleProductionSelected(True)
        else:
            self.toggleProductionSelected(False)
        return True

    def onChangedProject(self):
        self.getProject()
        self.setPreviewText()
        return True

    def onChangedPreset(self):
        self.getPreset()
        return True

    def onChangedTextField(self):
        self.setPreviewText()
        return True

    ### UI Populators ########################################################
    def populateFromScene(self):
        self.live_scene = scene.MetaScene()
        self.prod_id    = DRP_PROD_NAME_START_ID
        self.proj_id    = DRP_PROJ_NAME_START_ID
        self.populateProductions()
        # Exit out if the scene isn't tagged
        if not (self.live_scene.is_tagged()):
            self.setDefaultState()
            return False
        # Get the index of the production
        for k,v in self.productions.iteritems():
            if (v == self.live_scene.production):
                self.prod_id = k
                self.setProduction(self.prod_id)
        try:
            # Get the index of the project
            self.populateProjects()
            for k,v in self.projects.iteritems():
                if (v == self.live_scene.project_name):
                    self.proj_id = k
                    self.setProject(self.proj_id)
                    self.toggleProjectSelected(flag=True)
        except KeyError: pass
        self.setScene(self.live_scene.scene_name)
        self.setFramerate(self.live_scene.framerate)
        return True
    
    def populateProductions(self):
        self.setEmptyDropdowns(prod=True)
        self.pullProductionList()
        # populate production dropdown
        for idx in self.productions:
            self.AddChild(DRP_PROD_NAME, idx, self.productions[idx])
        self.setProduction(DRP_PROD_NAME_START_ID)
        return True

    def populateProjects(self):
        self.setEmptyDropdowns(proj=True)
        self.pullProjectList()
        # populate project dropdown
        for idx in self.projects:
            self.AddChild(DRP_PROJ_NAME, idx, self.projects[idx])
        self.setProject(DRP_PROJ_NAME_START_ID)
        return True

    def populatePresets(self):
        self.setEmptyDropdowns(pres=True)
        self.pullRenderPresets()
        for idx in self.presets:
            self.AddChild(DRP_PRES_NAME, idx, self.presets[idx])
        self.setPreset(DRP_PRES_NAME_START_ID)
        return True

    def populateSwatches(self):
        home_tricode = self.GetString(TXT_HOME_TRICODE)
        away_tricode = self.GetString(TXT_AWAY_TRICODE)
        try:
            home_colors = database.getTeamColors(self.getProduction(), home_tricode, squelch=True)
        except:
            home_colors = None
        try:
            away_colors = database.getTeamColors(self.getProduction(), away_tricode, squelch=True)
        except:
            away_colors = None

        if (home_colors):
            self.SetColorField(VEC_HOME_COLOR_P, home_colors['primary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_S, home_colors['secondary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_T, home_colors['tertiary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        else:
            self.SetColorField(VEC_HOME_COLOR_P, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_S, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_HOME_COLOR_T, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)

        if (away_colors):
            self.SetColorField(VEC_AWAY_COLOR_P, away_colors['primary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_S, away_colors['secondary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_T, away_colors['tertiary'], 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        else:
            self.SetColorField(VEC_AWAY_COLOR_P, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_S, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
            self.SetColorField(VEC_AWAY_COLOR_T, c4d.Vector(0,0,0), 1.0, 1.0, c4d.DR_COLORFIELD_NO_BRIGHTNESS)
        return True

    def pullProductionList(self):
        # generate a dictionary with gui ID as key and name as value
        self.setEmptyDropdowns(prod=True)
        idx = DRP_PROD_NAME_START_ID
        self.productions[idx] = ''
        for prod in database.getAllProductions():
            idx += 1
            self.productions[idx] = prod
        return True

    def pullProjectList(self):
        # generate a dictionary with gui ID as key and name as value
        idx = DRP_PROJ_NAME_START_ID
        for proj in database.getAllProjects(self.productions[self.prod_id]):
            idx += 1
            self.projects[idx] = proj
            #print "retrieve_projects(): {}".format(id_)
        return True

    def pullRenderPresets(self):
        # generate a dictionary with gui ID as key and name as value
        idx = DRP_PRES_NAME_START_ID
        for pres in database.getAllPresets(self.productions[self.prod_id]):
            idx +=1 
            self.presets[idx] = pres
        return True

    ### OPERATIONS ###########################################################
    ### Builders (of C4D objects) ############################################
    def buildNewScene(self):
        invalid_field = self.getInvalidFields()
        if not (invalid_field == None):
            raise debug.UIError(invalid_field)

        # cancel if any required fields are empty
        self.live_scene = scene.MetaScene.from_data(       
            {'production'  : self.getProduction(),
             'project_name': self.getProject(),
             'scene_name'  : self.getScene(),
             'framerate'   : self.getFramerate(),
             'version'     : 1},
            set_output = True,
            set_frate  = True,
            set_rdata  = False,
            save       = True
        )
        return True

    def buildPresetRenderData(self):
        try:
            self.live_scene._set_rscene_renderdata(self.getPreset())
            self.live_scene._set_rscene_output_paths()
        except AttributeError:
            raise debug.PipelineError(1)
        return True

    def buildTake(self):
        name = gui.RenameDialog('')
        if not (name == ''):
            core.take(name, set_active=False)
        else: pass
        return True

    def buildTeamColorMaterial(self, location, swatch):
        location = location.upper()
        swatch   = swatch.upper()
        name     = '{0}_{1}'.format(location, swatch)
        core.createMaterial(name)
        return True

    ### Pushers (modify C4D objects) #########################################
    def pushOutputPaths(self):
        self.live_scene._set_rscene_output_paths()
        return True

    def pushPngOutput(self):
        core.setOutputFiletype('png', 16)

    def pushExrOutput(self):
        core.setOutputFiletype('exr')

    def pushTeamColors(self):
        values = {}
        values['home_primary'] = self.GetColorField(VEC_HOME_COLOR_P)
        values['home_secondary'] = self.GetColorField(VEC_HOME_COLOR_S)
        values['home_tertiary'] = self.GetColorField(VEC_HOME_COLOR_T)
        if (self.GetBool(IS_MATCHUP)):
            values['away_primary'] = self.GetColorField(VEC_AWAY_COLOR_P)
            values['away_secondary'] = self.GetColorField(VEC_AWAY_COLOR_S)
            values['away_tertiary'] = self.GetColorField(VEC_AWAY_COLOR_T)
        for k,v in values.iteritems():
            core.changeColor(k.upper(), v['color'], exact=False)
        return True

    ### Executors (external scripts / operations) ############################
    def submitToFarm(self):
        dlg = submit.SubmissionDialog()
        dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=300, defaulth=50)
        return True

    def save(self):
        self.live_scene.save()
        return True

    def rename(self):
        self.live_scene.rename()
        return True

    def versionUp(self):
        self.live_scene.version_up()
        return True

    def createObjectBuffers(self):
        if len(core.getCheckedTakes()):
            scene.createObjectBuffers(consider_takes=True)
        else:
            scene.createObjectBuffers(consider_takes=False)
        return True

    def help(self, tab):
        help_diag = ESPNHelp(panel=tab)
        help_diag.Open(dlgtype=c4d.DLG_TYPE_MODAL, xpos=-1, ypos=-1)
        return True


class ESPNHelp(gui.GeDialog):
    def __init__(self, panel):
        self.panel = panel

    def CreateLayout(self):
        self.LoadDialogResource(ESPNHelpMenu)
        try: 
            gui.GetIcon(BUTTON_ID)["bmp"].FlushAll()
            gui.UnregisterIcon(BUTTON_ID)
        except: pass
        dir, file = os.path.split(__file__)
        if (self.panel=='tab1'):
            fn = os.path.join(dir, "res", "icons", "tab1_help.tif")
        elif (self.panel=='tab3'):
            fn = os.path.join(dir, "res", "icons", "tab3_help.tif")
        elif (self.panel=='save_rename'):
            fn = os.path.join(dir, "res", "icons", "save_rename_help.tif")
        bmp = bitmaps.BaseBitmap()
        bmp.InitWith(fn)
        gui.RegisterIcon(BUTTON_ID, bmp)
        return True

class ESPNPipelinePlugin(plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ESPNMenu()

        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=300, defaulth=50)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ESPNMenu()

        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

if __name__ == "__main__":
    bmp = bitmaps.BaseBitmap()

    dir, file = os.path.split(__file__)
    fn = os.path.join(dir, "res", "icons", "icon.png")
    bmp.InitWith(fn)

    #desc = plugins.GeLoadString(ESPNPipelineMenu)

    plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                  str="ESPN Pipeline",
                                  info=0,
                                  help="Main menu for ESPN pipeline operations",
                                  dat=ESPNPipelinePlugin(),
                                  icon=bmp)