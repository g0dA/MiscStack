# RpmOvalCheck

基于`OVAL`的针对`centos`的check，实际是针对`RedHat`的，但是因为`centos`不更新了然后只对比`version`不管`release`所以直接用`RedHat`的。

> `build.gradle`中配置了自动下载`xml`，如果内外网隔离导致下载失败的话可以注释掉手动放入文件。

# 用法

* test.java
```

public class test {
    public static void main(String[] args) throws Exception{
        RpmGet rpmGet=new RpmGet();

        String name = "dnsmasq";
        String version="2.66";
        String arch="x86_64";

        System.out.print(rpmGet.getCveDetail(name,version,arch));

    }
}
```
