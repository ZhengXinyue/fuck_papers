from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

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

    @property
    def paper_info(self):
        d = dict()

        d['url'] = self._url
        d['title'] = self._title
        d['author'] = self._author
        d['abstract'] = self._abstract
        d['subjects'] = self._subject
        d['submit_info'] = self._submit_info

        return d

    def parse_url(self, url):
        paper = BeautifulSoup(requests.get(url, headers=self.headers).text, 'html.parser')
        return paper

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

    def get_title(self, paper):
        element = paper.find('h1', class_='title mathjax')
        title = list(element.strings)[-1].strip()
        return title

    def get_author(self, paper):
        element = paper.find('div', class_='authors')
        authors = ''.join(list(element.strings)[1:]).replace('\n', '')
        return authors

    def get_abstract(self, paper):
        element = paper.find('blockquote', class_='abstract mathjax')
        abstract = list(element.strings)[-1].strip()
        return abstract

    def get_subject(self, paper):
        element = paper.find('span', class_='primary-subject')
        subject = element.string
        return subject

    def get_submit_info(self, paper):
        element = paper.find('div', class_='submission-history')
        infos = list(element.strings)[5:]
        submit_info = ''.join(infos).replace('\n', ' ').strip()
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


def create_paper(url):
    for parser in URL_PARSERS:
        if parser.url_match(url):
            p = parser(url)
            p.start_pip_line()
            return p.paper_info
    return None


if __name__ == '__main__':
    article = create_paper('http://de.arxiv.org/abs/2005.10791')
    print(article)
