`k8s`的架构


![516d87a1-26be-421b-b749-a4fd021cc459.png](通过发布应用认识k8s_files/516d87a1-26be-421b-b749-a4fd021cc459.png)


得先明白`k8s`的一些基础概念才行


# Node
节点可以是一个虚拟机或者是物理机这个完全取决于集群的配置，分为`Master Node`和`Worker Node`前者在一个集群中唯一，其上提供了各种控制组件用来管理整个`k8s`集群，而`Worker Node`则一般用作项目发布用，如果用传统网络来比喻的话`Master Node`像是`域控`，而`Worker Node`则是一个个基础服务器。


# Pod
`K8s`的最小管理单元，但是依然是一个概念性质的东西，是一个针对`逻辑主机`的建模，其中包含了一个或者多个的`container`，这儿的`container`就是`docker`实现的那个`container`的概念，但是因为上层有个`pod`的概念这就需要其中的`container`共享`namespace`，因此用传统网络比喻的话，`pod`更像是服务器上的一个虚拟机，而`container`则是虚拟机中的一个进程。一个`pod`在创建后一般情况下是无法改变的，只能通过新建来取代掉，但是对于运行中的`pod`，还是能够针对某些字段进行更新，其中`pod id`在整个集群中唯一。


# Cluster
集群的概念，即一个`Master Node`和多个`Worker Node`组成的集合。


# Namespace
和`Linux Namespace`不是一个概念东西，而是一个虚拟集群的概念，一切资源都在`Cluster`上，但是并非一切资源都在`Namespace`中，例如其本身，还有持久化卷，`Node`等资源。


# ApiServer
在`Master Node`上的集群核心组件，主要功能是提供管理整个集群的`REST API`，支持`https(6443)`和`http(8080)`，其中`http`接口无任何安全/授权认证，因此禁止生产环境启用。因为`k8s`集群中的一些操作都需要通过`apiserver`所以可以提供`audit log`作为安全审计的日志


# kubelet
`Node`上运行的组件，可以看成是`k8s`管理整个集群的`client`或者是`agent`，常驻服务负责和`apiserver`通信管理`Node`上的`pods`。


# kube-proxy
`k8s`在每个`Node`上运行的`网络代理`服务，不过底层原理是调用的`iptables`，实现了一种`VIP 虚拟IP`。


# Role
`k8s`使用的是一种基于角色的访问控制方式(`RBAC`)，其元数据中规定了一个角色能够对指定的资源进行指定的操作。其中`Role`的权限局限于一个`Namespace`中，而`ClusterRole`则是适用于整个集群。


# ServiceAccount
`k8s`中为`pod`内`服务`访问`apiserver`或者其余服务专门设计了一个`ServiceAccount`，如果要使用这个功能的话，则需要将`pod`指定的`serviceaccount`的`secrets`挂载到`pod`内部。


# RoleBinding
角色绑定，这个功能将一个对某些资源有既定权限的角色授予一个或者一组用户(`User`，`Group`或者是`ServiceAccount`)，使得被授权的用户获得相应的权限。


# Job
`k8s`中一次性任务的概念，即想要运行容器执行特定的任务，当任务完成后容器也没有存在的必要了，`pod`会自动退出且集群也不再重新将其唤醒，一般创建出来用来做`数据计算`和`测试`。


# Cronjob
`k8s`中计划任务的概念，可以参照一下`linux`的`crontab`


# DaemonSet
如同名字的含义类似于基础组件一样的对象，通过`DaemonSet`创建的`Pod`可以确保在集群中的每一个`Node`上运行着，比如新加入集群的`Node`上会自动被添加一个`Pod`，其常常用来运行一些基础组件服务比如`集群存储`，`节点监控`之类的。


# ReplicaSet
为了解决`pod`重启而提出来 `Replication Controller`简称`RC`的概念用来保证在任意时间运行的`pod`的副本数量，即保证`pod`总是可用的。但是随着技术的发展新出现的`Replication Set`逐渐取代`RC`，其实二者功能基本一致，唯一的区别就是`RC`只支持基于等式的`selector`即`env=dev`而`RS`则支持基于集合的`selector`即`version in (v1.0, v2.0)`


