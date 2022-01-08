# 折腾
> 问题是这样的，因为`docker`中的操作无法获取到，而且`伪proc`的信息也并不能展示全，且各种工具的很多，因此十分不可控，因此打算把所有的内部命令外部命令的入口统一成`busybox`，所有的命令都是`busybox`的参数能够提取到。

好处：
1. 入口单一，可以全量控制
2. 定制化的tools，尽在掌握
3. 除非自己上传或者提供shell，否则很难绕过监控 

然而问题就出来了：
1. 启动服务需要用到`java`这样的命令，`busybox`如何能执行？
2. 怎样能在通过`dockerfile`构建镜像的时候替换掉执行入口

## 命令入口
`busybox`的命令入口相当有意思，这涉及到`busybox`本身的使用方式：
1. `busybox wget`这样直接跟着命令
2. `cp busybox wget`，`wget`这样重命名执行
3. `ln -s busybox wget`这样软链接执行

上面三种方式都是能够执行到`busybox`提供的`wget`的，在`busybox`中有很多`程序入口`这些是诸如`wget`真正的入口，一般是`wget_main`，然而对于`busybox`来说，入口只有一个就是`libbb/appletlib`下面的`main`函数
```
int main(int argc UNUSED_PARAM, char **argv)
```
对于第一种执行方式，`argv[0]=busybox argv[1]=wget`
而对于二三种则是`argv[0]=wget`，所有的信息都是字符串数组，而最终经过处理的信息，都会以`run_applet_and_exit`这个函数收尾。
因此可以这么用这个入口，把所有的信息打印出来。
> 就写在`run_applet_and_exit`上面，因为这时候所有的数据都是处理完的。

```
   for(int cmd=0;cmd<string_array_len(argv);cmd++){
        printf("Command[%d]=%s\n",cmd, argv[cmd]);
    }
```
但是新的问题就是出来了，就是`sh`这种交互式命令，它利用的是系统本身的环境变量，因此能够解决上述的问题，就是可以调用`java`
> 但是事实上`busybox`是不提供`sh`和`bash`的，其实这些都是`ash`(默认)

```
 if (login_sh) {
  const char *hp;

  state = 1;
  read_profile("/etc/profile");
 state1:
  state = 2;
  hp = lookupvar("HOME");
  if (hp)
   read_profile("$HOME/.profile");
 }
```
而在交互式过程中的命令状态，通过`lineedit`的`save_history`函数来记录，而如果启用了退出时记录的话，则还有另一种解决参数的方式：
```
1. static void save_history(char *str)  //交互式过程记录
2. void save_history(line_input_t *st)  //推出shell时记录
```
这些可以通过写入文件测试一下
```
   FILE *cmdline = NULL;
   fp = fopen("/tmp/cmdline", "w+");
   fputs("This is testing for fputs...\n",cmdline);
   fclose(cmdline);
```
那简单的方式就是：
1. 构建镜像时将`login shell`指定。
2. 构建docker时在最后把所有的内置`binary`替换掉。
3. 最后的传输方案使用`Filebeat`。

然后需要缩减`busybox`的工具，就需要在`make menuconfig`时候把非常多的选项给取消掉，当然还有更为重要的一点就是静态编译，此点可以直接防御`动态链接库劫持`。

## Filebeat
这个工具非常的不错，无缝衔接`kafka`，`logstash`或者是`es`。
配置上也十分简单：
```
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/*.log
      #json:
      # keys_under_root: true
      # add_error_key: true
      # message_key: log
```
这是`input`部分，指定`log`文件，如果是`json`格式的数据就把下面那个`#`部分给取消注释，其中`message_key`就是你的`json`数据的某个`key`
输出部分的话我是直接连接的`kafka`，配置起来贼简单，我是带`sals`认证的，如果没有的话把`username`和`password`取消掉就好了：
```
output.kafka:
  enabled: true
  # The kafka hosts
  hosts: ["localhost:9092","localhost2:9092"]
  topic: Topicname
  username: "username"
  password: "password" 
```
启动的话
```
./filebeat -c filebeat.yml
```

## `busybox`直连`kafka`的问题
> 没想到这才是真正的坑

事情是这样的，用`filebeat`虽然达成了目的，但是却引入了两个新的问题:
1. `kafka`的认证帐号密码泄露
2. `filebeat`的进程`保活`问题(虽然`保活`这个词被疯狂吐槽)

