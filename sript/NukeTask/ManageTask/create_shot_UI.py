#!/usr/bin/env python
# -*- coding:utf-8 -*-

import nuke
from nukescripts import panels
import sys,os
import time
import traceback
from datetime import datetime
import xlsxwriter
from functools import partial
try:
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtGui as Gui
    # from PySide2.QtWebEngineWidgets import QWebEngineView
    from PySide2 import QtCore
except ImportError:
    from PySide import QtGui
    from PySide import QtWebKit as QtWebKit
    from PySide import QtCore
    
TempPath = r'C:/image/tempImage'
OTHER_STATE = [u'缩略图',u'项目',u'幕数',u'场次',u'镜头号',u'开始帧',u'结束帧',u'帧数',u'状态',u'日期']
Locator = []
GIF_FILE = os.path.join(os.path.dirname(__file__),'Logo/Loading.gif').replace('\\','/')
QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))

def _showProgress(label='', waitSeconds=0.01):
    def call(func):
        def handle(*args, **kwargs):
            progress = TextProgressDialog(label, action=func, args=args, kwargs=kwargs,
                                          waitSeconds=waitSeconds, parent=args[0])
            return progress.start()
        return handle
    return call

class Widget(QtGui.QDialog):
    def __init__(self,parent = None):
        super(Widget, self).__init__(parent)
        self.resize(1000,370)
        self.setWindowTitle('nuke_create_shot')
        self.initUI()
        self.comboBoxSelectList = []
        import create_shot
        reload(create_shot)
        self.shot = create_shot.CreateShots()
        self.lis = []

    def moveEvent(self, event):
        Locator.append(self.frameGeometry())  # 获取主窗体的位置及大小信息

    #初始化界面
    def initUI(self):

        comboBox = ['comboBox', 'comboBox1', 'comboBox2', 'comboBox3', 'comboBox4', 'comboBox5']
        lineEditlabel = QtGui.QLabel(u'请输入分隔符:')

        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setFixedSize(60,20)
        self.lineEdit.setPlaceholderText(u'按回车键返回示例')

        self.lineEdit.returnPressed.connect(self.lineEditText)

        self.displayLabel = QtGui.QLabel()

        label1 = QtGui.QLabel(u'示例:')
        label2 = QtGui.QLabel(u'一级: ')
        label3 = QtGui.QLabel(u'二级: ')
        label4 = QtGui.QLabel(u'三级: ')
        label5 = QtGui.QLabel(u'四级: ')

        for i in range(6):
            comboBox[i] = QtGui.QComboBox()
            comboBox[i].addItem('')
            comboBox[i].addItem('project')
            comboBox[i].addItem('act')
            comboBox[i].addItem('eps')
            comboBox[i].addItem('shot')
        
        topHlayout = QtGui.QHBoxLayout()#最顶部的布局
        topHlayout.addWidget(lineEditlabel)
        topHlayout.addWidget(self.lineEdit)
        topHlayout.addStretch()
        topHlayout.addWidget(label1)
        topHlayout.addWidget(self.displayLabel)
        topHlayout.addStretch()


        midHlayout = QtGui.QHBoxLayout()#中间的布局
        midHlayout.addWidget(label2)
        midHlayout.addWidget(comboBox[2])
        midHlayout.addStretch()
        midHlayout.addWidget(label3)
        midHlayout.addWidget(comboBox[3])
        midHlayout.addStretch()
        midHlayout.addWidget(label4)
        midHlayout.addWidget(comboBox[4])
        midHlayout.addStretch()
        midHlayout.addWidget(label5)
        midHlayout.addWidget(comboBox[5])
        midHlayout.addStretch()

        mid2Hlayout = QtGui.QHBoxLayout()#中间的布局
        topVlayout = QtGui.QVBoxLayout()#中间的布局
        topVlayout.addLayout(topHlayout)
        topVlayout.addLayout(midHlayout)
        topVlayout.addLayout(mid2Hlayout)


        self.updateBtn = QtGui.QPushButton(u'刷新')

        self.createBtn = QtGui.QPushButton(u'创建')
        self.updateShotInfoBtn = QtGui.QPushButton(u'更新')
        self.createBtn.setEnabled(False)

        space = QtGui.QSpacerItem(200,10)

        self.progress = QtGui.QProgressBar()


        hlay = QtGui.QHBoxLayout()
        hlay.addWidget(self.updateBtn)
        hlay.addStretch(1)
        hlay.addWidget(self.createBtn)
        hlay.addWidget(self.updateShotInfoBtn)

        vlay = QtGui.QVBoxLayout()
        vlay.addLayout(hlay)
        vlay.addWidget(self.treeWidget())
        vlay.addWidget(self.progress)

        Hlay = QtGui.QVBoxLayout()
        Hlay.addLayout(topVlayout)
        Hlay.addLayout(vlay)
        Hlay.addSpacerItem(space)
        Hlay.addLayout(self.exportExcelFileWidget())
        
        self.setLayout(Hlay)


        # comboBox[0].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[0],0))
        # comboBox[1].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[1],1))
        comboBox[2].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[2],0))
        comboBox[3].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[3],1))
        comboBox[4].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[4],2))
        comboBox[5].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[5],3))

        self.updateBtn.clicked.connect(self.update)
        self.createBtn.clicked.connect(self.create)

        self.updateShotInfoBtn.clicked.connect(self.updateShotInfo)

