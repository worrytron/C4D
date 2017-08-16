"""
Submit Scene to Qube

Copyright: 2017 ESPN Productions
Compatible with Cinema4D R14, R15, R17
Author: Mark Rohrer (mark.rohrer@espn.com)

Name-US: Submit Scene to Qube
Description-US: Submit this scene file to Qube
"""

import c4d
import subprocess
import time
import datetime
from random import uniform
from c4d import gui

from espntools import core

# Default submission settings
default_priority = 5000
instances = 10
max_cpus = 50

# Localization variables for each ESPN render farm
mapped_drives = ['Y:', 'W:']
local_drives = ['C:', 'V:']
nas_unc = '\\\\cagenas'

# Unique id numbers for each of the GUI elements - DO NOT CHANGE
LBL_JOB_NAME =      1000
LBL_SCENE_FILE =    1001
LBL_RENDER_PATH =   1002
LBL_FRAME_RANGE =   1003
LBL_NUM_THREADS =   1004
LBL_PRIORITY =      1005
LBL_CLUSTER =       1006
LBL_RESTRICTIONS =  1007
LBL_ALL_THREADS =   1008
LBL_MULTI_PATH =    1009

GROUP_MAIN =        9999

TXT_JOB_NAME =      10001
TXT_SCENE_FILE =    10002
TXT_RENDER_PATH =   10003
TXT_MULTI_PATH =    10004
TXT_FRAME_RANGE =   10005

GROUP_NUM_THREADS = 10006 
TXT_NUM_THREADS =   10007
BOOL_ALL_THREADS =  10008

TXT_PRIORITY =      10009
TXT_CLUSTER =       10010

GROUP_RESTRICTIONS= 10011
TXT_RESTRICTIONS =  10012
BOOL_RESTRICTIONS = 10013

GROUP_BUTTONS =     20000
BTN_SUBMIT =        20001
BTN_CANCEL =        20002

