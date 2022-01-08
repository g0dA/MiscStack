环境：
1. PC
2. HOST1
3. HOST2

# 密钥对生成
PC上执行：
```
ssh-keygen -t rsa -C "user"
```
在填写`Enter file in which to save the key (/home/user/.ssh/id_rsa):`时候可以改一下最终生成的`密钥名`，比如是`id_rsa_user`

把`.ssh/id_rsa_user.pub`拷贝到`HOST1`和`HOST2`的`.ssh/authorized_keys`中。
登录时执行：
```
ssh -i .ssh/id_rsa_user user@HOST1
ssh -i .ssh/id_rsa_user user@HOST2
```
这样就能免密登录。
如果想`PC`登录到`HOST1`再直接登录到`HOST2`上，就需要用到一个转发。
这是因为`ssh`的认证通道主要是`SSH_AUTH_SOCK`，修改掉就行。
利用`ssh-agent`，首先后台运行`ssh-agent`：
```
eval `ssh-agent`
```
添加需要代理的`私钥`
```
ssh-add .ssh/id_rsa_user
```
登录`HOST1`时添加一个`验证代理转发`
```
ssh -A user@HOST1
```
接着在`HOST1`上执行
```
ssh user@HOST2
```
这样可以直接登录上去。
关于查看和清空代理的私钥：
```
ssh-add -l //查看所有私钥
ssh-add -L //查看所有私钥对应的公钥
ssh-add -d .ssh/id_rsa_user
ssh-add -D //清空所有的
```
关于`ssh-agent`关闭
```
ssh-add -k
```
再记录下配合pam_radius的双因素认证：
虽然可以通过认证登录，但是也能直接主机登录，所以后面还得限制下。
以centos为例：
Step.1:
```
$ sudo yum install gcc pam pam-devel make -y
```
主要安装为pam-devel环境，否则以后编译步骤会缺少头文件
 
Step.2:
到freeradius官网下载最新的pam_radius模块:http://freeradius.org/sub_projects/，其中Sub_projects选择为PAM_RADIUS
```
$ wget https://github.com/FreeRADIUS/pam_radius/archive/release_1_4_0.tar.gz
$ tar xvf release_1_4_0.tar.gz
$ cd pam_radius-release_1_4_0
$ sudo ./configure
$ sudo make
```
Step.3:
```
$ vi pam_radius_auth.conf 
```
修改#server[: port]  shared_secret   timeout (s)下面的内容为：
```
server:port    secret    3
#other-server    other-secret    3
```
Step.4:
```
$ sudo cp pam_radius_auth.so /lib64/security/
如果是32位则是/lib/security/
$ sudo mkdir /etc/raddb
$ sudo cp pam_radius_auth.conf /etc/raddb/server
```
 
Step.5:
```
$ sudo vi /etc/pam.d/sshd
```
修改成如下内容：
```
#%PAM-1.0
auth required pam_sepermit.so
auth sufficient pam_radius_auth.so
auth include password-auth
#auth substack password-auth
auth include postlogin
# Used with polkit to reauthorize users in remote sessions
-auth optional pam_reauthorize.so prepare
account required pam_nologin.so
account include password-auth
password include password-auth
# pam_selinux.so close should be the first session rule
session required pam_selinux.so close
session required pam_loginuid.so
# pam_selinux.so open should only be followed by sessions to be executed in the user context
session required pam_selinux.so open env_params
session required pam_namespace.so
session optional pam_keyinit.so force revoke
session include password-auth
session include postlogin
# Used with polkit to reauthorize users in remote sessions
-session optional pam_reauthorize.so prepare
```
Step.6:
```
$ sudo vi /etc/ssh/sshd_config
```
修改其中的两个缺省值：
```
ChallengeResponseAuthentication yes
#ChallengeResponseAuthentication no
```
```
#UsePAM no
UsePAM yes
```
Step.7:
极为重要！！
radius中的用户必须要和/etc/passwd中的用户同步，即都存在。例如用户：test，用户组用apps，可以用其他的
```
$ sudo useradd -g apps -d /home/test test
```
 Step.8:
重启sshd服务
```
$ sudo systemctl restart sshd
```

# 参考资料
* [SSH开启key-agent转发进行跳板登陆 ](http://blog.sina.com.cn/s/blog_4da051a60102vple.html)
* [了解ssh代理](http://www.zsythink.net/archives/2407/)
* [ssh转发代理：ssh-agent用法详解](https://www.cnblogs.com/f-ck-need-u/p/10484531.html)
* [linux 基于ssh创建跳板机](https://www.jianshu.com/p/5fe9152fe78d)
* [PAM RADIUS Installation and Configuration Guide](https://docs.secureauth.com/display/81docs/PAM+RADIUS+Installation+and+Configuration+Guide#tab-RedHat+%2F+CentOS)
* [linux pam安全认证模块su命令的安全隐患](https://idc.wanyunshuju.com/li/134.html)