#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import json
import subprocess
sys.path.append(r"C:\cgteamwork\bin\lib\pyside")
sys.path.append(r"C:\cgteamwork\bin\base")
import fllb
import nuke
try:
    from PySide2 import QtWidgets as QtGui
    from PySide2.QtWebEngineWidgets import QWebEngineView 
    from PySide2 import QtCore
except ImportError:
    from PySide import QtGui
    from PySide import QtWebKit as QtWebKit
    from PySide import QtCore

MOVE_SUFFIX =['avi','AVI' ,'mp4','MP4', 'mov','MOV','wmv', 'mpeg', 'mkv', 'flv', '3g2','swf','mgp','f4v', 'm4v','vob', '3gp','vob']
JPG_SUFFIX = ['jpg','JPG', 'png','PNG', 'gif', 'fpx', 'bmp', 'tiff', 'TIFF','tif', 'TIF','tga','TGA','exr','EXR','dpx','DPX']
#ffmpegPath=r"G:/Beijing/lib/ffmpeg/bin/ffmpeg.exe"
ffmpegPath = os.path.join(os.path.dirname(__file__),'ffmpeg/bin/ffmpeg.exe').replace('\\','/')
FFPROBE_PATH =  os.path.join(os.path.dirname(__file__),'ffmpeg/bin/ffprobe.exe').replace('\\','/')
TempPath = r'C:/image/tempImage'
'''请注意命名的冲突'''
class CreateShots():
    def __init__(self):
        import cgtw
        try:
            self._t_tw = cgtw.tw()
        except:
            nuke.message('Please open CGteamwork')
            return False
#得到数据库信息*******************************************
    def getProjectDatabase(self,project):
        t_info = self._t_tw.info_module("public", "project")
        filters = [
            ["project.code", "=", project],
        ]
        t_info.init_with_filter(filters)
        fields = ["project.database"]
        database = t_info.get(fields)[0]['project.database']
        return database


#创建eps场次号(如果存在则忽略)************************************
    def Create_eps(self,project,eps,act):
        """
        创建集数信息
        :param project:
        :eps: 'ep001'
        :return:
        """
        eps_List = []
        projectDb = self.getProjectDatabase(project)
        eps_name = self.getProjectEps(project)
        for i in range(len(eps_name)):
            eps_List.append(eps_name[i]['eps.eps_name'])
        t_info = self._t_tw.info_module(projectDb, "eps")
        
        Create_data = {"eps.eps_name":eps,"eps.act":act}
        
        if Create_data['eps.eps_name'] not in eps_List:
            t_info.create(Create_data)
            return True
        else:
            return False


#得到特定场次下面的镜头号****************************************
    def getEpsShot(self,project,eps):
        '''
        :param project:查询项目
        :param eps: 场次号，例如：ep001
        :return: 查询场次号下面所有的镜头号列表
        '''
        shotInfo = []
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, 'shot')
        filters = [
            ["eps.eps_name","=",eps]
            ]
        t_info.init_with_filter(filters)#过滤器
        fields = ["shot.shot"]#查询的内容
        data = t_info.get(fields)
        for i in data:
            shotInfo.append(i['shot.shot'])
        return shotInfo

# 得到eps场次名称******************************************
    def getProjectEps(self, project):
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "eps")
        filters = []
        t_info.init_with_filter(filters)
        fields = ["eps.eps_name"]
        data = t_info.get(fields)
        return data

