# Limit
tornado的极轻量级博客

**环境要求**： `Python 2.7` `Mysql/Mariadb`  
**模块安装**:  
1. `tornado`
2. `time`
3. `sqlalchemy`
4. `markdown`  

**启动**:  
`main.py`  
```
define("port", default=8080, help="PORT", type=int)
```  
修改其中的`default`，为想要设定的web端口  

**Usage**  
建立数据库，导入blog.sql  
终端执行  
```
$python2 main.py
``` 
**注意**

404页面中存在一个Video区域，但是我没有上传那个Video，所以可以自行选取一个Video放到视屏床上，然后引用

**文件自定义**  

`extensions.py`  
```
engine = create_engine('mysql://ume:pwd@localhost:3306/blog_db', echo=True)#ume和pwd为mysql用户帐号和密码，blog_db为博客指定的数据库
```  
`main.py`  
```
sys.path.append("Blog_Path") #Blog的根目录地址
```  
```
cookie_secret="c2fc16cbc0e8462248d26b7d74e0b562=",#Cookie的加盐,自定义加盐的数据，反正你看不懂
```  
`handlers/index.py`  
```
class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user != 'Password': #Password部分为自己定义
```  
`urls.py`  
```
Blog的路由表，欲添加新的页面，自写
```  

**安全性**  
作为一个安全从业者，第一次玩开发，就没有去考虑安全性 :)  
密码采用的是写死在文件的方式，数据库中只有一个表，也就是记录文章的，只要Blog不使用具备`_File_`权限的用户启动，我想大概也许可能应该是没有啥问题的吧，哈哈，但是后台可以爆破，这儿我实在是懒得加验证码机制了，原本想调用Google的`authOA`的，但是还是懒得写了，所以把存在的漏洞和功能一起说吧  

**漏洞**  
1. `/`  
前台采用`Timeline`的方式展示文章，搜索框支持模糊查询，但仅限查询文章名中的关键字  
因为没有做过滤，所以此处存在Sql注入  
2. `login`  
JQ的动态登录页面，需要点击任意属性，触发`login`框题浮现，第一个`input`是装饰，第二个`input`输出密码，回车进入后台  
因为没有添加验证码，所以存在后台爆破的漏洞  
3. `home`  
JQ分页，这是我搞了两小时才搞定的东西，`Tornado`自带`xsrf_token`，所以不用担心`csrf`的攻击,但是由于本人前端功底实在low，所以有可能会出现前端渲染崩溃的问题  
删除按钮存在sql注入  
4. `edit` `add`  
这两个页面一个模板，后端不一样而已，比较舒服的是支持了Markdown的编写和即时预览，这就很舒服了，我就觉得Blog的Post应该用Markdown语法写才有感觉  
都存在Sql注入，可能存在XSS，没有测过  

**麻烦的地方**  
后台添加了两个网易云音乐的链接，但是很烦的是网络环境差的话会一直加载，很烦  
Link的友链必须得手动修改源码才能添加，原本想后台写个源码的，但是一想到又要建表，瞬间不想动了，多接触接触源码也好，还有文章留言的问题，原本想调用多说的，结果刚把Blog完成，多说被封了！！！我当时是绝望的，所以就直接气得不添加留言了，等多说解禁，再抽时间添加上去，自己添加也很简单  

**优点(自认为，可忽略)**  
1. 非常轻量级的Blog程序，不加index的那个背景图，只有1M大小
2. 功能修改，添加，删除极其简单，后期添加功能完全盲打，不需要调试，前端简洁，虽然有时候可能会崩溃
3. Code量少，非常容易理解，所以非常适合二次开发
4. 等等。。。。  

**联系作者**  
Blog程序出什么问题的话，可以在`Github`项目下留言  

**前端展示**  
![Limit](Limit.png)
