#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import nuke
import time
import os
from nukescripts import panels
from functools import partial
import create_task
import traceback
try:
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtGui as Gui
    # from PySide2.QtWebEngineWidgets import QWebEngineView 
    from PySide2 import QtCore
except ImportError:
    from PySide import QtGui
    from PySide import QtWebKit as QtWebKit
    from PySide import QtCore

# project = "TWE"
Locator = []
GIF_FILE = os.path.join(os.path.dirname(__file__),'Logo/Loading.gif').replace('\\','/')
QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))

# 进度条函数
def _showProgress(label='', waitSeconds=0.01):
    def call(func):
        def handle(*args, **kwargs):
            progress = TextProgressDialog(label, action=func, args=args, kwargs=kwargs,
                                          waitSeconds=waitSeconds, parent=args[0])
            return progress.start()
        return handle
    return call

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Manage Task")
        self.initUI()
        self.resize(936, 400)

    def initUI(self):
        self.tabelDialog = TabDialog()
        self.setCentralWidget(self.tabelDialog)
    # 窗体移动触发事件
    def moveEvent(self, event):
        Locator.append(self.frameGeometry())    # 获取主窗体的位置及大小信息
        
class TabDialog(QtGui.QDialog):
    def __init__(self,parent = None):
        super(TabDialog, self).__init__(parent)
        tabWidget = QtGui.QTabWidget()

        tabWidget.addTab(TreeWidgetOne(),u"选中backdrop创建任务")
        # tabWidget.addTab(TreeWidgetTwo(),u'选中节点创建任务')

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(tabWidget)
        self.setLayout(mainLayout)

#根据选中的baakdrop节点的层级关系来设置任务的状态

