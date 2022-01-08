> 一样，工作上遇到的就记录下来


事情是这样的，因为之前我给容器做了缩减删除了大量不必要的二进制文件以提高线上容器的安全性，但是随之而来的问题就是公司内部一些高权限的业务组想要直接调试线上的容器而极度不方便，这样最开始我的方案只能是提供一个工具包出来，其中包括了各种调试用的二进制文件以及这些文件所需要的`lib`和`config`，每次调试前下载，调试后清除。这种模式在一定程度上确实解决调试线上容器的需求，但是缺点也是非常明显的：
```
镜像类型可能是`centos`可能是`ubuntu`甚至是其他，这就导致需要提供不同环境下可用的二进制文件，静态编译的二进制文件显然是一个很好的无视环境的方法，但是各种二进制文件的静态编译这个行为本身就是一个十分耗费精力甚至是不可实现的操作，因为并非所有的二进制文件在设计之初就是考虑到静态编译的，这就导致他们在静态编译的情况下会出现意料之外的问题甚至是不可运行。后来想过用`busybox`来替代这些调试软件，因为其本身就是一个调试工具箱，但是新的问题又来了，busybox提供的applet是相比于源程序来说很多是阉割版本的，这就导致对于某些参数的支持甚至是返回值的格式都存在问题，因此这个方案也被取缔掉了，而随着debug的需求越来越多，甚至是达到了要求按照不同的场景定制debug的要求产生时，已有的方案已经不足以支撑了，需要开拓新的技术方向不然只有死路一条。
```


# 从容器本身入手
首先要明白调试的需求是容器内的正在运行的进程或者是已经发生`coredump`的程序，后者会产生`core`文件，而调试的本质上是去调试相应的`core`文件而非进程本身，这个实际上是好做的，只需要拉取到相应的`core`文件便是，然而前者却是一个大问题。


调试一个活着的进程最典型的操作就是用`gdb`去`attach`一个进程，然而不说进行了缩减后的容器中肯定会删掉`gdb`，光就`centos`或者`ubuntu`本身实际上就是没有预装`gdb`的，而在`ubuntu`装一个`gdb`程序涉及到的文件引入高达`2000+`，这明显超出了能够容忍的底线，因此在容器中直接提供`gdb`一开始是被我直接否决的，除非是用到了静态编译的`gdb`，这个可太难了我花了半天没搞定最后还是直接下了一个别人静态编译好的，全网也就找到那么一个，不过倒是有相关的讨论可以参考一下。


如果`gdb`是在宿主机上的该怎么办呢？容器本身的隔离是依靠的`namespace`的隔离，意思就是说倘若`gdb`能够进入到容器内部的`namespace`自然是能够调试其中的进程的，而`nsenter`这个工具就很非常容易的完成这个操作，不少人应该用过`docker-exec`，可以说`nsenter`就是`docker-exec`的底层实现
```
nsenter -t $PID --mount --uts --ipc --net --pid 基本上就等于是docker-exec
```
但是新的问题就来了，`gdb`是根据`/proc/pid/exe`去加载相应的程序的，基本上加载不到相应的程序是必然发生的事情，而且因为`gdb`是外部的`pid namespace`因此还得去找一下容器内部的进程在外部的`pid`。


到这儿我的思路是卡住的，感觉进入到了死胡同里，只能去查阅一下资料，意外的发现了一篇关于`docker-debug`的文章，大概看了一遍后大骂自己蠢，自己以前明明搞过`runc`把`fs`搞的十分透彻了结果现在全忘了，这不就是依靠`UnionFs`可以顺利解决的事情吗？


说的简单的原理就是找到要调试的容器的`filesystem`，然后在这个基础上利用`UnionFs`的特性再生成一个包含了`debug`工具的新的`filesystem`，然后再打开一个新的容器挂载这个`fs`并且与被调试容器具有相同的`pid, ipc, uts, net`等`namespace`，别人连现成的代码都直接放出来了，感慨一句动手能力真的强大，虽然用的是我最为讨厌的语言 -- `Go`。


# 源码阅读
> 幸亏代码量不多，不然我真是看都不想看