#创建镜头******************************************************
    def Creatshot(self, project, eps, shot, rgb = '', first_frame = None, last_frame = None, frame = None,status = '',act = ''):
        '''
        :param project:
        :param eps:
        :param shot:
        :param rgb: 选中的节点颜色(默认为白色)
        :param first_frame:
        :param last_frame:
        :param frame:
        :return:
        '''
        projectDb = self.getProjectDatabase(project)
        self.Create_eps(project, eps,act)
        t_info = self._t_tw.info_module(projectDb, 'shot')
        shotdata = {"eps.eps_name": eps, "shot.shot": shot,
                    "shot.color": '#' + rgb,
                    "shot.first_frame":first_frame,
                    "shot.last_frame":last_frame,
                    "shot.frame":frame,
                    "shot.status":status,
                    }

        shotInfo = self.getEpsShot(project, eps)  # 得到eps当前场次下面的镜头信息
        if shot not in shotInfo:                    #避免重复创建
            t_info.create(shotdata)                  # 不存在则会创建
        else:                                         #场景修改则会修改teamwork信息
            filters = [['eps.eps_name', '=', eps],
                       ['shot.shot', '=', shot]]
            t_info.init_with_filter(filters)
            data = {'shot.color': '#' + rgb,
                    "shot.first_frame": first_frame,
                    "shot.last_frame": last_frame,
                    "shot.frame": frame,
                    "shot.status": status,
                    }
            t_info.set(data)


#创建选中的backdrop的镜头号*******************************************
    def createBackdropshot(self, project, eps, shot, rgb = '', first_frame = '', last_frame = '', frame = '',status = ''):
        projectDb = self.getProjectDatabase(project)
        self.Create_eps(project, eps)
        t_info = self._t_tw.info_module(projectDb, 'shot')
        shotdata = {"eps.eps_name": eps, "shot.shot": shot,
                    "shot.color": '#' + rgb,
                    "shot.first_frame":first_frame,
                    "shot.last_frame":last_frame,
                    "shot.frame":frame,
                    "shot.status":status
                    }
        t_info.create(shotdata)
        # shotInfo = self.getEpsShot(project, eps)  # 得到eps当前场次下面的镜头信息
        # if shot not in shotInfo:                    #避免重复创建
        #     t_info.create(shotdata)



#根据选中的节点改变镜头颜色(镜头不存在的话就创建)********************

    def SelectReadCreateShot(self,node,project,eps,shot,act):

        # read = nuke.selectedNodes()
        # for i in range(len(read)):
        #
        #     if read[i].Class() == "Read":

        nodeInfo = self.getNodeInfo(node)

        status = self.getNodeStatus(node)

        image = self.getPicture(node,project,eps,shot)
        self.getExcelImage(image)
        self.Creatshot(project, eps, shot, rgb = nodeInfo["color"],
                             first_frame = nodeInfo["first"],last_frame=nodeInfo["last"],frame=nodeInfo["allframe"],status=status,act = act)

        self.setshotImage(project, eps, shot,imagePath=image)

#选中backdrop节点，该节点标签创建场次，标签下面的read节点创建成镜头号*******((待修改)已修改)*********
    def SelectBackdropCreateShot(self,project,eps,shot,node):

        nodeInfo = self.getNodeInfo(node)
        project = nodeInfo["project"]

        status = self.getNodeStatus(node)

        image = self.getPicture(node,project,eps,shot)

        self.createBackdropshot(project, eps, shot, rgb=nodeInfo["color"],
                       first_frame=nodeInfo["first"], last_frame=nodeInfo["last"],
                       frame=nodeInfo["allframe"],status = status)
        self.setshotImage(project, eps, shot, imagePath=image)
        # else:
        #     print 'file path error'

# 根据节点颜色设置镜头状态*********************************************************
    def getNodeStatus(self, node):
        colorValue = node.knob('tile_color').value()
        if colorValue == 0:
            return "Wait"#统一设置为Wait状态
        else:
            return "Wait"
        # else:
        #     rgbValue = hex(colorValue).strip('0x')
        #     R = int(rgbValue[0:2], 16)
        #     G = int(rgbValue[2:4], 16)
        #     B = int(rgbValue[4:6], 16)
        #
        #     if R == G == B == 192:
        #         #return "Close"
        #         return "Wait"
        #     elif R == G == B == 129:
        #         #return "Ready"
        #         return  "Work"
        #     elif R ==255 and G == 158 and B == 62:
        #         return "Pause"
        #     elif R == 0 and G == 172 and B == 86:
        #         return "Approve"
        #     elif R == 110 and G == 221 and B == 0:
        #         return "Omit"
        #     elif R == 110 and G == 182 and B == 255:
        #         return "Test"
        #     elif R == 62 and G == 158 and B == 255:
        #         return "Revert"
        #     elif R == 255 and G == 62 and B == 62:
        #         return "Retake"
        #     elif R == 14 and G == 134 and B == 254:
        #         return "Check"
        #     elif R == 108 and G == 108 and B == 108:
        #         return "Active"
        #     else:
        #         return "Ready"
