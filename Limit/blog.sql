-- phpMyAdmin SQL Dump
-- version 4.6.0
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Mar 25, 2017 at 09:48 AM
-- Server version: 10.1.21-MariaDB
-- PHP Version: 7.1.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `blog`
--

-- --------------------------------------------------------

--
-- Table structure for table `post`
--

CREATE TABLE `post` (
  `id` int(20) NOT NULL,
  `title` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `html` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `post`
--

INSERT INTO `post` (`id`, `title`, `content`, `html`, `date`) VALUES
(2, 'Blog\'s Usage', '**环境要求**： `Python 2.7` `Mysql/Maridb`  \r\n**模块安装**:  \r\n1. `tornado`\r\n2. `time`\r\n3. `sqlalchemy`\r\n4. `markdown`  \r\n\r\n**启动**:  \r\n`main.py`  \r\n```\r\ndefine("port", default=8080, help="PORT", type=int)\r\n```  \r\n修改其中的`default`，为想要设定的web端口  \r\n**Usage**  \r\n```\r\n$python2 main.py\r\n```  \r\n**文件自定义**  \r\n`extensions.py`  \r\n```\r\nengine = create_engine(\'mysql://ume:pwd@localhost:3306/blog_db\', echo=True)#ume和pwd为mysql用户帐号和密码，blog_db为博客指定的数据库\r\n```  \r\n`main.py`  \r\n```\r\nsys.path.append("Blog_Path") #Blog的根目录地址\r\n```  \r\n```\r\ncookie_secret="c2fc16cbc0e8462248d26b7d74e0b562=",#Cookie的加盐,自定义加盐的数据，反正你看不懂\r\n```  \r\n`handlers/index.py`  \r\n```\r\nclass LoginHandler(BaseHandler):\r\n    def get(self):\r\n        if self.current_user != \'Password\': #Password部分为自己定义\r\n```  \r\n`urls.py`  \r\n```\r\nBlog的路由表，欲添加新的页面，自写\r\n```  \r\n**安全性**  \r\n作为一个安全从业者，第一次玩开发，就没有去考虑安全性 :)  \r\n密码采用的是写死在文件的方式，数据库中只有一个表，也就是记录文章的，只要Blog不使用具备`_File_`权限的用户启动，我想大概也许可能应该是没有啥问题的吧，哈哈，但是后台可以爆破，这儿我实在是懒得加验证码机制了，原本想调用Google的`authOA`的，但是还是懒得写了，所以把存在的漏洞和功能一起说吧  \r\n\r\n**漏洞**  \r\n1. `/`  \r\n前台采用`Timeline`的方式展示文章，搜索框支持模糊查询，但仅限查询文章名中的关键字  \r\n因为没有做过滤，所以此处存在Sql注入  \r\n2. `login`  \r\nJQ的动态登录页面，需要点击任意属性，触发`login`框题浮现，第一个`input`是装饰，第二个`input`输出密码，回车进入后台  \r\n因为没有添加验证码，所以存在后台爆破的漏洞  \r\n3. `home`  \r\nJQ分页，这是我搞了两小时才搞定的东西，`Tornado`自带`xsrf_token`，所以不用担心`csrf`的攻击,但是由于本人前端功底实在low，所以有可能会出现前端渲染崩溃的问题  \r\n删除按钮存在sql注入  \r\n4. `edit` `add`  \r\n这两个页面一个模板，后端不一样而已，比较舒服的是支持了Markdown的编写和即时预览，这就很舒服了，我就觉得Blog的Post应该用Markdown语法写才有感觉  \r\n都存在Sql注入，可能存在XSS，没有测过  \r\n\r\n**麻烦的地方**  \r\n后台添加了两个网易云音乐的链接，但是很烦的是网络环境差的话会一直加载，很烦  \r\nLink的友链必须得手动修改源码才能添加，原本想后台写个源码的，但是一想到又要建表，瞬间不想动了，多接触接触源码也好，还有文章留言的问题，原本想调用多说的，结果刚把Blog完成，多说被封了！！！我当时是绝望的，所以就直接气得不添加留言了，等多说解禁，再抽时间添加上去，自己添加也很简单  \r\n\r\n**优点(自认为，可忽略)**  \r\n1. 非常轻量级的Blog程序，不加index的那个背景图，只有1M大小\r\n2. 功能修改，添加，删除极其简单，后期添加功能完全盲打，不需要调试，前端简洁，虽然有时候可能会崩溃\r\n3. Code量少，非常容易理解，所以非常适合二次开发\r\n4. 等等。。。。  \r\n\r\n**联系作者**  \r\nBlog程序出什么问题的话，可以在`Github`项目下留言', '<p><strong>环境要求</strong>： <code>Python 2.7</code> <code>Mysql/Maridb</code><br />\n<strong>模块安装</strong>:<br />\n1. <code>tornado</code>\n2. <code>time</code>\n3. <code>sqlalchemy</code>\n4. <code>markdown</code>  </p>\n<p><strong>启动</strong>:<br />\n<code>main.py</code><br />\n<code>define("port", default=8080, help="PORT", type=int)</code><br />\n修改其中的<code>default</code>，为想要设定的web端口<br />\n<strong>Usage</strong><br />\n<code>$python2 main.py</code><br />\n<strong>文件自定义</strong><br />\n<code>extensions.py</code><br />\n<code>engine = create_engine(\'mysql://ume:pwd@localhost:3306/blog_db\', echo=True)#ume和pwd为mysql用户帐号和密码，blog_db为博客指定的数据库</code><br />\n<code>main.py</code><br />\n<code>sys.path.append("Blog_Path") #Blog的根目录地址</code><br />\n<code>cookie_secret="c2fc16cbc0e8462248d26b7d74e0b562=",#Cookie的加盐,自定义加盐的数据，反正你看不懂</code><br />\n<code>handlers/index.py</code><br />\n<code>class LoginHandler(BaseHandler):\n    def get(self):\n        if self.current_user != \'Password\': #Password部分为自己定义</code><br />\n<code>urls.py</code><br />\n<code>Blog的路由表，欲添加新的页面，自写</code><br />\n<strong>安全性</strong><br />\n作为一个安全从业者，第一次玩开发，就没有去考虑安全性 :)<br />\n密码采用的是写死在文件的方式，数据库中只有一个表，也就是记录文章的，只要Blog不使用具备<code>_File_</code>权限的用户启动，我想大概也许可能应该是没有啥问题的吧，哈哈，但是后台可以爆破，这儿我实在是懒得加验证码机制了，原本想调用Google的<code>authOA</code>的，但是还是懒得写了，所以把存在的漏洞和功能一起说吧  </p>\n<p><strong>漏洞</strong><br />\n1. <code>/</code><br />\n前台采用<code>Timeline</code>的方式展示文章，搜索框支持模糊查询，但仅限查询文章名中的关键字<br />\n因为没有做过滤，所以此处存在Sql注入<br />\n2. <code>login</code><br />\nJQ的动态登录页面，需要点击任意属性，触发<code>login</code>框题浮现，第一个<code>input</code>是装饰，第二个<code>input</code>输出密码，回车进入后台<br />\n因为没有添加验证码，所以存在后台爆破的漏洞<br />\n3. <code>home</code><br />\nJQ分页，这是我搞了两小时才搞定的东西，<code>Tornado</code>自带<code>xsrf_token</code>，所以不用担心<code>csrf</code>的攻击,但是由于本人前端功底实在low，所以有可能会出现前端渲染崩溃的问题<br />\n删除按钮存在sql注入<br />\n4. <code>edit</code> <code>add</code><br />\n这两个页面一个模板，后端不一样而已，比较舒服的是支持了Markdown的编写和即时预览，这就很舒服了，我就觉得Blog的Post应该用Markdown语法写才有感觉<br />\n都存在Sql注入，可能存在XSS，没有测过  </p>\n<p><strong>麻烦的地方</strong><br />\n后台添加了两个网易云音乐的链接，但是很烦的是网络环境差的话会一直加载，很烦<br />\nLink的友链必须得手动修改源码才能添加，原本想后台写个源码的，但是一想到又要建表，瞬间不想动了，多接触接触源码也好，还有文章留言的问题，原本想调用多说的，结果刚把Blog完成，多说被封了！！！我当时是绝望的，所以就直接气得不添加留言了，等多说解禁，再抽时间添加上去，自己添加也很简单  </p>\n<p><strong>优点(自认为，可忽略)</strong><br />\n1. 非常轻量级的Blog程序，不加index的那个背景图，只有1M大小\n2. 功能修改，添加，删除极其简单，后期添加功能完全盲打，不需要调试，前端简洁，虽然有时候可能会崩溃\n3. Code量少，非常容易理解，所以非常适合二次开发\n4. 等等。。。。  </p>\n<p><strong>联系作者</strong><br />\nBlog程序出什么问题的话，可以在<code>Github</code>项目下留言</p>', '2017-03-24');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `post`
--
ALTER TABLE `post`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `post`
--
ALTER TABLE `post`
  MODIFY `id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