整个代码的核心逻辑并不多，可以分为三大逻辑区域：
1. `Init Config`
2. `Init Cli`
3. `Init Container`


## `Init Config`
这个其实是写在`Init Cli`的逻辑中的，但是一切的开始
```
conf, err := config.LoadConfig()
```
简单来说逻辑就是去查看指定路径下是否已经有了`Config`文件，有的话则读取一下然后直接进入到`Init Cli`的流程，但是如果没有的话则需要去生成默认的配置
```
version = "unknown-version"
mount_dir = "/mnt/container"
image = "nicolaka/netshoot:latest"
timeout = 10000000000
config_default = "default"


[config]
  [config.default]
    version = "1.40"
    host = "unix:///var/run/docker.sock"
    tls = false
    cert_dir = ""
    cert_password = ""
```
上面是一个配置应该有的状态，其中`mount_dir`，`image`是比较重要的两个配置，这个会在`Init Container`中被用到，`host`这一个优先会根据`DOCKER_HOST`这个环境变量配置，但是如果没有的话会进入到`ParsHost`的流程然后设置一个缺省值
```
DefaultUnixSocket = "/var/run/docker.sock"
var DefaultHost = fmt.Sprintf("unix://%s", DefaultUnixSocket) 
 46 func ParseHost(defaultToTLS bool, val string) (string, error) {                                                                                                                                                                           
 47     host := strings.TrimSpace(val)
 48     if host == "" {
 49         if defaultToTLS {
 50             host = DefaultTLSHost
 51         } else {
 52             host = DefaultHost
 53         }
 54     } else {
 55         var err error
 56         host, err = parseDockerDaemonHost(host)
 57         if err != nil {
 58             return val, err
 59         }
 60     }
 61     return host, nil
 62 }
```
这是`Init Config`的部分，主要的功能就是在指定的位置生成一个基础的config文件，且内容大多默认，然而问题就是这一份文件其实在后续的利用中是被读入到内存中然后再去变化其各个值的，因此才能做到启动多个debug环境也能只需要一个config


## `Init Cli`
工具是一个命令行工具，且需要和环境中的docker通信并发生调用，因此需要创建一个`Cli`的环境出来，大的函数是`buildCli`，其中的相当一部分逻辑其实还是在修改读取到内存中的`config`，真正涉及到`cli`创建的逻辑是这一部分：
```
 71 func NewDebugCli(ops ...DebugCliOption) (*DebugCli, error) {                                                                                                                                                                              
 72     cli := &DebugCli{}
 73     if err := cli.Apply(ops...); err != nil {
 74         return nil, err
 75     } 
 76     if cli.out == nil || cli.in == nil || cli.err == nil {
 77         stdin, stdout, stderr := term.StdStreams()
 78         if cli.in == nil { 
 79             cli.in = stream.NewInStream(stdin)
 80         }   
 81         if cli.out == nil {
 82             cli.out = stream.NewOutStream(stdout)
 83         }   
 84         if cli.err == nil {
 85             cli.err = stderr
 86         }
 87     }
 88     return cli, nil
 89 }
```
可以看到主要是输入输出流的建立，其实并没有什么可说的部分