#->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # elif R > 180 and R <= 255 and G > 100 and G <= 255 and B >= 0 and B < 162:
            #     return "Pause"
            # elif R >= 0 and R < 100 and G > 122 and G < 222 and B > 36 and B < 136:
            #     return "Approve"
            # elif R > 10 and R < 160 and G > 171 and G <= 255 and B >= 0 and B < 50:
            #     return "Omit"
            # elif R > 60 and R < 160 and G > 90 and G < 210 and B > 200 and B <= 255:
            #     return "Test"
            # elif R > 12 and R < 112 and G > 108 and G < 208 and B > 205 and B <= 255:
            #     return "Revert"
            # elif R > 150 and R <= 255 and G >= 0 and G < 100 and B >= 0 and B < 100:
            #     return "Retake"
            # elif R >= 0 and R < 100 and G >= 0 and G < 140 and B > 150 and B <= 255:
            #     return "Check"
            # else:
            #     return "Ready"


# #得到rgb的值*****************************************************
#     def getRGB(self,node):
#         colorValue = node.knob('tile_color').value()
#         rgbValue = hex(colorValue).strip('0x')
#         rgb = rgbValue.rjust(8, "0")[0:6]
#         return rgb

#得到节点信息********************************************************************************
    def getNodeInfo(self,node):

        if node.Class() == 'Read':
            name = node.knob('name').value()
            path = node.knob('file').value()
            colorValue = node.knob('tile_color').value()
            rgbValue = hex(colorValue).strip('0x')
            rgb = rgbValue.rjust(8, "0")[0:6]

            status = self.getNodeStatus(node)
            first = node.knob('first').value()
            last = node.knob('last').value()
            allframe = last - first
            # project,act,eps,shot = self.getProjectAndEpsAndShot()
            ReadInfo = {
                "name":name,
                "file": path,
                "color":rgb,
                "status":status,
                "first": first,
                "last": last,
                "allframe":allframe
            }
            return ReadInfo


#更新场次信息，场次下面没有镜头的将会被删除*******************************************
    def UpdataEps(self,project):
        eps = self.getProjectEps(project)
        for i in range(len(eps)):
            if len(self.getEpsShot(project,eps[i]['eps.eps_name']))<1:
                projectDb = self.getProjectDatabase(project)
                t_info = self._t_tw.info_module(projectDb, 'eps')
                Epsdata = [["eps.eps_name","=",eps[i]['eps.eps_name']]]
                t_info.init_with_filter(Epsdata)
                t_info.delete()


    def updateShotFrame(self,project,eps,shot,startFrame,endFrame,allFrame,color,status):

        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "shot")
        filters = [['eps.eps_name','=',eps],
                ['shot.shot','=',shot]]
        t_info.init_with_filter(filters)
        fields = {"shot.first_frame":startFrame,"shot.last_frame":endFrame,"shot.frame":allFrame,"shot.color":'#'+color,"shot.status":status}
        t_info.set(fields)
        # return data


#得到缩略图**************************************************************
    def cutVideoImage_reAndTime(self,videoPath, fileName, time):#截取视频缩略图大图
        print 'ffmpeg open success:',videoPath
        videoPath = self.ChangeFilePath(videoPath).decode('utf-8').replace('"', '')
        fileName = self.ChangeFilePath(fileName).decode('utf-8').replace('"', '')
        # radio=self.getResolution(videoPath)
        # width = int(radio.split(':')[0])*40
        # height = int(radio.split(':')[1])*40
        # resolution = str(width)+'x'+str(height)
        # print resolution
        if os.path.exists(fileName):
            print 'already exist'
            return fileName.replace('"', '')
        
        # cmd = ffmpegPath + " -i " + "\"" + (videoPath) + "\"" + " -y " + " -ss " + str(time) \
              # + " -t 0.001 " + '-s '+str(resolution)+' '+ str(fileName)
        cmd = ffmpegPath + " -i " + "\"" + (videoPath) + "\"" + " -y " + " -ss " + str(time) \
              + " -t 0.001 " + str(fileName)
        cmd = cmd.encode(sys.getfilesystemencoding())
        if "?" in cmd:
            cmd = cmd.replace("?", "")
        subprocess.call(cmd, shell=True)