class TreeWidgetOne(QtGui.QWidget):
    def __init__(self):
        super(TreeWidgetOne, self).__init__()
        self.resize(837, 378)
        self.setWindowTitle('create task')
        self.intUI()
        import create_task
        reload(create_task)
        self.comboBoxSelectList = []
        self.CreateTask_api = create_task.CreateTask()

    def intUI(self):

        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels([u'幕数',u'场次',u'镜头号', u'阶段',u"制作者",u"起始帧",u"结束帧",u"总帧数",u"描述"])  #加幕数信息
        self.tree.setColumnWidth(0,120)
        okbtn = QtGui.QPushButton(u'更新')
        self.createBtn = QtGui.QPushButton(u'创建')
        self.createBtn.setEnabled(False)
        self.progressBar = QtGui.QProgressBar()

        comboBox = ['comboBox','comboBox1','comboBox2','comboBox3','comboBox4','comboBox5']

        shotLabel = QtGui.QLabel('Shot')
        self.shotLineEdit = QtGui.QLineEdit()
        self.shotLineEdit.setFixedSize(100,20)
        self.shotLineEdit.setPlaceholderText(u'按回车键返回示例')
        selectLabel = QtGui.QLabel(u'请选择Shot对应的层级')
        self.shotComboBox = QtGui.QComboBox()


        self.nodelabel = QtGui.QLabel()
        
        space = QtGui.QSpacerItem(50,10)
        
        topHlayout = QtGui.QHBoxLayout()
        topHlayout.addWidget(shotLabel)
        topHlayout.addWidget(self.shotLineEdit)
        topHlayout.addWidget(self.nodelabel)
        topHlayout.addSpacerItem(space)
        topHlayout.addWidget(selectLabel)
        topHlayout.addWidget(self.shotComboBox)
        topHlayout.addStretch()

        label = QtGui.QLabel('Level 1')
        label1 = QtGui.QLabel('Level 2')
        label2 = QtGui.QLabel('Level 3')
        label3 = QtGui.QLabel('Level 4')
        label4 = QtGui.QLabel('Level 5')
        label5 = QtGui.QLabel('Level 6')

        for i in range(6):
            comboBox[i] = QtGui.QComboBox()
            comboBox[i].addItem('')
            comboBox[i].addItem('Act')
            comboBox[i].addItem('Sequence')
            comboBox[i].addItem('Step')
            comboBox[i].addItem('Artist')
            comboBox[i].addItem('Description')

        gridlay = QtGui.QGridLayout()
        gridlay.addWidget(label,0,0)
        gridlay.addWidget(comboBox[0],0,1)
        gridlay.addWidget(label1,1,0)
        gridlay.addWidget(comboBox[1],1,1)
        gridlay.addWidget(label2,2,0)
        gridlay.addWidget(comboBox[2],2,1)
        gridlay.addWidget(label3,3,0)
        gridlay.addWidget(comboBox[3],3,1)
        gridlay.addWidget(label4,4,0)
        gridlay.addWidget(comboBox[4],4,1)
        gridlay.addWidget(label5,5,0)
        gridlay.addWidget(comboBox[5],5,1)

        hlay = QtGui.QHBoxLayout()
        hlay.addWidget(okbtn)
        hlay.addWidget(self.progressBar)
        hlay.addWidget(self.createBtn)

        # Vlay = QtGui.QVBoxLayout()
        # Vlay.addWidget(self.tree)
        # Vlay.addLayout(hlay)
        
        
        
        Vlay1 = QtGui.QHBoxLayout()
        Vlay1.addLayout(gridlay)
        Vlay1.addWidget(self.tree)

        Hlay = QtGui.QVBoxLayout()
        Hlay.addLayout(topHlayout)
        # Hlay.addWidget(self.tree)
        Hlay.addLayout(Vlay1)
        Hlay.addLayout(hlay)
        self.setLayout(Hlay)

        comboBox[0].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[0],0))
        comboBox[1].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[1],1))
        comboBox[2].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[2],2))
        comboBox[3].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[3],3))
        comboBox[4].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[4],4))
        comboBox[5].currentIndexChanged.connect(lambda: self.comboBoxChange(comboBox[5],5))
        self.shotComboBox.currentIndexChanged.connect(lambda:self.shotComboBoxF(self.shotComboBox))
        self.shotLineEdit.returnPressed.connect(self.shotLineEditText)
        okbtn.clicked.connect(self.getTreeData)
        self.createBtn.clicked.connect(self.createTaskFunc)

    def comboBoxChange(self,comboBox,int):
        '''

        :param comboBox:传递过来的对象本身
        :param int: 给选中的comboBox编号序号留到下面筛选使用
        :return: dic
        '''
        dic = {}
        dic[int] = comboBox.currentText()
        self.comboBoxSelectList.append(dic)    #self.comboBoxSelectList已在init方法下声明


    def shotComboBoxF(self,comboBox):#如果不给字符串切割，则combox给空
        try:
            self.num = int(comboBox.currentText().split('.')[0]) - 1
        except:
            self.num =''

    def shotLineEditText(self):#通过按压回车键，对combox增加item，选择对应的镜头号
        nameList = ''
        lis = []
        self.nodelabel.clear()
        self.shotComboBox.clear()
        text = self.shotLineEdit.text()
        if text:
            nodes = nuke.selectedNodes()
            for data_node  in nodes:
                if data_node.Class() == 'Read':
                    lis.append(data_node)

            filename = lis[0].knob('file').value().split('/')[-1].split('.')[0]
            if text in filename:
                length = len(filename.split(text))
                for i in range(length):
                    name = filename.split(text)[i]
                    self.shotComboBox.addItem(str(i+1)+'.shot')
                    nameList = nameList + ' ' + str(i+1) + ':' +name
                self.nodelabel.setText(nameList)
                return text
            else:
                self.nodelabel.setText(u'请输入正确分割符')


    @_showProgress(label='Getting global Information')  # 修饰器
    def getTeamworkInfo(self,project,epsLis,shotLis):
        teamworkShot = create_task.CreateTask().getshotInfo(project,epsLis,shotLis)
        dic = {}
        epsName = []
        lis = []
        for data_team in teamworkShot:
            epsName.append(data_team['eps.eps_name'])
            dic[data_team['eps.eps_name']] = data_team['shot.shot']
            lis.append(dic)
            dic = {}

        for i in lis:
            for k,v in i.items():
                dic.setdefault(k,[]).append(v)

        return dic,epsName

    # @_showProgress(label='Getting global Information')  # 修饰器
    def AssemblyData(self):
        '''
        组装数据
        :return:
        '''

        Info = self.sortComboBoxSelectList(self.comboBoxSelectList)  #给backdrop排列先后顺序，最里面的排在第一位，依次类推
        NodeInfoList = []              #节点信息以列表里面存字典的方式存储
        nodes = nuke.selectedNodes()
        for k, v in self.nodeInfo(nodes,len(Info)).items():     #nodeInfo函数是组装一个数据字典给设置节点信息使用
            try:
                Shot = nuke.toNode(k).knob('file').value().split('/')[-1].split('.')[0].split('_')[self.num]  # 镜头号有相同的存在
            except:
                Shot = nuke.toNode(k).knob('file').value().split('/')[-1].split('.')[0]  #查询是否选择了镜头号，如果没选择则按照文件全名
            dic = {
                "Node": k,
                "Act":'',
                "Sequence": '',
                "Shot": Shot,
                "Step": '',
                "Artist": '',
                "First": nuke.toNode(k).knob('first').value(),
                "Last": nuke.toNode(k).knob('last').value(),
                "Allframe": nuke.toNode(k).knob('last').value()-nuke.toNode(k).knob('first').value(),
                "Description": '',
                "Status":'',
                "BackdropNode":self.sortlayer(v)  #排列好的层级关系
            }
            NodeInfoList.append(dic)

        for i in range(len(Info)):
            for j in range(len(NodeInfoList)):
                NodeInfoList[j][Info[i].values()[0]] = nuke.toNode(NodeInfoList[j]['BackdropNode'][i]).knob('label').value().strip()
        return NodeInfoList


