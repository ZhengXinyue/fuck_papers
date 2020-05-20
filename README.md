##利用flask搭建的一个在线文献管理工具网站——Fuck Papers
### （参考李辉的《Flask Web开发实战》）
用户输入url，网站进行解析收录。
先尝试支持https://arxiv.org/ ，例如https://arxiv.org/abs/2005.06800     
提供多种文献操作（分类，收藏，已评注，已读，最近阅读）     
    
Demo:   
Not yet     

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
or with Pipenv:
```
$ pipenv install --dev
$ pipenv shell
```
generate fake data then run:
```
$ flask forge
$ flask run
* Running on http://127.0.0.1:5000/
```

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