#得到缩略图，素材为图片的缩略图为素材本身**********************************************
    def getPicture(self,node,project,eps,shot):

        nodeInfo = self.getNodeInfo(node)
        filePath = nodeInfo['file']
        fileType = os.path.splitext(os.path.basename(filePath))[1].split('.')[1]
        filename = os.path.splitext(os.path.basename(filePath))[0].split('.')[0]
        print 'filename',filename
        if fileType in MOVE_SUFFIX:
            if os.path.exists(TempPath):
                tempPath = os.path.join(TempPath,filename+'.jpg').replace('\\', '/')
                if os.path.exists(tempPath):
                    return tempPath
                else:
                    time = (nodeInfo["allframe"] / 24) / 2
                    self.cutVideoImage_reAndTime(filePath, tempPath, time)
                    return tempPath
            else:
                os.makedirs(TempPath)
                tempPath_tex = tempPath = os.path.join(TempPath,filename+'.jpg').replace('\\', '/')
                time = (nodeInfo["allframe"] / 24) / 2
                self.cutVideoImage_reAndTime(filePath, tempPath_tex, time)
                return tempPath_tex
                
        elif fileType in JPG_SUFFIX:#图片截取
                imagePath = self.Seq_data(node)
                return imagePath
        else:
            print 'No Open:',fileType
      