#treeWidget
    def treeWidget(self):
        self.tree = QtGui.QTreeWidget()
        heads = [u'节点',u'幕数',u'场次',u'镜头',u'起始帧',u'结束帧',u'是否创建',u'镜头状态',u'更改状态','Note','']
        self.tree.setHeaderLabels(heads)

        return self.tree

#导出excel界面
    def exportExcelFileWidget(self):
        label = QtGui.QLabel(u'输出文件路径')
        self.file_dit = QtGui.QLineEdit()
        browserBtn = QtGui.QPushButton('Browser')
        self.check_image = QtGui.QCheckBox(u'是否导出缩略图')
        exportBtn = QtGui.QPushButton('Export')
        exportBtn.setFixedSize(120,20)
        hlay = QtGui.QHBoxLayout()
        hlay.addWidget(label)
        hlay.addWidget(self.file_dit)
        hlay.addWidget(browserBtn)

        hlay1 = QtGui.QHBoxLayout()
        hlay1.addWidget(self.check_image)
        hlay1.addWidget(exportBtn)

        vlay = QtGui.QVBoxLayout()
        vlay.addLayout(hlay)
        vlay.addLayout(hlay1)

        browserBtn.clicked.connect(self.browser)
        exportBtn.clicked.connect(self.exportExcel)

        return vlay

    def browser(self):

        filePath, Type = QtGui.QFileDialog.getSaveFileName(self, "Export excel file", "", "excel file (*.xlsx)")
        self.file_dit.setText(unicode(filePath))


    def exportExcel(self):
        path = self.file_dit.text()
        if path:
                nodeInfo = self.getNodesInfo()
                if nodeInfo:
                    self.wirteInfoFromNode(path,nodeInfo)
                # self.destroy()
                    nuke.message('Export successful')
                else:
                    nuke.message('Please select to node if you want to export excel file')
        else:
            nuke.message('please write file path')


    # @_showProgress(label='get information')
    # def getNodesInfo_bank(self):
        # comboBoxList = self.sortComboBoxSelectList(self.comboBoxSelectList)
        # text = self.lineEditText()
        # node = nuke.selectedNodes()
        # nodeInfoList = []
        # for i in range(len(node)):
            # if  node[i].Class() == 'Read':
                # nodePath = node[i].knob('file').value()
                # filename = os.path.basename(nodePath)
                # Fullname = filename.split('.')[0]
                # project, act, eps, shot = self.getProjectAndEpsAndShot(comboBoxList, Fullname, text)
                # first = node[i].knob('first').value()
                # last = node[i].knob('last').value()
                # frame = last - first
                # nodeInfo = {
                    # "name": Fullname,
                    # "project": project,
                    # "screen_num":act,
                    # "eps": eps,
                    # "shot": shot,
                    # "first": first,
                    # "last": last,
                    # "frame": frame,
                    # "status": '1',
                    # "nodeType": node[i].Class()
                # }

                # status = self.shot.getepsStatus(project,eps, shot)

                # if status:
                    # nodeInfo.update(status[0])
                # else:
                    # nodeInfo.update({"status": '0'})
                # nodeInfoList.append(nodeInfo)
        # return nodeInfoList
        
    @_showProgress(label='get information')
    def getNodesInfo(self):
        comboBoxList = self.sortComboBoxSelectList(self.comboBoxSelectList)
        text = self.lineEditText()
        node = nuke.selectedNodes()
        nodes = self.NodesDuplicate(node)
        nodeInfoList = []
        for node in nodes:
            nodePath = node.knob('file').value()
            filename = os.path.basename(nodePath)
            Fullname = filename.split('.')[0]
            project, act, eps, shot = self.getProjectAndEpsAndShot(comboBoxList, Fullname, text)
            first = node.knob('first').value()
            last = node.knob('last').value()
            frame = last - first
            nodeInfo = {
                "name": Fullname,
                "project": project,
                "screen_num":act,
                "eps": eps,
                "shot": shot,
                "first": first,
                "last": last,
                "frame": frame,
                "status": '1',
                "nodeType": node.Class()
            }

            status = self.shot.getepsStatus(project,eps, shot)

            if status:
                nodeInfo.update(status[0])
            else:
                nodeInfo.update({"status": '0'})
            nodeInfoList.append(nodeInfo)
        return nodeInfoList
    
    def NodesDuplicate(self,node):#node 去重
        node_all = [x for x in node if x.Class() == 'Read']
        reverNode = node_all[::-1]
        nodes = []
        
        for i in range(len(reverNode)):
            for j in range(i+1,len(reverNode)):
                if reverNode[i].knob('file').value() == reverNode[j].knob('file').value():
                    nodes.append(reverNode[j])
        nodes_data = list(set(node_all)^set(nodes))
        return nodes_data
    
    def wirteInfoFromNode(self, path, nodeInfo):
        '''
        :param path: excel存储路径
        :return:
        '''
        work_book = xlsxwriter.Workbook(path)
        style1 = work_book.add_format({'align': 'left', 'font_size': 9, 'num_format': 'dd/mm/yyyy hh:mm AM/PM'})
        worksheet = work_book.add_worksheet('Export shot information')
        workformat = work_book.add_format()
        workformat_head = work_book.add_format({'bold': True, 'bg_color': 'green'})
        workformat.set_align('center')
        workformat.set_align('vcenter')
        worksheet.set_column('A:A', 40, workformat)#kaun
        worksheet.set_column('B:J', 15, workformat)
        worksheet.set_row(0, 20, workformat)

        for i in range(len(OTHER_STATE)):  # 对表头进行填写
            worksheet.write(0, i, OTHER_STATE[i], workformat_head)
        self.info = nodeInfo
        row = 1
        if self.info:
            for index, data in enumerate(self.info):
                worksheet.set_row(index+1, 120, workformat)#gao
                image_path = os.path.join(TempPath, data['name'] + '_mix.jpg')
                if self.check_image.isChecked():
                    if os.path.exists(image_path):
                        worksheet.insert_image(index+1,0,image_path,{'x_scale': 0.5, 'y_scale': 0.5})
                worksheet.write(index+1, 1, data['project'], workformat)
                worksheet.write(index+1, 2, data['screen_num'], workformat)
                worksheet.write(index+1, 3, data['eps'], workformat)
                worksheet.write(index+1, 4, data['shot'], workformat)
                worksheet.write(index+1, 5, data['first'], workformat)
                worksheet.write(index+1, 6, data['last'], workformat)
                worksheet.write(index+1, 7, data['frame'], workformat)
                if data['status'] == '1':
                    worksheet.write(index+1, 8, data['shot.status'], workformat)
                else:
                    worksheet.write(index+1, 8, u'镜头未创建', workformat)
                row+=1
            worksheet.write(row,9,datetime.now(),style1)
            print 'create successful'
            work_book.close()
        else:
            print 'plaese select right node'