## `Init Container`
这是整个工具的核心逻辑，主函数逻辑在`runExec`中，读一下函数结果第一个就能看到的是函数中的一个延迟函数，也就是函数要返回时回去执行的逻辑
```
124     defer func() {
125         if containerID != "" {
126             err = cli.ContainerClean(containerID)
127             if err != nil {
128                 logrus.Debugf("%+v", err)
129             }                                                                                                                                                                                                                             
130         }
131         err = cli.Close()
132         if err != nil {
133             logrus.Debugf("%+v", err)
134         }
135     }()
```
根据名字可以大致看出来逻辑是先去清除一个容器，然后关闭掉`Cli`环境，可见这确实就是最后的收尾部分了。
继续看正常的运行逻辑，之前说过`config`中的`image`是有用的，因为这儿就有一个`images, err := cli.FindImage(conf.Image)`的函数操作，先看变量是`config.image`，如果用户没有用`--image`去指定`image`的话用的就会是`config`中默认的值，这一部分逻辑在`buildCli`中
```
 82     //修改配置文件中拉取的debug image
 83     if options.image != "" {
 84         conf.Image = options.image
 85     }
```
着重去跟一下`FindImage`函数
```
232 func (cli *DebugCli) FindImage(image string) ([]types.ImageSummary, error) {                                                                                                                                                              
233     args := filters.NewArgs()
234     args.Add("reference", image)
235     ctx, cancel := cli.withContent(cli.config.Timeout)
236     defer cancel()
237     return cli.client.ImageList(ctx, types.ImageListOptions{
238         Filters: args,
239     })  
240 }   
```
这个注意一个`cli.client`，这个就已经是调用到`docker/client`了，而`ImageList`是其中的一个`interface`，作用是展示镜像列表，等同于`$docker images`的效果，而传入的`types.ImageListOptions`则是筛选项，即只获取到`args`指定的那个镜像，也就是`config`中的`image`。
这儿肯定要考虑到，如果没有这个镜像怎么办呢？作者也考虑到了这个问题，因此在下面会根据返回值是否为空来决定是否要调用`PullImage`拉取镜像，这儿就等同于`$docker pull image`，但是要注意的一点就是从哪儿拉取镜像，镜像的拉取其实是需要写完整镜像中心域名的，不然就是按照缺省值拼接，正如这儿的拼接
```
212     domain, remainder := splitDockerDomain(image)
213     imageName := domain + "/" + remainder
```
再看`splitDockerDomain`
```
193 func splitDockerDomain(name string) (domain, remainder string) {
194     i := strings.IndexRune(name, '/')
195     if i == -1 || (!strings.ContainsAny(name[:i], ".:") && name[:i] != "localhost") {
196         domain, remainder = defaultDomain, name
197     } else {
198         domain, remainder = name[:i], name[i+1:]
199     }
200     if domain == legacyDefaultDomain {
201         domain = defaultDomain
202     }
203     if domain == defaultDomain && !strings.ContainsRune(remainder, '/') {
204         remainder = officialRepoName + "/" + remainder
205     }
206     return
207 }
```
基本都是回归到`defaultDomain = docker.io`上，因此如果工具是各位二次开发给公司内部用且内部有自己的镜像中心的话，建议这儿改掉缺省值，不然会存在安全问题。
上面的整个逻辑是去准备`debug image`，那接着就是要去确定被调试的那个容器了，这儿作者玩了一个手段
```
containerID, err = cli.FindContainer(options.container)
```
`options.container`是用户的输入也是必须要的值，然后通过`FindContainer`这个函数去确认，这儿我一开始的想法应该是作者在这个函数中做了处理逻辑，做了一个容器的`containerid`和`image`的映射，但是转头一想如果用户输入的是`image`而且同时启动了两个相同的`image`的容器怎么办？结果跟进去一看
```
446 func (cli *DebugCli) FindContainer(name string) (string, error) {                                                                                                                                                                         
447     return name, nil
475 } 
```
妙啊，是不是还奇怪行号有问题，这是因为作者注释了好大一大段，大概逻辑就是实现我上面那个疑惑，结果大概是因为没解决直接删了: )
那结果显而易见了，用户的输入只能是一个确定的`containerID`，因为这是唯一的，能省去很多麻烦提升效率。
接下来就是最核心的部分`containerID, err = cli.CreateContainer(containerID, options)`
先说一下这个工具的调试思想是创建一个新的容器和被调试容器共享指定的`namespae`，而在文件系统的解决方案上是直接把被调试容器的`mergedDir`挂载到新容器中，这个方法其实还是有缺陷的，毕竟不是用的相同的`fs`，因此在`/proc`的`exe`指向上还有`动态链接库`等用到了绝对路径的情况上依然存在问题。
`CreateContainer`首先会调用`info, err := cli.client.ContainerInspect(ctx, attachContainer)`去获取到被调试容器的详情并从中提取到`MergedDir`，这个代表的是被调试容器的`fs`路径，找到后添加到一个`[]mount.Mount`类型的数组里
> 这个可以参照`$docker inspect containerID`