#截取序列帧或者图片
    def Seq_data(self,node):
        '''
        info:imagePath = r"E:/NukeTask_test/TWE_ACT13_S032_ST0080/TWE_ACT13_S033_ST0080.01.tga"
        :return:
        '''
        info = self.getNukeNodes(node)
        path = self.ImageFormatTrans(info)
        return path

    def getNukeNodes(self,node):

        # for i in range(len(nodes)):
        #     if nodes[i].Class() == 'Read':
        path = node.knob('file').value()
        filetype = os.path.splitext(os.path.basename(path))[1].split('.')[1]
        dirname = os.path.dirname(path)
        if filetype in JPG_SUFFIX:
            cut_image_info = fllb.query(dirname, unSeqExts=MOVE_SUFFIX, sequencePattern='#.', getAllSubs=False)
            cut_image = cut_image_info[0]['paths'][len(cut_image_info[0]['paths']) / 2]
            return cut_image

    def ChangeFilePath(self,path):
        '整理路径'
        FilePath = ''
        if '/' in path:
            FilePath = path.split('/')
        elif '\\' in path:
            FilePath = path.replace('\\', '/')
            FilePath = FilePath.split('/')
        else:
            pass
        new_FilePath = "'"
        for length in range(len(FilePath)):
            if length == 0:
                new_FilePath = new_FilePath + '"' + FilePath[length] + "/"
            elif length == len(FilePath) - 1:
                new_FilePath = new_FilePath + FilePath[length] + '"' + "'"
            elif length != 0 and length != len(FilePath) - 1:
                new_FilePath = new_FilePath + FilePath[length] + '/'
        return new_FilePath.replace("'", "")

    def getExcelImage(self,path):#用来获取excel 的小图
        print 'path',path
        Filename = os.path.splitext(os.path.basename(path))[0].split('.')[0] + '_mix.jpg'
        img_path = os.path.join(TempPath, Filename).replace('\\', '/')

        image_Path = self.ChangeFilePath(path).decode('utf-8').replace('"', '')
        Saveimage = self.ChangeFilePath(img_path).decode('utf-8').replace('"', '')
        
        radio=self.getResolution(image_Path)
        width = int(radio.split(':')[0])*50
        height = int(radio.split(':')[1])*50
        resolution = str(width)+'x'+str(height)
        print resolution
        if os.path.exists(Saveimage):
            print 'already exist'
            return Saveimage.replace('"', '')
        cmd = ffmpegPath + ' -y -i ' + image_Path + ' -ac 1 -acodec libamr_nb' \
                                                    ' -ar 8000 -ab 12200 -s '+str(resolution)+' -b 128 -r 15 ' + Saveimage
        cmd = cmd.encode(sys.getfilesystemencoding())
        if "?" in cmd:
            cmd = cmd.replace("?", "")
        subprocess.call(cmd, shell=True)
        SavePath = Saveimage.replace('"', '')
        return SavePath
        
        
    def getResolution(self, filename):
        filename = filename.replace('"', '')
        command = [FFPROBE_PATH, "-loglevel", "quiet", "-print_format", "json", "-show_format", "-show_streams",
                   "-i",
                   filename]
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
        out = result.stdout.read()
        try:
            temp = str(out.decode('utf-8'))
        except:
            temp = str(out)
        print 'temp',temp
        try:
            # data = json.loads(temp)['streams'][1]['width']
            # data1 = json.loads(temp)['streams'][1]['height']
            radio =  json.loads(temp)['streams'][1]['display_aspect_ratio']
            
        except:
            # data = json.loads(temp)['streams'][0]['width']
            # data1 = json.loads(temp)['streams'][0]['height']
            radio =  json.loads(temp)['streams'][0]['display_aspect_ratio']
        return radio
        
    def ImageFormatTrans(self,FilePath):#FFmpeg 截取大图片缩略图
        
        Filename = os.path.splitext(os.path.basename(FilePath))[0].split('.')[0] + '.jpg'
        img_path = os.path.join(TempPath, Filename).replace('\\', '/')

        image_Path = self.ChangeFilePath(FilePath).decode('utf-8').replace('"', '')
        Saveimage = self.ChangeFilePath(img_path).decode('utf-8').replace('"', '')
        
        # radio=self.getResolution(image_Path)
        # width = int(radio.split(':')[0])*40
        # height = int(radio.split(':')[1])*40
        # resolution = str(width)+'x'+str(height)
        # print resolution
        if os.path.exists(Saveimage):
            print 'already exist'
            return Saveimage.replace('"', '')
        # cmd = ffmpegPath + ' -y -i ' + image_Path + ' -ac 1 -acodec libamr_nb' \
                                                    # ' -ar 8000 -ab 12200 -s '+str(resolution)+' -b 128 -r 15 ' + Saveimage
        cmd = ffmpegPath + ' -y -i ' + image_Path + ' -ac 1 -acodec libamr_nb' \
                                                     ' -ar 8000 -ab 12200 '+' -b 128 -r 15 ' + Saveimage
        cmd = cmd.encode(sys.getfilesystemencoding())
        if "?" in cmd:
            cmd = cmd.replace("?", "")
        subprocess.call(cmd, shell=True)
        SavePath = Saveimage.replace('"', '')
        return SavePath


#设置镜头缩略图*****************************************************
    def setshotImage(self,project,eps,shot,imagePath):
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb,'shot')
        filters = [['eps.eps_name','=',eps],
                ['shot.shot','=',shot]]
        t_info.init_with_filter(filters)
        t_info.set_image("shot.image", imagePath)

#得到镜头状态*****************************************************
    def getepsStatus(self,project,eps,shot):
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "shot")
        filters = [['eps.eps_name','=',eps],
                ['shot.shot','=',shot]]
        t_info.init_with_filter(filters)
        fields = ["shot.status"]
        data = t_info.get(fields)
        return data
#得到某个项目下面的所有场次*****************************************
    def epsShotInfo(self,project):

        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "shot")
        # filters = [['eps.eps_name','=','ACT1'],
        #            ['shot.shot','in',['S001','S031','S030','S032']]   #返回存在镜头的id
        #            ]

        filters = [['eps.eps_name','has','%']]
        t_info.init_with_filter(filters)
        data =  t_info.get(['eps.eps_name','shot.shot'])
        # data = t_info.get(['shot.shot'])
        return data