#输入的分割符
    def lineEditText(self):
        lis = []
        nameList = ''
        text = self.lineEdit.text()
        if text:
            nodes = nuke.selectedNodes()
            if nodes == []:
                nuke.message('Please select ReadNodes')
            else:
                for i in range(len(nodes)):
                    if nodes[i].Class() == 'Read':
                        lis.append(nodes[i])

                filename = lis[0].knob('file').value().split('/')[-1].split('.')[0]
                
                if text in filename:
                    length = len(filename.split(text))
                    for i in range(length):
                        name = filename.split(text)[i]
                        nameList = nameList + ' ' + str(i+1) + ': ' +name
                    self.displayLabel.setText(nameList)
                    return text
                else:
                    self.displayLabel.setText(u'请输入正确分割符')

#选择的类别
    def comboBoxChange(self,comboBox,int):
        '''

        :param comboBox:传递过来的对象本身
        :param int: 给选中的comboBox编号序号留到下面筛选使用
        :return: dic
        '''
        dic = {}
        dic[comboBox.currentText()] = int
        self.comboBoxSelectList.append(dic)    #self.comboBoxSelectList已在init方法下声明

#给选择的顺序重新排序
    def sortComboBoxSelectList(self,list):
        '''
        :param list: 每选一次，到会有信息写进list，这时要过滤重复的，为空的其次再按照序号排好顺序
        :return:
        '''
        revertList = list[::-1]
        revertList1 = revertList
        lisInfo = []
        for i in range(len(revertList)):
            for j in range(i+1,len(revertList)):
                if revertList[i].values() == revertList[j].values():
                    revertList1[j] = {}
        for i in range(len(revertList1)):
            if revertList1[i] != {}:
                lisInfo.append(revertList1[i])
        Info = [i for i in lisInfo if i.keys()[0]!=''][::-1]   #选取的层数   把选取的字典重新排序
        for i in range(len(Info)):
            for j in range(i+1,len(Info)):
                if Info[i].values()[0]>Info[j].values()[0]:
                    s = Info[i]
                    Info[i] = Info[j]
                    Info[j] = s
        return Info