# Submission dialog window
class SubmissionDialog(gui.GeDialog):
  def CreateLayout(self):
    self.submit_dict = self.gather(init=True)

    self.SetTitle('Submit Scene to Qube')

    self.GroupBegin(GROUP_MAIN, c4d.BFH_LEFT, 2, 1)

    # Job name field
    self.AddStaticText(LBL_JOB_NAME, c4d.BFH_LEFT, name='Job Name') 
    self.AddEditText(TXT_JOB_NAME, c4d.BFH_LEFT, 600)
    self.SetString(TXT_JOB_NAME, self.submit_dict['name'])
    
    # Job scene path field
    self.AddStaticText(LBL_SCENE_FILE, c4d.BFH_LEFT, name='Scene File') 
    self.AddEditText(TXT_SCENE_FILE, c4d.BFH_LEFT, 600)
    self.SetString(TXT_SCENE_FILE, self.submit_dict['package']['-render'])
    
    # Job render path field
    self.AddStaticText(LBL_RENDER_PATH, c4d.BFH_LEFT, name='Render Path') 
    self.AddEditText(TXT_RENDER_PATH, c4d.BFH_LEFT, 600)
    self.SetString(TXT_RENDER_PATH, self.submit_dict['package']['-oimage'])
    self.Enable(TXT_RENDER_PATH, self.save_main_bool)

    # Job render multi path field
    self.AddStaticText(LBL_MULTI_PATH, c4d.BFH_LEFT, name='Multipass Path') 
    self.AddEditText(TXT_MULTI_PATH, c4d.BFH_LEFT, 600)
    self.SetString(TXT_MULTI_PATH, self.submit_dict['package']['-omultipass'])
    self.Enable(TXT_MULTI_PATH, self.save_multi_bool)

    # Frame range field
    self.AddStaticText(LBL_FRAME_RANGE, c4d.BFH_LEFT, name='Frame Range') 
    self.AddEditText(TXT_FRAME_RANGE, c4d.BFH_LEFT, 100)
    self.SetString(TXT_FRAME_RANGE, self.submit_dict['package']['range'])

    # Num Threads field
    self.AddStaticText(LBL_NUM_THREADS, c4d.BFH_LEFT, name='Num. Threads') 

    self.GroupBegin(GROUP_NUM_THREADS, c4d.BFH_LEFT, 2, 1)
    self.AddEditText(TXT_NUM_THREADS, c4d.BFH_LEFT, 60)
    self.SetString(TXT_NUM_THREADS, '16')
    self.AddCheckbox(BOOL_ALL_THREADS, c4d.BFH_RIGHT, 0, 0, name='All')
    
    self.Enable(TXT_NUM_THREADS, 0)
    self.SetBool(BOOL_ALL_THREADS, 1)

    self.GroupEnd()

    # Priority field
    self.AddStaticText(LBL_PRIORITY, c4d.BFH_LEFT, name='Priority') 
    self.AddEditText(TXT_PRIORITY, c4d.BFH_LEFT, 100)
    self.SetString(TXT_PRIORITY, default_priority)

    # Cluster field
    self.AddStaticText(LBL_CLUSTER, c4d.BFH_LEFT, name='Cluster') 
    
    self.GroupBegin(GROUP_RESTRICTIONS, c4d.BFH_LEFT, 2, 1)
    self.AddEditText(TXT_CLUSTER, c4d.BFH_LEFT, 60)
    self.AddCheckbox(BOOL_RESTRICTIONS, c4d.BFH_LEFT, 0, 0, 'Restrict')
    self.GroupEnd()

    self.SetString(TXT_CLUSTER, '/')

    # Restrictions field
    self.AddStaticText(LBL_RESTRICTIONS, c4d.BFH_LEFT, name='Restrictions') 
    self.AddEditText(TXT_RESTRICTIONS, c4d.BFH_LEFT, 100)
    self.SetString(TXT_RESTRICTIONS, '')
    
    self.Enable(TXT_RESTRICTIONS, 0)
    self.SetBool(BOOL_RESTRICTIONS, 0)

    self.GroupEnd()

    # Buttons field
    self.GroupBegin(GROUP_BUTTONS, c4d.BFH_RIGHT, 2, 1)
    self.AddButton(BTN_SUBMIT, c4d.BFH_SCALE, name='Submit to Farm')
    self.AddButton(BTN_CANCEL, c4d.BFH_SCALE, name='Cancel')
    self.GroupEnd()
    
    self.ok = False
    
    return True

  # React to user's input:
  def Command(self, id, msg):
    # Enable/disable text field if 'all threads' is checked
    if id == BOOL_ALL_THREADS:
      i = self.GetBool(BOOL_ALL_THREADS)
      self.Enable(TXT_NUM_THREADS, (1-i))
    elif id == BOOL_RESTRICTIONS:
      i = self.GetBool(BOOL_RESTRICTIONS)
      self.Enable(TXT_RESTRICTIONS, i)
    # Close the window on CANCEL
    elif id==BTN_CANCEL:
      self.Close()
    # Submit the scene on OK
    elif id==BTN_SUBMIT:
      self.ok = True
      self.run()
      self.Close()
    return True

  def run(self):
    ''' New for R17: Iterate through checked takes to submit each individually. If no
        checked takes are found, it will submit the old-fashioned way.'''
    # Check for "Save Project File" .. aka the .aec contingency
    # Check for active takes in the scene
    takes = core.getCheckedTakes()
    # None found -- submit without specifying takes
    if len(takes) == 0:
      self.submit_dict = self.gather()
      self.submit()
    else:
      # Iterate over all checked takes and flag them in the submission string
      for take in takes:
        self.submit_dict = self.gather()
        self.submit_dict['package']['-take'] = take.GetName()
        self.submit_dict['name'] += ' - {}'.format(take.GetName())
        self.submit()

  def aecSanityCheck(self):
    doc = c4d.documents.GetActiveDocument()
    rd  = doc.GetActiveRenderData()

    if (rd[c4d.RDATA_PROJECTFILE]):
      chk = gui.QuestionDialog(
        "Your scene is set to export a comp to After Effects -- this feature will be disabled for the farm submission. Would you like to export it now instead?"
        )
      if (chk):
        c4d.CallButton( rd, c4d.RDATA_PROJECTFILESAVE )

      rd[c4d.RDATA_PROJECTFILE] = False
      return


  def gather(self, init=False, *a):
    # INITIALIZATION
    # This branch pulls in raw data from the scene.  The user will have the option
    # to modify it in the UI, which is parsed in the "not init" branch below.
      
    # RenderData container object
    doc = c4d.documents.GetActiveDocument()
    rd  = doc.GetActiveRenderData()

    # Get C4D version
    version = c4d.GetC4DVersion()/1000
    version_map = {
      17: "R:\\Program Files\\MAXON\\CINEMA 4D R17\\CINEMA 4D.exe",
      15: "R:\\Program Files\\MAXON\\CINEMA 4D R15\\CINEMA 4D 64 Bit.exe",
      14: "R:\\Program Files\\MAXON\\CINEMA 4D R14\\CINEMA 4D 64 Bit.exe"
    }

    if (init):
      # Scene name / location
      scene_name = doc.GetDocumentName()
      scene_path = doc.GetDocumentPath() + '\\' + scene_name

      # Getting frame range in cinema is a PITA
      fps = rd[c4d.RDATA_FRAMERATE]
      step = rd[c4d.RDATA_FRAMESTEP]
      start = rd[c4d.RDATA_FRAMEFROM]
      end = rd[c4d.RDATA_FRAMETO]
      start_frame = start.Get() * fps
      end_frame = end.Get() * fps
      # Additional steps for frame step formatting
      frame_range = str(int(start_frame)) +"-"+ str(int(end_frame))
      if step > 1:
        frame_range += ("x" + str(step))

      # Is saving output files enabled?
      self.save_main_bool = rd[c4d.RDATA_SAVEIMAGE]
      self.save_multi_bool = rd[c4d.RDATA_MULTIPASS_SAVEIMAGE]

      # Get output paths.
      output_path = {True:rd[c4d.RDATA_PATH], False:""}[self.save_main_bool]
      output_multi_path = {True:rd[c4d.RDATA_MULTIPASS_FILENAME], False:""}[self.save_multi_bool]

      # Default placeholder values
      cluster = ""
      restrictions = ""
      priority = 0


    # POST-LAUNCH PARSING
    # This branch parses the UI for any overrides or changes the user has made.
    if not (init):
      # Scene data
      scene_name = self.GetString(TXT_JOB_NAME)
      scene_path = self.GetString(TXT_SCENE_FILE)
      output_path = self.GetString(TXT_RENDER_PATH)
      output_multi_path = self.GetString(TXT_MULTI_PATH)
      frame_range = self.GetString(TXT_FRAME_RANGE)
      # Farm data
      priority = self.GetString(TXT_PRIORITY)
      cluster = self.GetString(TXT_CLUSTER)
      restrictions = self.GetString(TXT_RESTRICTIONS)
      
    # Timestamp
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " " + str(int(uniform(100,300)))

    # FORMATTING / CLEANUP / DEPENDENT FLAGS
    # Pathing everything to \\cagenas from Y/W:
    for letter in mapped_drives:
      scene_path = scene_path.replace(letter, nas_unc)
      output_path = output_path.replace(letter, nas_unc)
      output_multi_path = output_multi_path.replace(letter, nas_unc)

    # Dealing with threads
    if self.GetBool(BOOL_ALL_THREADS):
      threads = 0
      reservations = 'host.processors=1+'
      requirements = 'host.processors.used==0'
      useAllCores = 1
      rtc = 1
    else:
      threads = self.GetString(TXT_NUM_THREADS)
      reservations = 'host.processors=' + str(threads)
      requirements = ''
      useAllCores = 0
      rtc = threads


    # SANITY CHECKS --
    # 1.  Is saving render output enabled?
    if not rd[c4d.RDATA_GLOBALSAVE]:
      chk = gui.QuestionDialog(
        "Saving is not enabled for rendering!  You'll need to turn that on in Render Settings."
        )
      self.Close()

    if not self.save_main_bool:
      chk = gui.QuestionDialog(
        "Saving is not enabled for your beauty render.  Do you want to proceed?"
        )
      if chk: pass
      else: self.Close()

    if not self.save_multi_bool:
      chk = gui.QuestionDialog(
        "Saving is not enabled for your multi-passes.  Do you want to proceed?"
        )
      if chk: pass
      else: self.Close()

    # 2.  Is the full path to the scene file too long to render?
    if len(scene_path) > 199:
      chk = gui.QuestionDialog(
        "The full path to your scene file...:\n" + str(scene_path) + "\n...Is too long.  You'll need to shorten it before you submit."
        )
      self.Close()

    # 3. Is the user attempting to submit a scene saved locally, or trying to output renders to a local drive?
    for d in local_drives:
      if d in scene_path or d in output_path or d in output_multi_path:
        chk = gui.QuestionDialog(
          "Your scene file or render output are set to a local drive.  You'll need to change this before you submit."
          )
        self.Close()

    # 4. Are there unsaved changes in the scene?
    unsaved_changes = c4d.documents.GetActiveDocument().GetChanged()
    if (unsaved_changes):
      chk = gui.QuestionDialog(
        "Your scene has unsaved changes. Proceed anyway?"
        )
      if (chk): pass
      else: self.Close()

    # The Qube submission dictionary
    submit_dict = {
         'name': scene_name,
         'prototype':'cmdrange',
         'package':{
                    'simpleCmdType': 'Cinema4d (Win)',
                    'c4dExe':        version_map[version],
                    'c4dVersion':    [version, '0', None],
                    '-render':       scene_path,
                    '-oimage':       output_path, 
                    '-omultipass':   output_multi_path,
                    'range':         frame_range,
                    'threads':       threads,
                    'useAllCores':   useAllCores,
                    'renderThreadCount': rtc
                    },
          'label':        timestamp,
          'cluster':      cluster,
          'restrictions': restrictions,
          'priority':     priority,
          'cpus':         instances,
          'max_cpus':     max_cpus,
          'reservations': reservations,
          'requirements': requirements,
          'flagsstring':  'auto_wrangling,disable_windows_job_object'
        }

    return submit_dict

  def submit(self, *a):
    subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(self.submit_dict)])