#更新treewidget上面的信息，先组装数据然后在往里面写数据
    def getTreeData(self):
        activate = True #用于按钮是否激活

        self.createList = []
        epsNum = self.AssemblyData()
        epsLisNode = []
        shotLisNode = []

        for data_info in epsNum:
            shotLisNode.append(data_info['Shot'])
            epsLisNode.append(data_info['Sequence'])
            
        pro_read = [x for x in nuke.selectedNodes() if x.Class() == 'Read'][0]
        project = pro_read.knob('file').value().split('/')[-1].split('.')[0].split('_')[0]
        
        shotLisTeamwotk, epsNameTeamwork = self.getTeamworkInfo(project, epsLisNode, shotLisNode)
        
        self.tree.clear()
        
        for data_tree in epsNum:
            first = QtGui.QTreeWidgetItem(self.tree)
            first.setExpanded(True)
            if data_tree['Sequence'] in epsNameTeamwork:
                if data_tree['Shot'] in shotLisTeamwotk[data_tree['Sequence']]:
                    first.setText(0,data_tree['Act'])
                    first.setText(1,data_tree['Sequence'])
                    first.setText(2,data_tree['Shot'])
                    first.setText(3,data_tree['Step'])
                    first.setText(4,data_tree['Artist'])
                    first.setText(5,str(data_tree['First']))
                    first.setText(6,str(data_tree['Last']))
                    first.setText(7,str(data_tree['Allframe']))
                    first.setText(8,data_tree['Description'])
                    self.createList.append(data_tree)
                else:
                    first.setText(0,data_tree['Act'])
                    first.setText(1,data_tree['Sequence'])
                    first.setText(2,data_tree['Shot']+' None')
                    first.setText(3,data_tree['Step'])
                    first.setText(4,data_tree['Artist'])
                    first.setText(5,str(data_tree['First']))
                    first.setText(6,str(data_tree['Last']))
                    first.setText(7,str(data_tree['Allframe']))
                    # first.setText(8,epsNum[i]['Description'])
                    first.setText(8,u'镜头未创建')
                    activate = False
            else:
                first.setText(0, data_tree['Act'])
                first.setText(1, data_tree['Sequence']+' None')
                first.setText(2, data_tree['Shot'])
                first.setText(3, data_tree['Step'])
                first.setText(4, data_tree['Artist'])
                first.setText(5, str(data_tree['First']))
                first.setText(6, str(data_tree['Last']))
                first.setText(7, str(data_tree['Allframe']))
                # first.setText(8,epsNum[i]['Description'])
                first.setText(8, u'场次未创建')
                activate = False
        if activate :
            self.createBtn.setEnabled(True)
        else:
            self.createBtn.setEnabled(False)
                    
        # for i in range(len(epsNum)):
            # first = QtGui.QTreeWidgetItem(self.tree)
            # first.setExpanded(True)
            # if epsNum[i]['Sequence'] in epsNameTeamwork:
                # if epsNum[i]['Shot'] in shotLisTeamwotk[epsNum[i]['Sequence']]:
                    # first.setText(0,epsNum[i]['Act'])
                    # first.setText(1,epsNum[i]['Sequence'])
                    # first.setText(2,epsNum[i]['Shot'])
                    # first.setText(3,epsNum[i]['Step'])
                    # first.setText(4,epsNum[i]['Artist'])
                    # first.setText(5,str(epsNum[i]['First']))
                    # first.setText(6,str(epsNum[i]['Last']))
                    # first.setText(7,str(epsNum[i]['Allframe']))
                    # first.setText(8,epsNum[i]['Description'])
                    # self.createList.append(epsNum[i])
                # else:
                    # first.setText(0,epsNum[i]['Act'])
                    # first.setText(1,epsNum[i]['Sequence'])
                    # first.setText(2,epsNum[i]['Shot']+' None')
                    # first.setText(3,epsNum[i]['Step'])
                    # first.setText(4,epsNum[i]['Artist'])
                    # first.setText(5,str(epsNum[i]['First']))
                    # first.setText(6,str(epsNum[i]['Last']))
                    # first.setText(7,str(epsNum[i]['Allframe']))
                    # first.setText(8,epsNum[i]['Description'])#
                    # first.setText(8,u'镜头未创建')
            # else:
                # first.setText(0,u'场次未创建')
                # first.setText(0, epsNum[i]['Act'])
                # first.setText(1, epsNum[i]['Sequence']+' None')
                # first.setText(2, epsNum[i]['Shot'])
                # first.setText(3, epsNum[i]['Step'])
                # first.setText(4, epsNum[i]['Artist'])
                # first.setText(5, str(epsNum[i]['First']))
                # first.setText(6, str(epsNum[i]['Last']))
                # first.setText(7, str(epsNum[i]['Allframe']))
                # first.setText(8,epsNum[i]['Description'])#
                # first.setText(8, u'场次未创建')


    def createTaskFunc(self):
        '''
        :return: 创建功能
        '''
        pro_read = [x for x in nuke.selectedNodes() if x.Class() == 'Read'][0]
        project = pro_read.knob('file').value().split('/')[-1].split('.')[0].split('_')[0]
        
        pipelineName = self.CreateTask_api.getPipelineName(project)#获取teamwork任务阶段

        pipelineNameDic = {}
        for data_updata in pipelineName:
            pipelineNameDic.update({data_updata['name']:data_updata['id']})
            
        # for i in range(len(pipelineName)):
            # pipelineNameDic.update({pipelineName[i]['name']:pipelineName[i]['id']})
        # print pipelineNameDic

        #pipeline = [{'id': u'01F99FCE-3407-E541-E14C-DE4BD9D17AB7', 'name': u'animation'}]
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(self.createList))
        value = 0
        #循环创建
        for data_create in self.createList:#9.20.22.43
            if data_create['Step'] in pipelineNameDic.keys():
				
                self.CreateTask_api.createShotTask(project, data_create['Sequence'], data_create['Shot'],data_create['Act'],
                                                   pipelineNameDic[data_create['Step']], data_create['Step'])
                self.CreateTask_api.setShotTask(project, data_create['Sequence'], data_create['Shot'],data_create['Act'],
                                                data_create['Step'], data_create['Artist'],description = data_create['Description'])
                                                
                self.progressBar.setValue(value + 1)
                value += 1
        nuke.message("Create Successful")
        
        # for i in range(len(self.createList)):
            # if self.createList[i]['Step'] in pipelineNameDic.keys():
     
                # self.CreateTask_api.createShotTask(project, self.createList[i]['Sequence'], self.createList[i]['Shot'],
                                                   # pipelineNameDic[self.createList[i]['Step']], self.createList[i]['Step'])
                # self.CreateTask_api.setShotTask(project, self.createList[i]['Sequence'], self.createList[i]['Shot'],
                                                # self.createList[i]['Step'], self.createList[i]['Artist'])
                # self.progressBar.setValue(value + 1)
                # value += 1
        # self.progressBar.setValue(0)
        # nuke.message("Create Successful")


    def isReadInBackdrop(self,read, backdrop):
        '''

        :param read:节点 类型可以是多种
        :param backdrop: 节点
        :return:
        '''
        if read in backdrop.getNodes():
            return True

    def nodeInfo(self,nodes,layer):
        '''
        用来返回每个节点对应多少个层级关系
        :param nodes:节点
        :param layer:层的个数
        :return:组装成一个新的字典
        '''
        # nodes = nuke.selectedNodes()
        readNode = [i for i in nodes if i.Class() == "Read"]
        backdropNode = [i for i in nodes if i.Class() == "BackdropNode"]
        node = []
        dic = {}
        for i in range(len(readNode)):
            for j in range(len(backdropNode)):
                if self.isReadInBackdrop(readNode[i], backdropNode[j]):
                    dic[readNode[i]['name'].value()] = backdropNode[j]['name'].value()
                    node.append(dic)
                    dic = {}
        for i in node:
            for k, v in i.items():
                dic.setdefault(k, []).append(v)
        a = [i for i in dic.keys() if len(dic[i]) != layer]
        for i in a:
            dic.pop(i)
        return dic

    def sortlayer(self,s):
        '''

        :param s:  s = ['BackdropNode13', 'BackdropNode3', 'BackdropNode4', 'BackdropNode14']
        :return:按照层级顺序重新排列
        '''
        if len(s) == 1:
            return s
        else:
            outbackdrop = []
            inbackdrop = []
            for i in range(len(s)):
                for j in range(i + 1, len(s)):
                    if self.isReadInBackdrop(nuke.toNode(s[i]), nuke.toNode(s[j])):
                        outbackdrop.append(s[j])
                        inbackdrop.append(s[i])
                    elif self.isReadInBackdrop(nuke.toNode(s[j]), nuke.toNode(s[i])):
                        outbackdrop.append(s[i])
                        inbackdrop.append(s[j])

            #把层级的出现次数排列一下
            from collections import Counter
            outCounter = Counter(outbackdrop).most_common(4)
            inCounter = Counter(inbackdrop).most_common(4)

            newSort = []
            for i in outCounter:
                newSort.append(i[0])
            endSort = [i for i in inCounter[::-1] if i[0] not in newSort]
            for i in endSort:
                newSort.append(i[0])
            return newSort

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
                if revertList[i].keys() == revertList[j].keys():
                    revertList1[j] = {}
        for i in range(len(revertList1)):
            if revertList1[i] != {}:
                lisInfo.append(revertList1[i])


        Info = [i for i in lisInfo if i.values()[0]!=''][::-1]   #选取的层数   把选取的字典重新排序
        for i in range(len(Info)):
            for j in range(i+1,len(Info)):
                if Info[i].keys()[0]>Info[j].keys()[0]:
                    s = Info[i]
                    Info[i] = Info[j]
                    Info[j] = s
        return Info

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
                self.raiseExceptionDialog(error = self._actionException)
            return self._actionReturned

    # 触发重定义大小来获取中心位置，并移动
    def resizeEvent(self, event):
        # 获取parent，即SearchView窗口的宽高。
        self.width = self._parent.frameGeometry().width()
        self.height = self._parent.frameGeometry().height()

        self.x = Locator[-1].x() + self.width/2
        self.y = Locator[-1].y() + self.height/2

        self.pointMove.setX(self.x)
        self.pointMove.setY(self.y)
        self.move(self.pointMove)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    # stepui = TreeWidget()
    # stepui.show()
    app.exec_()