#更新功能，选中的节点之后点击更新   #得到信息
    # @_showProgress(label='get information')
    def update(self, *args, **kwargs):
        self.createBtn.setEnabled(True)
        epsList = []
        shotList = []
        self.tree.clear()
        if len([i for i in nuke.selectedNodes() if i.Class()=="Read"])>0:
            #获取信息
            eps_shot_info,project = self.getNukeNodes(nuke.selectedNodes()) #[{'ACT1': 'S031'}, {'ACT2': 'S030'}, {'ACT1': 'S032'}, {'ACT2': 'S031'}, {'ACT3': 'S032'}, {'ACT3': 'S031'}, {'ACT3': 'S030'}]
            for data in eps_shot_info:
            # for i in range(len(eps_shot_info)):
                epsList.append(data.keys()[0])
                shotList.append(data.values()[0])
            #从nuke得到的场次和镜头信息获取teamwork信息，存在的返回，不存在的不返回
            teamworkShotInfo,teamworkShotList = self.shot.getshotInfo(project,epsList,shotList) #得到信息
            self.updateShotLis,self.NotCreateNodeLis = self.setTreeDate(eps_shot_info,teamworkShotList,teamworkShotInfo)#eps_shot_info是从nuke节点获取的，teamworkShotList是nuke节点信息在teamwork查找的
            #返回的信息是已经创建的镜头和没有创建的镜头，已创建的拿出来给更新函数使用,没创建的拿去创建函数使用

# 创建镜头函数接口

    def createShot(self, createShotLis, node):
        '''
        :param createShotLis:需要创建的镜头，类型为字典[{'ACT1':'S030'},{'ACT1':'S031'}]
        :param node: 和选中的节点对比还是和所有的节点对比
        :return:
        '''

        comboBoxList = self.sortComboBoxSelectList(self.comboBoxSelectList)
        text = self.lineEditText()
        app = QtGui.QApplication.instance()
        if len(createShotLis) > 0:
            self.progress.setMinimum(0)
            self.progress.setMaximum(len(createShotLis))
            # self.progress.setValue(0)
            value = 0
            for index ,data in enumerate(node):
                filename = data.knob('file').value().split('/')[-1].split('.')[0]
                project, act, eps, shot = self.getProjectAndEpsAndShot(comboBoxList, filename, text)
                for data_1 in createShotLis:
                    if data_1.keys()[0] == eps and data_1.values()[0] == shot:
                        # 创建镜头

                        self.shot.SelectReadCreateShot(data, project, eps, shot, act)
                        # 获取treewidget的最高层的次数
                        row = self.tree.topLevelItemCount()
                        for i in range(row):
                            if self.tree.topLevelItem(i).text(2) == eps and self.tree.topLevelItem(i).text(
                                    3) == shot:  # 找的对应的行然后更改信息
                                self.tree.topLevelItem(i).setText(6, u'已创建')
                                app.processEvents()
                        value+=1
                        self.progress.setValue(index+1)
                        break
            nuke.message('Create successful')
            self.update()
        else:
            nuke.message('No node can be created')