```
275         if ok {
276             mounts = append(mounts, mount.Mount{ 
277                 Type:   "bind",
278                 Source: mountDir,
279                 Target: cli.config.MountDir,
280             })
281         }
```
并将挂载类型选择为`bind`，这部分知识点涉及到了容器的两种数据持久化挂载类型：
1. `bind`
2. `volume`


作者继续考虑到的一种情况是被调试容器中存在挂载的的情况，也就是`$docker run -v path:path`这一种启动情况，因此针对这种情况也做了一个检查后增加`Mount`
```
282         for _, i := range info.Mounts {                                                                                                                                                                                                   
283             var mountType = i.Type
284             if i.Type == "volume" {
285                 mountType = "bind"
286             }   
287             mounts = append(mounts, mount.Mount{
288                 Type:     mountType,
289                 Source:   i.Source,
290                 Target:   cli.config.MountDir + i.Destination,
291                 ReadOnly: !i.RW,
292             })
293         }
```
至此就是在`mounts`中设置好了调试容器中全部要挂载的路径以及相关挂载属性。接下来就是要真正创建出一个`container`了
```
357     body, err := cli.client.ContainerCreate(
358         ctx,
359         conf,
360         hostConfig,
361         nil,
362         "",
363     )
```
`conf`和`hostConfig`是代表和一个`container`的构建属性
```
333     targetName := containerMode(attachContainer)
334 
335     conf := &container.Config{
336         Entrypoint: strslice.StrSlice([]string{"/usr/bin/env", "sh"}), //debug container的entrypoint
337         Image:      cli.config.Image,                                  //镜像系统选择,决定了debug容器的基础镜像
338         Tty:        true,
339         OpenStdin:  true,
340         StdinOnce:  true,
341     }
342     hostConfig := &container.HostConfig{
343         NetworkMode: container.NetworkMode(targetName), //network共享
344         UsernsMode:  container.UsernsMode(targetName),  //user共享
345         PidMode:     container.PidMode(targetName),     //pid共享
346         Mounts:      mounts,                            //容器内部的挂载情况
347         SecurityOpt: options.securityOpts,              //入参项，无视
348         CapAdd:      options.capAdds,                   //入参项目，无视
349         //VolumesFrom: []string{attachContainer},
350     }
```
这部分配置其实是容器启动后，可以通过`$docker inspect containerID`查看到，这儿设置的就是那一部分数据，至此为止一个容器其实是一种完成了，后面的逻辑就是把`container`启动起来，然后再通过`exec`去执行命令然后打印输出，这部分可以看作者原博客的`demo`来理解。


# 结语
工具好吗？说实话还是可以的，相比于`nsenter`来说确实是更易于调试，因为内部挂载了相应的文件系统，而且`/proc`少了很多干扰，但是和我理想中的调试情况还是有点差距，这点主要是由于`docker`本身来带的限制，也就是针对`image`的存储上好象是杜绝了用户介入，导致无法自定义一个镜像的`layer`，在粒度行就粗略了太多，而在这方面直接使用`runc`来进行容器的创建可能更好一点，但是另一个问题就是随之带来的就是技术难度的升级，因为`runc`本身不会去管`fs`的生成，同时其是否有能力共享指定的`namespace`还有待确认，路漫漫其修远兮啊。


# 参考资料
* [gdb-static]([https://github.com/hugsy/gdb-static](https://github.com/hugsy/gdb-static))
* [How i can static build GDB from source?]([https://stackoverflow.com/questions/9364685/how-i-can-static-build-gdb-from-source](https://stackoverflow.com/questions/9364685/how-i-can-static-build-gdb-from-source))
* [docker 容器调试新姿势]([https://blog.zeromake.com/pages/docker-debug/](https://blog.zeromake.com/pages/docker-debug/))
* [docker-debug]([https://github.com/zeromake/docker-debug](https://github.com/zeromake/docker-debug))
* [Docker学习笔记（6）——Docker Volum]([https://www.jianshu.com/p/ef0f24fd0674](https://www.jianshu.com/p/ef0f24fd0674))
* [走进docker(05)：docker在本地如何管理image（镜像）?]([https://segmentfault.com/a/1190000009730986](https://segmentfault.com/a/1190000009730986))