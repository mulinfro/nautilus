pysh：融合python和shell的脚本语言
=======

pysh使用python实现，语法大部分继承自python，在此基础增加了一些shell的语法特性。


pysh的特点
-------

1.  支持python的所有内置函数
2.  支持python的package管理机制，用法跟python的import用法一样；python文件及pysh文件都支持
3.  数据结构跟python一样，List， Dict， Tuple，True|False， String
4.  关键词列表: def, is, in, if, else, for, while, break, continue, return, lambda 
5.  操作符列表：and, or, not, +, -, *, /, %, =, :=, $, |, . , &>, &>>, >, >=, <, <=, !=, ==



新增的特性
----------------
1. 管道PIPE
2. IO重定向到文件的操作符
3. 调用shell原生命令的操作符
4. 偏函数定义
5. 使用end作为语句结束标识，不再需要严格的缩进
6. list切片，dict取list里所有对象

pysh支持的一些语法用例
-------
		[1,2,8,1:5, 10:1:-2]