#更新功能
    def updateShotInfo(self):

        nodes = nuke.selectedNodes()
        self.updateShotFunction(self.updateShotLis, nodes)

#更新函数

    def updateShotFunction(self,updateShotLis,nodes):
        '''
        :param updateShotLis:需要跟新的镜头信息   updateShotDic = [{
                                                "eps.eps_name": eps_shot_info[i].keys()[0],
                                                "shot.shot": eps_shot_info[i].values()[0],
                                                "shot.first_frame": node_first_frame,
                                                "shot.last_frame": node_last_frame
                                                }]
        :return:
        '''
        app = QtGui.QApplication.instance()
        comboBoxList = self.sortComboBoxSelectList(self.comboBoxSelectList)
        text = self.lineEditText()
        if len(updateShotLis)>0:
            for i in range(len(updateShotLis)):
                # nodes = nuke.selectedNodes()
                for j in range(len(nodes)):
                    if nodes[j].Class() == "Read":
                        nodeName = nodes[j].knob("name").value()
                        filename = nodes[j].knob('file').value().split('/')[-1].split('.')[0]
                        project, act, eps, shot = self.getProjectAndEpsAndShot(comboBoxList, filename, text)
                        if updateShotLis[i]['eps.eps_name'] == eps and updateShotLis[i]['shot.shot'] == shot:
                            firsrFrame = nodes[j].knob('first').value()
                            lastFrame = nodes[j].knob('last').value()
                            allFrame = lastFrame - firsrFrame
                            rgb = self.shot.getNodeInfo(nodes[j])['color']
                            status = self.shot.getNodeInfo(nodes[j])['status']
                            self.shot.updateShotFrame(project, eps, shot,firsrFrame,lastFrame,allFrame,rgb,status)
                            row = self.tree.topLevelItemCount()
                            for h in range(row):
                                if self.tree.topLevelItem(h).text(0) == nodeName:
                                    self.tree.topLevelItem(h).setText(6, u'已更新')
                                    print 'update successful'
                                    app.processEvents()
                                    break
            nuke.message('updata successfull')
        else:
            nuke.message('No lens to update')

#填写镜头信息函数
    def setTreeDate(self, eps_shot_info, teamworkShotList,teamworkShotInfo):
        '''
        :param eps_shot_info: 需要创建的节点镜头信息和场次信息[{'ACT1':'S030'},{'ACT1':'S031'}]
        :param teamworkShotList: 从teamwork获取的信息[{'ACT1':'S030'},{'ACT2':'S031'}]
        :return:
        '''
        app = QtGui.QApplication.instance()
        status = self.shot.getStatusAndColor()
        comboBoxList = self.sortComboBoxSelectList(self.comboBoxSelectList)
        text = self.lineEditText()
        node = [i for i in nuke.selectedNodes() if i.Class() == "Read"]  # 获取所有read节点
        CreateNodeLis = []
        NotCreateNodeDic = {}
        NotCreateNodeLis = []
        for i in range(len(eps_shot_info)):
            first = QtGui.QTreeWidgetItem(self.tree)
            first.setExpanded(True)
            for j in range(len(node)):
                filename = node[j].knob('file').value().split('/')[-1].split('.')[0]
                project,act,eps,shot = self.getProjectAndEpsAndShot(comboBoxList,filename,text)
                if eps_shot_info[i].keys()[0] == eps and eps_shot_info[i].values()[0] == shot:
                    nodeName = node[j].knob('name').value()
                    first.setText(0, str(nodeName))
                    first.setText(1, act)
                    first.setText(2, eps)
                    first.setText(3, shot)
                    first.setText(4, str(node[j].knob('first').value()))
                    first.setText(5, str(node[j].knob('last').value()))

                    node_first_frame = node[j].knob('first').value()
                    node_last_frame = node[j].knob('last').value()

                    if eps_shot_info[i] in teamworkShotList:
                        first.setText(6, u'已创建')
                        updateShotDic = {
                            "eps.eps_name": eps_shot_info[i].keys()[0],
                            "eps.act":act,
                            "shot.shot": eps_shot_info[i].values()[0],
                            "shot.first_frame": node_first_frame,
                            "shot.last_frame": node_last_frame
                        }
                        for s in range(len(teamworkShotInfo)):
                            if teamworkShotInfo[s]['eps.eps_name'] == eps_shot_info[i].keys()[0] and teamworkShotInfo[s]['shot.shot'] == eps_shot_info[i].values()[0]:
                                first.setText(7, teamworkShotInfo[s]['shot.status'])

                        comboBox = QtGui.QComboBox(self)
                        comboBox.addItem('')
                        comboBox.addItems(status.keys())
                        self.tree.setItemWidget(first, 8, comboBox)

                        button = QtGui.QPushButton(self)
                        button.setText('EditNote')
                        self.tree.setItemWidget(first, 9, button)

                        comboBox.currentIndexChanged.connect(partial(self.change, project, eps, shot, comboBox,nodeName))
                        button.clicked.connect(partial(self.buttonChange, project, eps, shot))
                        CreateNodeLis.append(updateShotDic)

                    else:
                        first.setText(6, u'镜头未创建')
                        NotCreateNodeDic[eps_shot_info[i].keys()[0]] = eps_shot_info[i].values()[0]
                        NotCreateNodeLis.append(NotCreateNodeDic)
                        NotCreateNodeDic = {}
                    app.processEvents()
                    break
        return CreateNodeLis, NotCreateNodeLis

