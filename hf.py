import re

import bs4
import markdownify


BASE_URL = 'https://www.hentai-foundry.com'
PARSER = 'lxml'

CONVERT_TAGS = [
    'a',
    'b',
    'br',
    'em',
    'i',
    'strong',
]

EMPTY_LINES_PATTERN = re.compile(r'\n[\s*]*\n')
REPEATED_WHITESPACE_PATTERN = re.compile(r' {2,}')
URL_PATTERN = re.compile(r'www\.hentai-foundry\.com/\S*')

PAGE_TYPE_PATTERNS = {
    'image': re.compile(r'www\.hentai-foundry\.com/pictures/user/[^/]+/[^/]+/[^/]+'),
    'chapter': re.compile(r'www\.hentai-foundry\.com/stories/user/[^/]+/[^/]+/[^/]+/[^/]+/Chapter[^/]+/.*'),
    'story': re.compile(r'www\.hentai-foundry\.com/stories/user/[^/]+/[^/]+/[^/]+.*'),
}


def find_urls(text):
    """Find HF URLs in a string.

    argument text: str

    returns: list of str OR []
    """

    return URL_PATTERN.findall(text)


def classify_url(url):
    """Classify a HF URL as image or story.

    argument url: str

    returns: str ('', 'image', 'story')
    """

    for label, pattern in PAGE_TYPE_PATTERNS.items():
        if pattern.search(url):
            return label

    return ''


def clean_description(text):
    """Clean up image/story description text and convert to markdown.

    argument text: str

    returns: str (markdown)
    """

    markdown = markdownify.markdownify(text, convert=CONVERT_TAGS)
    markdown = EMPTY_LINES_PATTERN.sub('\n\n', markdown)
    markdown = REPEATED_WHITESPACE_PATTERN.sub(' ', markdown)

    return markdown


def summarize_image(page):
    """Create summary of an HF image page.

    argument page: str (html)

    returns: dict with keys:
        'description': str
        'image': str
        'ratings': list of str
        'title': str
        'url': str
        'user': str
        'user_icon: str
        'user_url': str
    """

    soup = bs4.BeautifulSoup(page, features=PARSER)

    summary = {}

    mainmenu = soup.find('nav', attrs={'id': 'mainmenu'})
    summary['url'] = BASE_URL + mainmenu.find('form').get('action')

    picbox = soup.find('section', attrs={'id': 'picBox'})
    pictitle = picbox.find('div', attrs={'class': 'boxtitle'})
    summary['title'] = pictitle.find('span', attrs={'class': 'imageTitle'}).get_text()
    user = pictitle.find('a')
    summary['user'] = user.get_text()
    summary['user_url'] = BASE_URL + user.get('href')
    summary['image'] = 'https:' + picbox.find('img').get('src')

    descriptionbox = soup.find('section', attrs={'id': 'descriptionBox'})
    summary['user_icon'] = 'https:' + descriptionbox.find('img').get('src')
    description = descriptionbox.find('div', attrs={'class': 'picDescript'})
    summary['description'] = clean_description(description.decode_contents())

    ratings = soup.find('div', attrs={'class': 'ratings_box'}).find_all('span')
    summary['ratings'] = [r.get_text() for r in ratings]

    return summary


def summarize_story(page):
    """Create summary of an HF story page.

    argument page: str (html)

    returns: see summarize_image()
    """

    soup = bs4.BeautifulSoup(page, features=PARSER)

    summary = {'image': ''}

    titlebar = soup.find('div', attrs={'class': 'titlebar'})
    summary['title'] = titlebar.get_text()
    summary['url'] = BASE_URL + titlebar.find('a').get('href')

    storyinfo = soup.find('td', attrs={'class': 'storyInfo'})
    user = storyinfo.find('a')
    summary['user'] = user.get_text()
    summary['user_url'] = BASE_URL + user.get('href')
    summary['user_icon'] = 'https:' + storyinfo.find('img').get('src')

    description = soup.find('td', attrs={'class': 'storyDescript'})
    ratings = description.find('div', attrs={'class': 'ratings_box'}).find_all('span')
    summary['ratings'] = [r.get_text() for r in ratings]
    description.find('div', attrs={'class': 'storyRead'}).decompose()
    description.find('div', attrs={'class': 'storyCategoryRating'}).decompose()
    summary['description'] = clean_description(description.decode_contents())

    return summary


def summarize_chapter(page):
    """Create summary of an HF story chapter.

    argument page: str (html)

    returns: see summarize_image()
    """

    soup = bs4.BeautifulSoup(page, features=PARSER)

    summary = {'image': ''}

    chapterbox = soup.find('section', attrs={'id': 'viewChapter'})
    chaptertitle = chapterbox.find('div', attrs={'class': 'boxtitle'})
    summary['title'] = chaptertitle.get_text()

    titlebar = soup.find('div', attrs={'class': 'titlebar'})
    summary['url'] = BASE_URL + titlebar.find('a').get('href')

    storyinfo = soup.find('td', attrs={'class': 'storyInfo'})
    user = storyinfo.find('a')
    summary['user'] = user.get_text()
    summary['user_url'] = BASE_URL + user.get('href')
    summary['user_icon'] = 'https:' + storyinfo.find('img').get('src')

    description = soup.find('td', attrs={'class': 'storyDescript'})
    ratings = description.find('div', attrs={'class': 'ratings_box'}).find_all('span')
    summary['ratings'] = [r.get_text() for r in ratings]
    description.find('div', attrs={'class': 'storyRead'}).decompose()
    description.find('div', attrs={'class': 'storyCategoryRating'}).decompose()

    excerpt = chapterbox.find('div', attrs={'class': 'boxbody'})
    summary['description'] = clean_description(excerpt.decode_contents()[:250]) + '...'

    return summary
