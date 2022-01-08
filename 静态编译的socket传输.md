> 最近工作中遇到一个小需求，就是向一个接口发送一个携带自定义`header`的`GET`请求，用linux c写。

如果是动态编译下实际很简单，想法就是写一个socket，然后手动构建一个`HTTP GET`请求头，然后`send`过去即可，然而再实际编写时却出了问题，就是静态编译时对于域名的处理。

对于`GET`请求我找了一个轮子：[httpclient.c](https://github.com/phisonk/lab4/blob/d020e8be5d93236367fc9ff367685733cec59121/socket-c-master/httpclient.c)，这个轮子比较好的达到了我的基础需求，但是在静态编译时候，报了警告：
```
/usr/bin/ld: /tmp/cc8wgsyL.o: in function `getHostInfo':
httpclient.c:(.text+0x108d): 警告：Using 'getaddrinfo' in statically linked applications requires at runtime the shared libraries from the glibc version used for linking
```
因为是个告警，我并不是很在意，然后就直接运行试试：
```
$ ./producer www.baidu.com 80 sdsad  
[1] 23534 segmentation fault (core dumped) ./producer www.baidu.com 80 sdsad
```
出现了`段错误`，猜测应该是`空指针`导致的问题。之前实际在`busybox`上遇到这个问题，那基本确定又是`getaddrinfo`的问题了。
这个函数属于`glibc`的`NSS`层，也就是`libnss`的支持，这个库在设计时候就是动态的，因为需要依靠`系统配置`来决定`dns server`，所以在`静态编译`的情况下会出现无法解析域名的情况，这样后续的`addrinfo`就会有`空指针`导致后续函数出错，从而导致段错误。

那解决方式就只有重写`getaddrinfo`这个函数了，这个函数的作用简单来说就是把`域名`解析成`IP`，而这个过程需要`dns`参与其中，而解析的过程实际就是需要向`DNS Server`发送一个`query`然后提取信息即可，但是我又找到一个轮子：[getaddrinfo.h](https://github.com/dna2github/dna2oslab/blob/master/linux/getaddrinfo.h)

这个轮子在大方向上实现了目的，但是并不是直接替换函数就行了，因为还要为两个轮子做做适配才行。

首先是`clinet`代码，核心连接函数是`establishConnection`，它的入参是通过`getaddrinfo.h`中提供的重写函数生成的。那先放在这往下看，假设这儿的入参没有问题，那么在下面`connect`时候可能会出问题：
```
if (connect(clientfd, info->ai_addr, info->ai_addrlen) < 0) 
```
这儿`connect`走的是`系统超时`也就是`net.ipv4.tcp_syn_retries`的配置，我的系统默认配置是`6`，也就是`127`秒：
```
$ sysctl net.ipv4.tcp_syn_retries  
net.ipv4.tcp_syn_retries = 6
```
这儿先改一下，加一个超时设置：
```
struct timeval timeo = {3, 0};
socklen_t time_len = sizeof(timeo);
timeo.tv_sec = atoi("3");
setsockopt(clientfd, SOL_SOCKET, SO_SNDTIMEO, &timeo, time_len);
```
这样`clientfd`这个`socket fd`就被会设置成`3s`超时。
然而`入参`就真的没问题吗？

## `getaddrinfo`
针对`dns`的解析有两种，一种是传输进来的`host`是`ip`，另一种是`域名`，针对`IP`的情况函数中调用了一个`__dns_is_ipv4`识别，然后再用`__dns_ipv4`去处理，然后把`addrinfo`填充起来。
然而坑的是，这儿端口是被设置成`0`的，这其实对于实现`dns`解析这个目的是没问题的，因为我们不需要端口，但是解析后的`addrinfo`如果给`establishConnection`使用就有问题了，因为端口是`0`，所以这儿加一个入参，把端口设置一下：
```
static int __dns_ipv4(const char *ip, const char *port,struct addrinfo **res) {
    ......
    sa->sin_port = htons((atoi(port)));
    ......
}
```
同样的对于域名的处理用的是`__dns_parse`函数填充，这儿就不止是端口了，还有`ai_flags`，`ai_socktype`，一样设置一下：
```
static int __dns_parse(const char *buf, const char *port,int query_len, struct addrinfo **res) {
    ......
    info->ai_flags = AI_PASSIVE;
    info->ai_socktype = SOCK_STREAM;
    sa->sin_port = htons((atoi(port)));
    ......
}
```
最后这样才能生成一个可供使用的`addrinfo`。

> 这里面还有一个`tips`是`sockaddr_in` 和`sockaddr`，`sockaddr`更早，`sockaddr_in`是补全形式，将`ip`和`port`分开了，两个结构体长度是一样的，因此指针可以直接相互引用。

# 参考
* [https://www.binarytides.com/dns-query-code-in-c-with-linux-sockets/](https://www.binarytides.com/dns-query-code-in-c-with-linux-sockets/)
* [DNS RESPONSE MESSAGE FORMAT](http://www.firewall.cx/networking-topics/protocols/domain-name-system-dns/161-protocols-dns-response.html)
* [linux下connect超时时间探究](https://www.cnblogs.com/minglee/p/10161899.html)
