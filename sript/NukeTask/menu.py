# -*- coding: utf-8 -*-
import nuke
from nukescripts import panels
import sys
#import getpass
#userName = getpass.getuser()
#pluginPath = "C:/Users/" + userName + "/.nuke"
pluginPath= os.path.join(os.path.dirname(__file__),'ManageTask').replace('\\','/')
sys.path.append(pluginPath)
#from ManageTask import create_shot_UI,create_task_UI,outPutXlsfile,setStatus,showShotInfo

# def CreateTask():
    # import  create_task_UI
    # create_task_UI.run()
    # reload (create_shot_UI)

# nuke.menu('Nuke').addCommand('Toolkit/CreateTask',lambda:_CreateTask)
# menu_bar = nuke.menu('Nuke')#menu参数是Nuke

# menu_bar.addCommand('Toolkit/CreateShot',CreateShot)

    # h=create_shot_UI.Widget
    # print h
    # win=panels.registerWidgetAsPanel('h', 'create_shot_UI', 'farts', True)
    # pane = nuke.getPaneFor('Properties.1')
    # win.addToPane(pane) 
    # return create_shot_UI.Widget
# def CreateShot():
import create_shot_UI
reload(create_shot_UI)
import create_task_UI
reload(create_task_UI)
panels.registerWidgetAsPanel('create_shot_UI.Widget', 'create shot', 'uk.co.thefoundry.Widget')
# pane = nuke.getPaneFor('Properties.1')
# panels.registerWidgetAsPanel('create_shot_UI.Widget', 'create_shot', 'MyWindowsShot', True).addToPane(pane)
panels.registerWidgetAsPanel('create_task_UI.MainWindow', 'create shotTask', 'uk.co.thefoundry.MainWindow')
# pane1 = nuke.getPaneFor('Properties.2')
# panels.registerWidgetAsPanel('create_task_UI.MainWindow', 'create_shotTask', 'MyWindowsTask', True).addToPane(pane1)

# menu_bar = nuke.menu('Nuke')#menu参数是Nuke

# menu_bar.addCommand('Toolkit/CreateShot',CreateShot)
# menu_bar.addCommand('Toolkit/CreateTask',CreateTask)
# menu_bar.addCommand('Toolkit/ExportExcelFile',CreateExcelfie)
# menu_bar.addCommand('Toolkit/SetStatus',SetStatus)
# menu_bar.addCommand('Toolkit/showShotInfo',showShotInfo)

# tool_bar = nuke.toolbar('Nodes')#toolbar参数是Nodes




