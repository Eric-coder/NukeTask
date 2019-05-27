#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import nuke
sys.path.append(r"C:\cgteamwork\bin\lib\pyside")
sys.path.append(r"C:\cgteamwork\bin\base")
SERVER_DI="to.xm.cgteamwork.com:1003"

'''请注意命名的冲突'''
class CreateTask():
    def __init__(self):
        import cgtw
        import cgtw2
        try:
            self._t_tw = cgtw.tw()
            self._t_tw2 = cgtw2.tw()#cgtw2 api 用来获取 a_flow_id
        except:
            nuke.message('Please open CGteamwork')
            return False
    def getProjectDatabase(self,project):
        t_info = self._t_tw.info_module("public", "project")
        filters = [
            ["project.code", "=", project],
        ]
        t_info.init_with_filter(filters)
        fields = ["project.database"]
        database = t_info.get(fields)[0]['project.database']
        return database

    # 创建eps场次号(如果存在则忽略)************************************
    def Create_eps(self, project, eps):
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
        Create_data = {"eps.eps_name": eps}
        if Create_data['eps.eps_name'] not in eps_List:
            t_info.create(Create_data)
            return True
        else:
            return False

# 得到eps场次名称******************************************
    def getProjectEps(self, project):
        eps_List = []
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "eps")
        filters = []
        t_info.init_with_filter(filters)
        fields = ["eps.eps_name"]
        data = t_info.get(fields)
        for i in range(len(data)):
            eps_List.append(data[i]['eps.eps_name'])
        return eps_List

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

    def createShotTask(self,project,eps,shot,act,pipeline_id,pipeline_name):
        print eps,shot,act#改
        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb,'shot')
        if act:
            filters = [['eps.eps_name','=',eps],
                    ['shot.shot','=',shot]
                    ['eps.act','=',act] #GAI
                    ]
        else:
            filters = [['eps.eps_name','=',eps],
                    ['shot.shot','=',shot]
                    # ['eps.act','=',act] #GAI
                    ]
        t_info.init_with_filter(filters)
        join_id = t_info.get_id_list()
        t_task_info = self._t_tw.task_module(projectDb, "shot")
        t_task_info.init_with_filter(filters)
        
        t_pipeline_id_list =  self._t_tw2.pipeline.get_id(projectDb, [['entity_name', '=', pipeline_name], 'and', ['module', '=', 'shot'],'and',['module_type', '=', 'task']])
        t_flow_list  =  self._t_tw2.flow.get_data(projectDb, t_pipeline_id_list)
        t_flow_id    =  t_flow_list[0]['flow_id']

        t_task_info.create_task(join_id[0],pipeline_id,pipeline_name,a_flow_id=t_flow_id, a_task_name="")


    def setShotTask(self,project,eps,shot,act,pipeline_name,artist_name,status = '',description = ''):
    
        projectDb = self.getProjectDatabase(project)
        t_task_info = self._t_tw.task_module(projectDb,"shot")
        if act:
            filters = [['eps.eps_name','=',eps],
                    ['shot.shot','=',shot],
                    # ['eps.act','=',act],#GAI
                    ['task.pipeline','=',pipeline_name]]
        else:
            filters = [['eps.eps_name','=',eps],
                    ['shot.shot','=',shot],
                    ['eps.act','=',act],#GAI
                    ['task.pipeline','=',pipeline_name]]
                    
        t_task_info.init_with_filter(filters)
        t_task_info.set({'task.artist':artist_name,'task.status':status,'task.dddd':description})#
        id = t_task_info.get(['task.id'])

        self.Send_Message(projectDb,id,eps,shot,pipeline_name,artist_name,description = description )
        self.MergeNote(projectDb,eps,shot)
        
    def getArtistId(self,artist):
        t_info = self._t_tw.info_module("public",'account')
        filters = [
        ['account.name','=',artist]
        ]
        t_info.init_with_filter(filters)

        # data = t_info.get(['account.name','account.project_permission','account.group','account.department'])
        data = t_info.get(['account.id'])
        name_id = []
        name_id.append(data[0]['account.id'])
        return name_id
        
    def Send_Message(self,database,id,eps,shot,pipeline_name,artist_name,description = ''):
        projectDb = database
        model = 'shot'
        model_type = 'task'
        account_id_list =self.getArtistId(artist_name)
        task_id = id[0]['id']
        message = str(eps + ' ' + shot + ' ' + pipeline_name + '     ' + ':'+description + ' ' + '\n'+ 'Assign to ' + artist_name )
        print projectDb,model,model_type,task_id,account_id_list
        self._t_tw.con()._send("c_msg","send_link_task", {"db":projectDb, "module":model, "module_type":model_type, "task_id": task_id,  "content":message, "account_id_array":account_id_list,'is_show_info_data':True})
        
    def getPipelineName(self,project):
        projectDb = self.getProjectDatabase(project)
        t_task_info = self._t_tw.pipeline(projectDb)
        pipelineList = t_task_info.get_with_module('shot',['name','#id'])

        return pipelineList
        # filters = []
        # t_task_info.init_with_filter(filters)
        # data = t_task_info.get(["task.pipeline"])
        # return data

    def getshotInfo(self,project,epsLis,shotLis):

        projectDb = self.getProjectDatabase(project)
        t_info = self._t_tw.info_module(projectDb, "shot")
        filters = [['eps.eps_name','in',epsLis],
                   ['shot.shot','in',shotLis]
                   ]
        t_info.init_with_filter(filters)
        data = t_info.get(['eps.eps_name','shot.shot'])

        return data

    def getArtistName(self):

        t_info = self._t_tw.info_module("public",'account')

        filters = [['account.name','has','%']]
        t_info.init_with_filter(filters)

        # data = t_info.get(['account.name','account.project_permission','account.group','account.department'])
        data = t_info.get(['account.name'])
        name = []
        for i in range(len(data)):
            name.append(data[i]['account.name'])
        return name

    def MergeNote(self,database,eps,shot):#合并任务模块的描述统计到镜头描述
        t_task = self._t_tw.task_module(database, "shot")
        filters = [['eps.eps_name','=',eps],
                   ['shot.shot','=',shot]
                   ]
        t_task.init_with_filter(filters)
        data_note = t_task.get(['task.dddd'])
        string = ''
        for data in data_note:
            string += data['task.dddd']
            string +=' '

        t_info = self._t_tw.info_module(database, "shot")
        t_info.init_with_filter(filters)
        t_info.set({'shot.vfx_note': string})



# if __name__ == '__main__':
    # Shot = CreateTask()
    # Shot.setShotTask("TWE","ACT2",'S030',"efx",'wadfgfdgr','11')

    # pipelineNameLis = []
    # pipelineNameDic = {}
    # for i in range(len(pipelineName)):
    #     pipelineNameDic.update({pipelineName[i]['name']: pipelineName[i]['id']})
    #     pipelineNameLis.append(pipelineName[i]['name'])
    # print pipelineNameDic,pipelineNameLis
    # Shot.createShotTask("TWE", "ACT1", "S031",'01F99FCE-3407-E541-E14C-DE4BD9D17AB7','animation')
    # Shot.setShotTask("TWE", "ACT1", "S032","animation","123456")
    #TWE ACT1 S031 01F99FCE-3407-E541-E14C-DE4BD9D17AB7 animation
    # data = Shot.setShotTask("TWE", "ACT1", "S032","animation")

    # print unicode(data[0]['task.artist'])

    print '----------------------------------------------------'