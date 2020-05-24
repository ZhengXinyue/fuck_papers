from datetime import datetime

from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from celery.utils.log import get_task_logger

from fuck_papers.models import Paper, Category, Message, User
from fuck_papers.extensions import db
from fuck_papers import celery, flask_app


logger = get_task_logger(__name__)
URL_PARSERS = []


def register_url_parser(cls):
    URL_PARSERS.append(cls)
    return cls


class BaseParser(object):
    name = 'BaseParser'
    patterns = []

    def __init__(self, url):
        self._url = url
        self._title = None
        self._author = None
        self._abstract = None
        self._subject = None
        self._submit_info = None
        self.headers = {'User-Agent': UserAgent().random}

    @classmethod
    def url_match(cls, url):
        raise NotImplementedError

    def start_pip_line(self):
        paper = self.parse_url(self._url)
        self._title = self.get_title(paper)
        self._author = self.get_author(paper)
        self._abstract = self.get_abstract(paper)
        self._subject = self.get_subject(paper)
        self._submit_info = self.get_submit_info(paper)

    def parse_url(self, url):
        raise NotImplementedError

    def get_title(self, paper):
        raise NotImplementedError

    def get_author(self, paper):
        raise NotImplementedError

    def get_abstract(self, paper):
        raise NotImplementedError

    def get_subject(self, paper):
        raise NotImplementedError

    def get_submit_info(self, paper):
        raise NotImplementedError

    @property
    def url(self):
        return self._url

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def abstract(self):
        return self._abstract

    @property
    def subject(self):
        return self._subject

    @property
    def submit_info(self):
        return self._submit_info

    def __repr__(self):
        return '%s' % self.name


@register_url_parser
class ArxivParser(BaseParser):
    name = 'ArxivParser'
    patterns = ['http://de.arxiv.org/abs/', 'https://arxiv.org/abs/']

    def __init__(self, url):
        super().__init__(url)

    @classmethod
    def url_match(cls, url):
        for pattern in cls.patterns:
            if url.startswith(pattern):
                return True
        return False

    def parse_url(self, url):
        paper = BeautifulSoup(requests.get(url, headers=self.headers).text, 'html.parser')
        return paper

    def get_title(self, paper):
        try:
            element = paper.find('h1', class_='title mathjax')
            title = ''.join(list(element.strings)[1:]).strip()
        except:
            title = '未获取，你可以手动添加该内容。'
        return title

    def get_author(self, paper):
        try:
            element = paper.find('div', class_='authors')
            authors = ''.join(list(element.strings)[1:]).replace('\n', '')
        except:
            authors = '未获取，你可以手动添加该内容。'
        return authors

    def get_abstract(self, paper):
        try:
            element = paper.find('blockquote', class_='abstract mathjax')
            abstract = list(element.strings)[-1].strip()
        except:
            abstract = '未获取，你可以手动添加该内容。'
        return abstract

    def get_subject(self, paper):
        try:
            element = paper.find('span', class_='primary-subject')
            subject = element.string
        except:
            subject = '未获取，你可以手动添加该内容。'
        return subject

    def get_submit_info(self, paper):
        try:
            element = paper.find('div', class_='submission-history')
            infos = list(element.strings)[5:]
            submit_info = ''.join(infos).replace('\n', ' ').strip()
        except:
            submit_info = '未获取，你可以手动添加该内容。'
        return submit_info

    def __repr__(self):
        return '%s' % self.name


@register_url_parser
class BiorxivParser(BaseParser):
    name = 'BiorxivParser'
    patterns = ['https://www.biorxiv.org/content/']

    def __init__(self, url):
        super().__init__(url)

    @classmethod
    def url_match(cls, url):
        for pattern in cls.patterns:
            if url.startswith(pattern):
                return True
        return False

    def parse_url(self, url):
        paper = BeautifulSoup(requests.get(url, headers=self.headers).text, 'html.parser')
        return paper

    def get_title(self, paper):
        try:
            element = paper.find('h1', id='page-title')
            title = ''.join(list(element.strings)).strip()
        except:
            title = '未获取，你可以手动添加该内容。'
        return title

    def get_author(self, paper):
        try:
            element = paper.find('div', class_='highwire-cite-authors')
            names = list(element.strings)
            authors = ''.join([name for name in names if name != 'View ORCID Profile'])
        except:
            authors = '未获取，你可以手动添加该内容。'
        return authors

    def get_abstract(self, paper):
        try:
            element = paper.find('div', id='abstract-1')
            abstract = ''.join(list(element.strings)[1:]).strip()
        except:
            abstract = '未获取，你可以手动添加该内容。'
        return abstract

    def get_subject(self, paper):
        try:
            element = paper.find('span', class_='highwire-article-collection-term')
            subject = ''.join(list(element.stripped_strings))
        except:
            subject = '未获取，你可以手动添加该内容。'
        return subject

    def get_submit_info(self, paper):
        try:
            element = paper.find('div', class_='panel-pane pane-custom pane-1')
            submit_info = ''.join(list(element.stripped_strings)).replace('\xa0', ' ')
        except:
            submit_info = '未获取，你可以手动添加该内容。'
        return submit_info

    def __repr__(self):
        return '%s' % self.name


@register_url_parser
class IEEEParser(BaseParser):
    name = 'IEEEParser'
    patterns = ['https://ieeexplore.ieee.org/document/']

    def __init__(self, url):
        super().__init__(url)

    @classmethod
    def url_match(cls, url):
        for pattern in cls.patterns:
            if url.startswith(pattern):
                return True
        return False

    def parse_url(self, url):
        # this need to deal with js
        paper = None
        return paper

    def get_title(self, paper):
        pass

    def get_author(self, paper):
        pass

    def get_abstract(self, paper):
        pass

    def get_subject(self, paper):
        pass

    def get_submit_info(self, paper):
        pass


@celery.task
def create_paper_and_notify(url, category_id, current_user_id):
    with flask_app.app_context():
        available_parsers = [parser for parser in URL_PARSERS if parser.url_match(url)]
        user = User.query.get(current_user_id)
        if not user:
            return
        category = Category.query.filter_by(user=user).filter_by(id=category_id).first()
        if not category:
            return
        if len(available_parsers) > 0:
            for parser in available_parsers:
                if parser.url_match(url):
                    p = parser(url)
                    try:
                        p.start_pip_line()
                    except requests.exceptions.RequestException:
                        message = Message(
                            content='无法解析 %s，请检查此url，或稍后再试。' % url,
                            add_timestamp=datetime.utcnow(),
                            user=user
                        )
                        db.session.add(message)
                        db.session.commit()
                    else:
                        paper = Paper(
                            url=p.url,
                            title=p.title,
                            author=p.author,
                            abstract=p.abstract,
                            subjects=p.subject,
                            submit_time=p.submit_info,
                            user=user,
                            category=category
                        )
                        message = Message(
                            content='论文 %s(%s) 收录完成。' % (p.url, p.title),
                            add_timestamp=datetime.utcnow(),
                            user=user
                        )
                        db.session.add(paper)
                        db.session.add(message)
                        db.session.commit()
        else:
            message = Message(
                content='您输入的 %s 与标准格式不匹配，请输入格式正确的url。' % url,
                add_timestamp=datetime.utcnow(),
                user=user
            )
            db.session.add(message)
            db.session.commit()
