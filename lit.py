import bs4
import regex


BASE_URL = 'https://literotica.com/s'
PARSER = 'lxml'

URL_PATTERN = regex.compile(r'literotica\.com/s/\S*')

AUTHOR_CLASS = 'y_eU'
ICON_CLASS = 'y_eR'
TAGS_CLASS = 'av_as'
TITLE_CLASS = 'j_eQ'
DESCRIPTION_CLASSES = [
    'aK_B',
    'bn_B',
]
WORDS_CLASSES = [
    'aK_ap',
    'bn_ap',
]


def find_urls(text):
    """Find Literotica URLs in a string.
    
    argument text: str
    
    returns: list of str OR []
    """

    return URL_PATTERN.findall(text)


def summarize_story(page):
    """Create summary of a Literotica story page.

    argument page: str (html)

    returns: dict with keys:
        'author': str
        'author_icon: str
        'author_url': str
        'description': str
        'tags': list of str
        'title': str
        'words': str
    """

    soup = bs4.BeautifulSoup(page, features=PARSER)
    
    summary = {}

    author = soup.find('a', attrs={'class': AUTHOR_CLASS})
    summary['author'] = author.get_text()
    summary['author_url'] = author.get('href')

    icon = soup.find('a', attrs={'class': ICON_CLASS})
    summary['author_icon'] = icon.find('img').get('src')

    summary['description'] = soup.find('div', attrs={'class': DESCRIPTION_CLASSES}).get_text()
    summary['title'] = soup.find('h1', attrs={'class': TITLE_CLASS}).get_text()

    tags = soup.find_all('a', attrs={'class': TAGS_CLASS})
    summary['tags'] = list({tag.get_text() for tag in tags})

    words = soup.find('span', attrs={'class': WORDS_CLASSES}).get_text()
    summary['words'] = words.split()[0]

    return summary
