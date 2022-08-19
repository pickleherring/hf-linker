import bs4
import markdownify
import regex


BASE_URL = 'https://www.hentai-foundry.com'
PARSER = 'lxml'

EMBEDDED_IMG_PATTERN = regex.compile(r'\[\**!\[\]\([^)]*\)\**\]\([^)]*\)')
EMPTY_LINES_PATTERN = regex.compile(r'\n\s*\n')
URL_PATTERN = regex.compile(r'www\.hentai-foundry\.com/\S*')

PAGE_TYPE_PATTERNS = {
    'image': regex.compile(r'www\.hentai-foundry\.com/pictures/user/[^/]+/[^/]+/[^/]+'),
    'story': regex.compile(r'www\.hentai-foundry\.com/stories/user/[^/]+/[^/]+/[^/]+.*'),
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

    returns: str
    """

    markdown = markdownify.markdownify(text)
    markdown = EMBEDDED_IMG_PATTERN.sub('', markdown)
    markdown = EMPTY_LINES_PATTERN.sub('\n\n', markdown)

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
    for div in description.find_all('div'):
        div.decompose()
    summary['description'] = clean_description(description.decode_contents())

    return summary