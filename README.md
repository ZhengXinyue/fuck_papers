## 利用flask搭建的一个在线文献管理工具网站——Fuck Papers
### （参考李辉的《Flask Web开发实战》）
用户输入url，网站进行解析收录。(集成redis，celery做异步爬虫)  
并提供多种文献操作（分类，收藏，已评注，已读，最近浏览）     

websites supported now:    

https://arxiv.org/abs/xxxx  
http://de.arxiv.org/abs/xxxx        
https://www.biorxiv.org/10.1101/xxx (maybe 10.1101 can alse be replaced.)       

may be supported in the future:   
 
https://ieeexplore.ieee.org/document/xxxx   

Demo:   
http://121.89.174.101/about       

example:
![screenshot](https://github.com/ZhengXinyue/fuck_papers/blob/master/example.png) 

clone:
```
https://github.com/ZhengXinyue/fuck_papers
cd fuck_papers
```

with venv/virtualenv + pip:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt
```

generate fake data then run:
```
$ flask forge
$ flask run
* Running on http://127.0.0.1:5000/

default username: default_user        
default password: 123456
```

or:
```
$ flask forge --username your_name --password your_password  (length between 6 and 20)
```


then you need to a redis server which runs on port 6379(Do it yourself)     

start another terminal:
```
$ celery worker -A fuck_papers.celery -l info 
```

if you get error like 'expect 3 but got 1....'(on win10),  run this(maybe you need to pip install some package):   
```
$ celery worker -A fuck_papers.celery -l info -P eventlet 
```



## License
This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
