# coding: UTF-8

# Debugging tools and logging for ESPN Animation projects pipeline

from c4d import gui

SCENE_PRELOAD =-1
SCENE_NEW     = 0
SCENE_OK      = 1
SCENE_BROKEN  = 2
SCENE_MISSING = 3

class BaseError(Exception):
    alert_map = {0: 'Prototype Error. You should not be seeing this.'}

    def __init__(self, message, alert=True):
        super(BaseError, self).__init__(message)
        self.message = message
        self.Alert(alert=alert)
        self.Cleanup()

    def Alert(self, alert):
        alert_text = "ERROR :: {0}".format(self.alert_map[self.message])
        if (alert):
            gui.MessageDialog(alert_text)
        else:
            return

    def Cleanup(self):
        pass

class FileError(BaseError):
    alert_map = {
        0: 'Scene backup folder not found or could not be created.',
        1: '',
        2: 'Your scene file name is invalid.  Must be name.#.c4d or name.c4d',
        3: 'Could not create one or more project folders.'
    }

class UIError(BaseError):
    alert_map = {
        0: 'Selected production could not be validated. Check the dropdown and try again.',
        1: 'Selected project could not be validated. Check the dropdown and try again.',
        2: 'Selected scene name could not be validated. Check the field and try again.',
        3: 'Selected framerate could not be validated. Check the field and try again.'
    }

class PipelineError(BaseError):
    alert_map = {
        0: 'No valid __SCENE__ object found. Has this scene been set up in the pipeline? If not, run the pipeline setup and try again.',
        1: 'Error validating scene metadata. Did you modify the __SCENE__ tag or rename the C4D file without using the pipeline tool?',
        2: 'Existing __SCENE__ object found. This command is intended to be run on a clean scene.',
        3: 'Could not load project data from database. Is this scene saved on the network in a project folder?',
        4: 'This operation is only permitted to create children of top-level RenderData.'
    }

class DatabaseError(BaseError):
    alert_map = {
        0: 'Master project database not found.',
        1: 'Production not found in database.',
        2: 'Team not found in production database.',
        3: 'Invalid parameter in settings database.'
    }

def warning(message, info=''):
    print "WARNING :: {0} : {1}".format(message, info)

def info(message, info=''):
    print "INFO :: {0} : {1}".format(message, info)