#得到项目镜头场次信息
    def getProjectAndEpsAndShot(self,comboBoxList,filename,text):
        # project = 'TWE'                #--------------------------------------------可以提前给好项目名称避免没有选项目创建不出来镜头------------------------------------------
        eps = ''
        act = ''
        shot = filename
        try:
            for data_p in comboBoxList:
                try:
                    project = filename.split(text)[data_p['project']]
                except:
                    pass
        except IndexError:
            pass
        try:
            for data_e in comboBoxList:
                try:
                    eps = filename.split(text)[data_e['eps']]
                except:
                    pass
        except IndexError:
            pass
        try:
            for data_a in comboBoxList:
                try:
                    act = filename.split(text)[data_a['act']]
                except:
                    pass
        except IndexError:
            pass
        try:
            for data_s in comboBoxList:
                try:
                    shot = filename.split(text)[data_s['shot']]
                except:
                    pass
        except IndexError:
            pass
        return project,act,eps,shot

#comboBox函数,设置镜头状态

    def change(self,project,eps,shot,comboBox,nodeName,*args, **kwargs):

        # dic = {
        #     "nodeName":nodeName,
        #     "project":project,
        #     "eps":eps,
        #     "shot":shot,
        #     "status":comboBox.currentText()
        # }

        app = QtGui.QApplication.instance()
        data = self.shot.getStatusAndColor()
        value = '0x' + data[comboBox.currentText()].strip('#') + 'ff'
        nuke.toNode(nodeName).knob('tile_color').setValue(int(value, 16))
        colorValue = nuke.toNode(nodeName).knob('tile_color').value()
        rgbValue = hex(colorValue).strip('0x')
        color = rgbValue.rjust(8, "0")[0:6]
        # color = data[comboBox.currentText()].strip('#') + 'ffl'
        self.shot.setshotStatus(project,eps,shot,comboBox.currentText(),color)
        # self.shot.updateShotFrame(project, eps, shot, firsrFrame, lastFrame, allFrame, rgb, status)
        row = self.tree.topLevelItemCount()
        for h in range(row):
            if self.tree.topLevelItem(h).text(0) == nodeName:
                self.tree.topLevelItem(h).setText(7, comboBox.currentText())
                print 'update successful'
                app.processEvents()
        # self.lis.append(dic)

#NoteBtn函数
    def buttonChange(self,project,eps,shot):
        id = self.shot.getShotId(project,eps,shot)
        projectDb = self.shot.getProjectDatabase(project)
        self.shot.Send_cgtwNote(projectDb,id[0]['id'])


