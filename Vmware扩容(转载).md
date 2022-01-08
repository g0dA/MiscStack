> 特别好，记录下


* [原文https://www.linuxidc.com/Linux/2019-04/158346.htm](https://www.linuxidc.com/Linux/2019-04/158346.htm)


在有些时候，自己或者公司开的虚拟机的磁盘在一开始的时候没规划好，或者有磁盘扩容的需求（其实在系统日常运维的时候这个需求时常出现），那么这个时候又该怎么处理呢，前几天刚好遇到了这个需要，所以也借此机会将整个磁盘扩容的过程步骤记录一下，以防以后再次出现同样的需求，并给读者作为参考。


一、环境
虚拟机软件：VMware 14
系统版本：CentOS 7


二、扩容步骤
1、VM上修改磁盘信息
将虚拟机关机，然后点击VM顶部菜单栏中的显示或隐藏控制台视图按钮来显示已建立的虚拟机的配置信息


![3635aed8-0749-4e3e-b319-7b3cf275cf18.png](Vmware扩容(转载)_files/3635aed8-0749-4e3e-b319-7b3cf275cf18.png)


然后左边菜单栏点击硬盘，在弹出的对话框选中硬盘，并点击扩展按钮，然后在弹出框中的最大磁盘大小修改未所需要的磁盘大小，比如我现在需要扩容30G，原本的磁盘大小是20G，所以我这里将原本的20G修改成50G，然后点击扩展


![55eb1bff-eb6e-4b22-9ba0-8c65235b8f0e.png](Vmware扩容(转载)_files/55eb1bff-eb6e-4b22-9ba0-8c65235b8f0e.png)


之后会收到提示：


![8986f286-ad0b-4a8e-9ecc-edeaea23d210.png](Vmware扩容(转载)_files/8986f286-ad0b-4a8e-9ecc-edeaea23d210.png)


然后开启虚拟机，对磁盘进行进一步的配置


2、在系统中挂载磁盘
开启虚拟机并登录后，使用命令查看当磁盘状态
```
#df -h
```


![682e01a8-ae9a-4cd2-93a2-c6629ee1d54d.png](Vmware扩容(转载)_files/682e01a8-ae9a-4cd2-93a2-c6629ee1d54d.png)


可看到当前还是原本的20G，并未扩容
首先先通过命令查看到新磁盘的分区
```
#ls /dev/
```


![44538344-ea59-4c71-ae45-7e7585d978c1.png](Vmware扩容(转载)_files/44538344-ea59-4c71-ae45-7e7585d978c1.png)


或者使用
```
#fdisk -l
```


![a92f1054-07e1-49cc-a27d-02ec1aff00a7.png](Vmware扩容(转载)_files/a92f1054-07e1-49cc-a27d-02ec1aff00a7.png)


然后对新加的磁盘进行分区操作：
```
#fdisk /dev/sda
```


![b5c1b2d8-30b2-4be0-8aff-d541a06dc980.png](Vmware扩容(转载)_files/b5c1b2d8-30b2-4be0-8aff-d541a06dc980.png)


![3449d140-09e4-4fad-b52c-a7349dafecb3.png](Vmware扩容(转载)_files/3449d140-09e4-4fad-b52c-a7349dafecb3.png)


期间，如果需要将分区类型的Linux修改为Linux LVM的话需要在新增了分区之后，选择t，然后选择8e，之后可以将新的分区修改为linux LVM
之后我们可以再次用以下命令查看到磁盘当前情况
```
# fdisk -l
```


![a8e3ef64-f077-4fbb-b652-25bac3268766.png](Vmware扩容(转载)_files/a8e3ef64-f077-4fbb-b652-25bac3268766.png)


重启虚拟机格式化新建分区
```
# reboot
```
然后将新添加的分区添加到已有的组实现扩容
首先查看卷组名
```
# vgdisplay
```


![cba7b211-1871-4bd6-a16c-81a9a5aae76d.png](Vmware扩容(转载)_files/cba7b211-1871-4bd6-a16c-81a9a5aae76d.png)


初始化刚刚的分区
```
# pvcreate /dev/sda3
```


![113f0d87-f2fa-45d9-9e5a-ca9fd12428bf.png](Vmware扩容(转载)_files/113f0d87-f2fa-45d9-9e5a-ca9fd12428bf.png)


将初始化过的分区加入到虚拟卷组名
```
# vgextend 虚拟卷组名 新增的分区
# vgextend centos /dev/sda3
```


![497f6df5-1d95-4fb1-8af6-94185652791d.png](Vmware扩容(转载)_files/497f6df5-1d95-4fb1-8af6-94185652791d.png)


再次查看卷组情况
```
# vgdisplay
```


![56085af0-8666-4e88-aed8-80e4154ae246.png](Vmware扩容(转载)_files/56085af0-8666-4e88-aed8-80e4154ae246.png)


这里可以看到，有30G的空间是空闲的
查看当前磁盘情况并记下需要扩展的文件系统名，我这里因为要扩展根目录，所以我记下的是 /dev/mapper/centos-root
```
# df -h
```


![3e0a9e07-409b-4fe5-bd68-43bba718a9b6.png](Vmware扩容(转载)_files/3e0a9e07-409b-4fe5-bd68-43bba718a9b6.png)


扩容已有的卷组容量（这里有个细节，就是不能全扩展满，比如空闲空间是30G，然后这里的话30G不能全扩展上，这里我扩展的是29G）
```
# lvextend -L +需要扩展的容量 需要扩展的文件系统名 
# lvextend -L +29G /dev/mapper/centos-root
```


![148f8723-a71d-4c78-a2a0-764c5e6001c5.png](Vmware扩容(转载)_files/148f8723-a71d-4c78-a2a0-764c5e6001c5.png)


然后我们用命令查看当前卷组
```
# pvdisplay
```


![cf33ba57-8101-4919-ab1a-6bcc80146855.png](Vmware扩容(转载)_files/cf33ba57-8101-4919-ab1a-6bcc80146855.png)


这里可以看到，卷组已经扩容了
以上只是卷的扩容，然后我们需要将文件系统扩容
```
# resize2fs 文件系统名
# resize2fs /dev/mapper/centos-root
```
这个是网上很多参考资料的用法，但是在这里报错了


![3b1e6dd1-0029-4e34-a95d-b65063516ebb.png](Vmware扩容(转载)_files/3b1e6dd1-0029-4e34-a95d-b65063516ebb.png)


解决办法是，首先查看文件系统的格式
```
# cat /etc/fstab | grep centos-root
```


![c274cb4c-0a3f-4331-971d-ce38fc5bfb8a.png](Vmware扩容(转载)_files/c274cb4c-0a3f-4331-971d-ce38fc5bfb8a.png)


这里可以看到，文件系统是xfs，所以需要xfs的命令来扩展磁盘空间
```
# xfs_growfs 文件系统名
# xfs_growfs /dev/mapper/centos-root
```


![7dfaf9d6-e1ef-4eb7-ae74-e748dab54795.png](Vmware扩容(转载)_files/7dfaf9d6-e1ef-4eb7-ae74-e748dab54795.png)


之后我们再次用命令查看磁盘状态
```
# df -h
```


![d6b4fdb1-e786-4715-9f8e-32e66df1331c.png](Vmware扩容(转载)_files/d6b4fdb1-e786-4715-9f8e-32e66df1331c.png)


