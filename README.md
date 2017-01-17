pysh：一个融合python和shell的语言
=======

pysh使用python实现，基础语法中大部分继承自python，在此基础增加了一些特殊特性。


pysh的特点
-------

1.支持python的所有内置函数
2.支持python的import的package里的函数和对象使用
3.语法上大部分继承自python，支持的python类型和对象包括：List， Dict， Tuple，True|False， String， def， is，in， if，for， while，break, continue, return, lambda (and, or, not, +, -, *, /, %)



新增的特性：
1 管道PIPE
2 IO重定向到文件的操作符
3 调用shell原生命令的操作符
3 shell命令与python对象的粘接
4 使用end作为语句结束标识，不再需要严格的缩进


pysh支持的一些语法用例
-------