#获取nuke信息
    def getNukeNodes(self,nodes):
        '''
        :param nodes:镜头列表
        :return: 镜头字典{'ACT1':'S031'}
        '''
        comboBoxList = self.sortComboBoxSelectList(self.comboBoxSelectList)
        text = self.lineEditText()
        project = ''
        dic = {}
        lis = []
        for i in range(len(nodes)):
            if nodes[i].Class() == "Read":
                path = nodes[i].knob('file').value()
                filename = path.split("/")[-1].split('.')[0]
                project, act, eps, shot = self.getProjectAndEpsAndShot(comboBoxList, filename, text)
                dic[eps] = shot
                lis.append(dic)
                dic = {}
        run_function = lambda x,y:x if y in x else x + [y]
        lis = reduce(run_function,[[],] + lis)
        return lis,project   #[{u'ACT2': u'S031'}, {u'ACT2': u'S030'}]


#获取teamwork信息
    def getTeamWorkShotList(self,project):
        teamworkShotList = []
        dic = {}
        shotInfo = self.shot.epsShotInfo(project)   # shotInfo =[{'eps.eps_name': u'ACT66', 'id': u'995573EB-69BF-3104-5154-F08AA441CC58', 'shot.shot': u'S001'}] teamwork存在的场次和镜头
        for i in range(len(shotInfo)):              # lis = [{u'ACT66': u'S001'}]   teamwork存在的镜头都记录下来，为下面的判断做好准备
            dic[shotInfo[i]['eps.eps_name']] = shotInfo[i]['shot.shot']
            teamworkShotList.append(dic)
            dic = {}
        return teamworkShotList

    def create(self):
        node = [i for i in nuke.selectedNodes() if i.Class() == "Read"]
        self.createShot(self.NotCreateNodeLis, node)

# 进度类
class TextProgressDialog(QtGui.QLabel):
    '''A dialog to show the progress of the process.'''

    def __init__(self, text, action, args=[], kwargs={}, waitSeconds=1, parent=None):
        '''If the passed time is greater then waitSeconds, the dialog will pop up.'''

        self._text = text + ' '
        self._action = action
        self._args = args
        self._kwargs = kwargs
        self._actionReturned = None
        self._actionFinished = False
        self._actionFailed = False
        self._actionException = ''
        self._thread = None
        self.pointMove = QtCore.QPoint()
        self._waitSeconds = waitSeconds
        self._sleepSecond = 0.13
        self._go = True
        self._app = QtGui.QApplication.instance()
        QtGui.QLabel.__init__(self, parent)
        self._parent = parent
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def closeEvent(self, event):
        self._go = False
        QtGui.QLabel.closeEvent(self, event)

    def _run(self):
        self._thread = QtCore.QThread(self)

        def run():
            try:
                self._actionReturned = self._action(*self._args, **self._kwargs)
                self._actionFailed = False
            except:
                self._actionFailed = True
                self._actionException = traceback.format_exc()

            self._actionFinished = True
            self._go = False

        self._thread.run = run
        self._thread.start()

    def raiseExceptionDialog(self,error=''):
        import traceback
        if not error:
            error = traceback.format_exc()
        title = 'Error Warning'
        content = 'There is an error!\n'
        content += error
        typ = QtGui.QMessageBox.Critical

        content = unicode(content)
        QtGui.QMessageBox(typ, title, content, parent=None).exec_()

    def start(self):
        if self._action:
            self._run()
        start = time.time()
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 无边框
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.movie = Gui.QMovie(GIF_FILE)
        # 设置cacheMode为CacheAll时表示gif无限循环，注意此时loopCount()返回-1
        self.movie.setCacheMode(Gui.QMovie.CacheAll)
        # 播放速度
        self.movie.setSpeed(100)
        self.setMovie(self.movie)
        while self._go:
            passedTime = time.time() - start
            if passedTime >= self._waitSeconds:
                if self.isVisible() == False:
                    self.movie.start()
                    self.show()
            self._app.processEvents()
            time.sleep(self._sleepSecond)
        else:
            self._thread.quit()
            self.close()
            if self._actionFailed:
                self.raiseExceptionDialog(error=self._actionException)
            return self._actionReturned

    # 触发重定义大小来获取中心位置，并移动
    def resizeEvent(self, event):
        # 获取parent，即SearchView窗口的宽高。
        self.width = self._parent.frameGeometry().width()
        self.height = self._parent.frameGeometry().height()

        self.x = Locator[-1].x() + self.width / 2
        self.y = Locator[-1].y() + self.height / 2

        self.pointMove.setX(self.x)
        self.pointMove.setY(self.y)
        self.move(self.pointMove)
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Widget()
    window.show()
    app.exec_()

