# NukeTask
工具说明：
    在CG软件中，基于流程管理软件cgteamwork，使用nuke对制作人员分配任务，以及创建镜头等操作
    
使用说明：
    1：Nuke中通过backdrop框进行层级分化，用户通过填写对应阶段的项目名，场次，集数等信息，进行录入
    2：支持批量导出EXCel表格，记录详细信息
    3: 创建完成镜头后，可以激活创建任务选项，可以对任务进行分配。

创建镜头阶段：
选中镜头序列帧或mov视频，如上:文件名为 pipeline_S031_ST003,文件名的分割符为下划线_ 所以在工具界面上请输入分隔符 栏填写 下划线 后按下回车如下:
![image](https://github.com/WangTianX/NukeTask/blob/master/image/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20190527212017.png)
![image](https://github.com/WangTianX/NukeTask/blob/master/image/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20190527212042.png)
如上创建镜头后，对应cgteamwork就有对应的镜头信息如下：
![image](https://github.com/WangTianX/NukeTask/blob/master/image/_20190527212124.png)

创建任务：
当镜头创建完成后，可以通过工具进行任务的创建，与分配。首先说明创建任务是根据nuke backdropNode层级创建的如图:
![image](https://github.com/WangTianX/NukeTask/blob/master/image/_20190527213158.png)
第一层级的 backdrop 为S031 第二层为 comp 第三层为 王天翔 第四层为抠像
![image](https://github.com/WangTianX/NukeTask/blob/master/image/_20190527213239.png)