#得到某个镜头下面的镜头信息*********************************************
    def getshotFrame(self,project,eps,shot):
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "shot")
        filters = [['eps.eps_name','=',eps],
                ['shot.shot','=',shot]]
        t_info.init_with_filter(filters)
        fields = ["shot.first_frame",'shot.last_frame']
        data = t_info.get(fields)
        return data
#**********************************************************************
    def getshotInfo(self,project,epslist,shotlist):

        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "shot")
        filters = [['eps.eps_name','in',epslist],
                   ['shot.shot','in',shotlist]
                   ]
        t_info.init_with_filter(filters)
        data = t_info.get(['eps.eps_name','shot.shot','shot.first_frame','shot.last_frame','shot.status'])
        teamworkShotList = []
        dic = {}
        for i in range(len(data)):
            dic[data[i]['eps.eps_name']] = data[i]['shot.shot']
            teamworkShotList.append(dic)
            dic = {}
        return data,teamworkShotList


    def getStatusAndColor(self):
        data = self._t_tw.sys().get_status_and_color()
        return data

    def setshotStatus(self,project,eps,shot,status,color):
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb,"shot")
        filters = [
            ['eps.eps_name', '=', eps],
            ['shot.shot', '=', shot],
        ]
        t_info.init_with_filter(filters)

        dict = {'shot.status': status,'shot.color':'#'+color}
        t_info.set(dict)

    def getShotId(self,project,eps,shot):
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, 'shot')
        filters = [
            ["shot.eps_name", '=', eps],
            ["shot.shot", '=', shot]
        ]
        t_info.init_with_filter(filters)  # 过滤器
        fields = []  # 查询的内容
        # 作者 模块 任务名称  阶段
        data = t_info.get(fields)
        print data
        return data



    def Send_cgtwNote(self,m_database,m_id):

        '''
        :param m_database: 获取项目的数据库 如: proj_csj
        :param m_id: 获取对应 条目的id 号:
        projectDb = self.getProjectDatabase()
        t_info = self.t_tw.info_module(projectDb, 'shot')

        filters = [
            ["shot.eps_name", '=', 'ACT2'],
            ["shot.shot", '=', 'S031']
        ]
        t_info.init_with_filter(filters)  # 过滤器
        fields = []  # 查询的内容
        # 作者 模块 任务名称  阶段
        data = t_info.get(fields)
        如 [{'id': u'0DC0AEAB-575B-6548-7287-6B0646070A79'}]
        :return:
        '''
        # app = QtGui.QApplication.instance()
        webview = QWebEngineView()
        m_token = self._t_tw.sys().get_token()
        m_ip = str(self._t_tw.sys().get_server_ip()) #如果是内网 则不要加入端口号，如果是外网需要加入+':10003'

        m_module = self._t_tw.info_module(m_database, 'shot').get_module()
        web_data ="http://" + str(m_ip) + "/index.php?controller=v_thirdpath_soft&method=show_page&db=" + str(
                m_database) + "&module=" + str(m_module) + "&module_type=info&theme=maya&lang=zh&task_id=" + str(
                m_id) + "&widget=note_widget&token=" + str(m_token) + "&is_qt=y"

        if  web_data:
            if web_data.find('://') == -1:
                web_data = 'http://' + web_data
            url = QtCore.QUrl(web_data)
            webview.load(url)
            webview.show()
            q = QtCore.QEventLoop()
            q.exec_()
        # if  web_data:
            # if web_data.find('://') == -1:
                # web_data = 'http://' + web_data
            # url = QtCore.QUrl(web_data)
            # webview.load(url)
            # webview.show()
            # q = QtCore.QEventLoop()
            # q.exec_()
            # app.exec_()



# if __name__ =="__main__":
    # Shot = CreateShots()
    # print Shot.getShotId('TWE','ACT2','S031')
    # print Shot.getshotFrame("TWE",'ACT1','S032')
    # Shot.SelectReadCreateShot()
    #Shot.SelectBackdropCreateShot()
    # Shot.epsShotInfo('TWE')
    # Shot.updateShotFrame("TWE",'ACT2','S030',1,2)