# Deployment
替代`RS`的更高级的部署概念定义，为`pod`和`RS`提供了声明式更新，`controller`会将`pod`和`RS`的状态改变到定义的目标状态，注意：您不该手动管理由 Deployment 创建的 Replica Set，否则您就篡越了 Deployment controller 的职责！


# Service
一个提供负载均衡和服务自动发现的概念，在`pod`反复滚动变动的情况下依然能对外保持一个服务整体，本质上是一种逻辑分组的策略，其中有四种类型：
1. `ClusterIp`：默认类型，自动分配一个仅集群内部可以访问的虚拟`IP`
2. `NodePort`：在`ClusterIp`的基础上给每个`Node`上绑定一个端口用来访问到`服务`
3. `LoadBalancer`：在`NodePort`的基础上借助云供应商创建一个新的负载均衡器并将请求转发到`NodePort`上
4. `ExternalName`：把集群外部服务引入到集群内部来并在内部直接使用


# Ingresses
一个新的流量控制层，可以看作是`Service`上层的`智能路由`，一般用`nginx`或者`haproxy`实现，本质上是一组基于`DNS`或者`URL`转发请求到指定`Service`的规则策略。


# Secrets
`k8s`中的一种对象类型，用来保存密码，私钥，口令敏感信息，`pod`通过挂载和环境变量的形式来引用到`Secrets`


# 对外发布一个服务
`k8s`的是现代很多`Devops`流程的底层实现，因为其发布服务能够高度定制化和快捷，要学习`k8s`的相关使用可以通过手动发布一个服务。
首先就是先搭建一个服务发布环境出来，其中包括集群的隔离，权限的划分等等，因此先创建一个`Namespace`作为发布环境：
```
apiVersion: v1
kind: Namespace
metadata:
  name: canarydemo
```
通过如下命令查看创建出来的`Namespace`详情
```
$ kubectl get namespaces canarydemo -o yaml
apiVersion: v1
kind: Namespace
metadata:
  creationTimestamp: "2021-03-16T07:18:25Z"
  managedFields:
  - apiVersion: v1
    fieldsType: FieldsV1
    fieldsV1:
      f:status:
        f:phase: {}
    manager: kubectl-create
    operation: Update
    time: "2021-03-16T07:18:25Z"
  name: canarydemo
  resourceVersion: "673943"
  selfLink: /api/v1/namespaces/canarydemo
  uid: d19706b3-9b0a-41b5-83be-1b991a1a098e
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
```
接着创建`Role`和`ServiceAccount`并且绑定角色，当然如果你的服务没有这个需求的话，这一步可以直接省略掉没什么必要
```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: canary-admin
  namespace: canarydemo


apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: canarydemo
  name: canary-admin
rules:
- apiGroups: [""] # "" 标明 core API 组
  resources: ["pods"]
  verbs: ["get", "watch", "list"]


apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pods-admin
  namespace: canarydemo
subjects:
- kind: ServiceAccount
  name: canary-admin
roleRef:
  kind: Role
  name: canary-admin   
  apiGroup: rbac.authorization.k8s.io
```
至此服务的发布环境就基本完成了，然后发布一个服务
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: canarydemo
  labels:
    app: myapp
spec:
  selector:
    matchLabels:
      app: myapp
  replicas: 2 
  template:
    metadata:
      labels:
        app: myapp
    spec:
      serviceAccountName: canary-admin
        #      automountServiceAccountToken: false
      containers:
      - name: k8sdemo
        image: myapp:v2
        securityContext:
          privileged: true
        workingDir: "/apps/"
        env:
          - name: PATH
            value: "/usr/local/bin/:/usr/local/sbin/:/usr/bin/:/usr/sbin/:/bin/:/sbin/"
        command: ["/apps/start.sh"]
        ports:
        - containerPort: 8080
```
其中的`replicas`设定了有两个副本，说明这个服务有两个`pod`，然后在`securityContext`中给予了`特权模式`，而服务的运行端口是`8080`。然而这个时候因为网络的问题服务还是访问不到的，需要通过创建`Service`来将`pod`应用公开为`网络服务`。
```
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: canarydemo
  labels:
    app: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - name: myapp
    protocol: TCP
    port: 80
    nodePort: 32600
    targetPort: 8080
  type: NodePort
```