用`supervisor`其实可以解决第二个问题，但是呢因为某些原因，此方法暂时不被考虑，那么就只能想办法换个思路了，就是用`c`程序直连`kafka`。
这就引入了[librdkafka](https://github.com/edenhill/librdkafka)这一个三方的`C库`。
先看下`librdkafka`的坑点：
```
./configure
make
sudo make install
```
当执行完三条命令后，就装好了一个`librdkafka`，然而问题是什么呢？是`.so`还有`.a`都被装到的是`/usr/local/lib/`下面，因此此时可以执行`cp`命令把他们全都拷贝过去。
```
sudo cp -r /usr/local/lib /usr/lib/
```
后面就是把一个`simple-producer`的函数实现写入`busybox`当中。可以自己写个头文件，然后再`include解决`，但是当时认识还不深，不敢乱弄怕破坏编译时候的结构关系，就选择直接把函数写入到`lineedit.c`中，这样的话连头文件都不需要了，直接调用函数就是了，参照给出来的`example`就行，适当改一下函数入口，只需要接收`char *message`即可。

本来到这我以为会很顺利的，然而问题就来了，就是静态编译时候产生的问题。
## 缺少大量的`静态链接库`
> `静态编译`是需要`静态链接库`的，一个`静态链接库`的制作就是针对`.o`的打包。

因为`busybox`选取的编译方式是`静态编译`，所以在引入`librdkafka`时候大量报错，大概都是如下错误，这是因为没有`静态链接库`导致找到不到函数符号。
```
undefined reference to 'xxxxx'
```
就以`-lssl`为例子，这是`libssl`的缩写，那么就应该是`openssl`的`c库`，其中这儿要注意和系统的`openssl`版本对应。
```
官方下载`openssl`
./config -fPIC no-shared
make
```
就可以找到`libcrypto.a`和`libssl.a`文件，把这两个文件放到`/usr/lib/`中即可。
当然还有一种就是比如`llz4`也就是`liblz4`，这个可以到编译好的`librdkafka`的`src`目录下('src-cpp'是`c++`)，可以看到有个`lz4.o`文件：
```
ar rcs -o liblz4.a lz4.o
```
这样就获得了一个`liblz4`的`静态链接库`。
把所有的`静态链接库`都整齐了，就需要修改`busybox`的`Makefile`。编译`librdkafka`的二进制程序需要加上参数`-lrdkafka -lz -lpthread -lrt`代表要用上这些`C库`，然而静态编译时候就需要更多了
```
-lrdkafka -lzstd -llz4 -lssl -lcrypto -lsasl2 -lz -lpthread -ldl -lm
```
这是一次`静态编译`所需要引用到的全部库把如上参数填写到`Makefile`的`LDLIBS`中
```
#本来的样子是这样的
#LDLIBS := 
LDLIBS := -lrdkafka -lzstd -llz4 -lssl -lcrypto -lsasl2 -lz -lpthread -ldl -lm
```
这时候再编译`busybox`就能顺利`make`成功了。
然而`make`成功并不代表可以运行成功。

## `gethostbyname`带来的巨大问题
如果你有仔细注意的话，在`make`时候会产生几个`warning`，大概内容是这样的：
```
b_sock.c:(.text+0x71): warning：Using 'gethostbyname' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
```
这个函数是`glibc`的`NSS`层，为了灵活性，他实际上可以说是强制链接到`动态链接库`的，这也就导致了程序在编译上是没有问题的，但是在真正运行的时候，当这些函数中传入了域名，便会发生`段错误`，这点我在`gdb`中观察过，十分的难受，然而`busybox`如果想任意移植，就必须保持`静态编译`。

那就只能完全重写`librdkafka`中有问题的函数：`getaddrinfo`，`freeaddrinfo`
全局`grep下`大概就定位到了相关的两个文件:`rdaddr.c`和`rdaddr.h`。按照nslookup在静态编译的busybox上如何正常解析域名](https://blog.csdn.net/prog_6103/article/details/78569510)中提供一个重写出来的头文件，直接在`rdaddr.c`的`#include "rdaddr.h"`下添加`#include "getaddrinfo.h"`。
先把`getaddrinfo.h`稍微改一下，大概就是改了两个函数的定义：
```
int getaddrinfo_re(const char *hostname, const char *service, const struct addrinfo *hints, struct addrinfo **res) { }
void freeaddrinfo_re(struct addrinfo *res) { }
```
这样改是为了方便调用，也不需要再`#define`了，直接把`rdaddr.c`中的两个函数给改成上述的两个：
```
169 if ((r = getaddrinfo_re(node, defsvc, &hints, &ais))) {
193 freeaddrinfo_re(ais);
206 freeaddrinfo_re(ais);
```
然后还有一个问题就是端口问题，原文件没有把传入的`端口`提取出来，因此在`return rsal;`前添加：
```
rsal->rsal_addr->in.sin_port = htons((atoi(defsvc)));
```
这样才能向我们指定的端口发送数据，不然都是`0`，改完后重新编译`librdkafka`生成`静态链接库`，然后再去编译`busybox`，此刻报错也无所谓了，因为已经能成功把数据上报到指定的`kafka`了。
 
# 参考资料
* [浅析busybox查找命令和调用相应命令函数的实现流程框架](https://blog.csdn.net/sfrysh/article/details/43679189)
* [BusyBox原理简单分析](https://www.cnblogs.com/sunyubo/archive/2010/08/04/2708294.html)
* [跟文件系统（二）busybox构建跟文件系统](http://www.lujun.org.cn/?p=3574)
* [Linux下librdkafka客户端的编译运行](https://www.cnblogs.com/vincent-vg/p/5855924.html)
* [librdkafka](https://docs.confluent.io/2.0.0/clients/librdkafka/rdkafka_8h)
* [gethostbyname报错问题](https://www.phpfans.net/ask/fansa1/1970772288.html)
* [如何解决编译一个静态二进制代码包括一个函数gethostbyname](http://zgserver.com/gethostbyname-2.html)
* [gcc同时使用动态和静态链接](https://flowaters.iteye.com/blog/2346234)
* [nslookup在静态编译的busybox上如何正常解析域名](https://blog.csdn.net/prog_6103/article/details/78569510)