# python+selenium
加载浏览器驱动
```
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()#加载系统的chromedriver
```
利用`chrome headless`实现对一个网页的爬取。
简单的注意事项：
1. 是否禁止加载图片
2. `disable-gpu`参数
3. `User-Agent`头的设置，否则默认的有`headless`标签
4. 启动的默认语言，建议为`lang=zh_CN.UTF-8`

> 还有代理一说，考虑到实用性，利用`socket代理`

说是`headless`实际上也就是提供了一个浏览器而已，实际逻辑上的实现还是依靠`webdriver`
* 初始化demo，即访问某个页面
```python
#!/usr/bin/env python2
# coding: utf-8
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()#加载系统的chromedriver
# 如果没有把chromedriver加入到PATH中,就需要指明路径 executable_path='/home/chromedriver'

prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs) #禁止加载图片信息
chrome_options.add_argument('--headless') #headless模式
chrome_options.add_argument('--disable-gpu') # 暂时需要，使用后消失
chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36')#添加UA头，否则默认为headlesschrome
chrome_options.add_argument('lang=zh_CN.UTF-8') #设置启动时默认语言为UTF-8
client = webdriver.Chrome(chrome_options=chrome_options)

client.get("http://victim.com/login/login.php")
content = client.page_source
print(content)
client.quit()
```
> 有个严重的问题就是`get`非常慢，因为涉及到资源请求，解析加载等问题，与`request`这样的请求还是不同，因此非常非常慢。添加一个资源超时的规避

```
from selenium.webdriver.common.keys import Keys
client.set_page_load_timeout(10) # in seconds
try: 
    client.get("")
except: 
    client.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
```

# 定位
> 可以通过正则的贪婪匹配，但是提供了定位的功能总是好的。

* id定位：find_element_by_id()
* name定位：find_element_by_name()
* class定位：find_element_by_class()
* tag定位：find_element_by_tag_name()
* link定位：find_element_by_link_text()
* partial link 定位： find_element_by_partial_link_text()
* Xpath定位
* CSS定位：find_element_by_css_selector()

实现几个功能`demo`
* 获取所有的css链接
```
for link in client.find_elements_by_tag_name("link"):
    print link.get_attribute('href')
```
> 可能会有其余的干扰，加一个后缀判断即可

* 获取所有图片链接
```
for link in client.find_elements_by_tag_name("img"):
    print link.get_attribute('src')
```

* 获取所有js链接
```
for link in client.find_elements_by_tag_name("script"):
    script_link = link.get_attribute('src')
    if len(script_link)>0:
        print script_link
```
> 有资源为空的情况，决定加个判断然后再输出，链接的获取基本如此

* 获取`form`表单信息
```
for form in client.find_elements_by_tag_name("form"):
    inputs_list = form.find_elements_by_tag_name('input')
    action_url = form.get_attribute('action')
    print action_url
    for inputs in inputs_list:
        print inputs.get_attribute('name')
```
> 表单形式的，就是获取一个`form`下所有的`input`信息

现在的问题就是针对`ajax`构造的`http请求`无法去泛量处理，只能定制化开发，所以这个还得后续研究才行。

* `socket5`代理
```
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
# 设置代理
chrome_options.add_argument('--proxy-server=socks5://localhost:1080')
chrome_options = webdriver.ChromeOptions()#加载系统的chromedriver
chrome_options.get('http://www.google.com')
``` 

# 参考
* [Python+Selenium（webdriver常用API](http://www.cnblogs.com/101718qiong/p/8250104.html)
* [ChromeOptions--禁止加载图片](https://blog.csdn.net/ircszwfcbvdgk234/article/details/78605052)
* [PYTHON 爬虫笔记七:Selenium库基础用法](https://www.cnblogs.com/darwinli/p/9450488.html)
* [获取当前页面的所有链接的四种方法对比（python 爬虫](https://www.cnblogs.com/hhh5460/p/5044038.html)
* [Python+Selenium学习笔记](http://baobiy.com/2018/10/23/Python+Selenium%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/)
* [这不是一篇爬虫教程](http://kissg.me/2016/06/02/not-a-tutorial-on-crawler/)
* [python selenium2 - webelement操作常用方法](https://www.jianshu.com/p/d22d563528ab)