# 目的
> 就是一个跳板机，想记录下所有通过跳板机登录服务器操作的命令。

架构的话如下：
```
PC ---ssh------------sshd---- 跳板机 ---ssh-----------sshd------ 服务器
```
可控的部分是跳板机的`sshd`和`ssh`。
不过不知道跳板机这边的`ssh`到底是个什么情况，是直接透传前一个`ssh`的流量还是又产生新的直连，还得探索下。

# Channel
Openssh是ssh的一个开源实现，其中关于ssh的数据通道，用的是Channel，这是一个加密的Tunnels。在任意的节点，当需要发起新的ssh传输是都可以打开一个Channel，每一个channel都有一个唯一数字标识。
Openssh中的Channel模块的数据结构及接口都声明于channels.h，实现于channels.c。
# Server & Client
这部分是Openssh的两个模块，分别为sshd和ssh，具体的实现分别在两份代码中：
serverloop.c
clientloop.c

# 实现
这边想法就比较简单了，就是把进入Channels的I/O记录下来打印出来就行。但是这儿也有两种，就是fd和input/output的，fd更接近原来的，所以我选择fd。
shell的录屏是server端通过channels把数据传给client端的，相对的fd是rfd，即和当前 Channel 关联的输入部分，处理函数是：
`channel_handle_rfd(struct ssh *ssh, Channel *c, fd_set *readset, fd_set *writeset)`
掏数据的话：
```
}else if ((r = sshbuf_put(c->input, buf, len)) != 0) { 
        fatal("%s: channel %d: put data: %s", __func__,
                c->self, ssh_err(r));
}
```
这儿就会把buf中的数据put到c->input里，而buf就是会在客户端显示的数据。

同样的，如果要记录的是操作命令的话，就可以记录`wfd`的数据，这是传入`do_execve`之前的，还能拦截。