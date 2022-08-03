import bs4
import markdownify
import regex
import requests


REQUEST_PARAMS = {'enterAgree': 1}
PARSER = 'lxml'

PROTOCOL = 'https:'
BASE_URL = PROTOCOL + '//www.hentai-foundry.com'

URL_PATTERN = regex.compile(r'www\.hentai-foundry\.com/\S*')


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

    if 'hentai-foundry.com/stories/user' in url:
        return 'story'
    elif 'hentai-foundry.com/pictures/user' in url:
        return 'image'
    else:
        return ''


def get_page(url):
    """Get content of an HF page.
    
    argument url: str
    
    returns: bs4.BeautifulSoup
    """
    
    r = requests.get(f'https://{url}', params=REQUEST_PARAMS)
    
    print(r.status_code, r.reason, url)
    
    return bs4.BeautifulSoup(r.text, features=PARSER)


def summarize_image(page):
    """Create summary of an HF image page.

    argument page: bs4.BeautifulSoup

    returns: see summarize_page()
    """

    summary = {}

    mainmenu = page.find('nav', attrs={'id': 'mainmenu'})
    summary['url'] = BASE_URL + mainmenu.find('form').get('action')

    picbox = page.find('section', attrs={'id': 'picBox'})
    pictitle = picbox.find('div', attrs={'class': 'boxtitle'})
    summary['title'] = pictitle.find('span', attrs={'class': 'imageTitle'}).get_text()
    user = pictitle.find('a')
    summary['user'] = user.get_text()
    summary['user_url'] = BASE_URL + user.get('href')
    summary['image'] = PROTOCOL + picbox.find('img').get('src')

    descriptionbox = page.find('section', attrs={'id': 'descriptionBox'})
    summary['user_icon'] = PROTOCOL + descriptionbox.find('img').get('src')
    description = descriptionbox.find('div', attrs={'class': 'picDescript'})
    summary['description'] = markdownify.markdownify(description.decode_contents())

    ratings = page.find('div', attrs={'class': 'ratings_box'}).find_all('span')
    summary['ratings'] = [r.get_text() for r in ratings]

    return summary


def summarize_story(page):
    """Create summary of an HF story page.

    argument page: bs4.BeautifulSoup

    returns: see summarize_page()
    """

    summary = {'image': ''}

    titlebar = page.find('div', attrs={'class': 'titlebar'})
    summary['title'] = titlebar.get_text()
    summary['url'] = BASE_URL + titlebar.find('a').get('href')

    storyinfo = page.find('td', attrs={'class': 'storyInfo'})
    user = storyinfo.find('a')
    summary['user'] = user.get_text()
    summary['user_url'] = BASE_URL + user.get('href')
    summary['user_icon'] = PROTOCOL + storyinfo.find('img').get('src')
    
    description = page.find('td', attrs={'class': 'storyDescript'})
    ratings = description.find('div', attrs={'class': 'ratings_box'}).find_all('span')
    summary['ratings'] = [r.get_text() for r in ratings]
    for div in description.find_all('div'):
        div.decompose()
    summary['description'] = markdownify.markdownify(description.decode_contents())

    return summary


SUMMARY_FUNCTIONS = {
    'image': summarize_image,
    'story': summarize_story,
}


def summarize_page(url):
    """Create summary of an HF page.

    argument url: str

    returns: dict with keys:
        description: str
        image: str
        ratings: list of str
        title: str
        url: str
        user: str
        user_icon: str
        user_url: str
    """

    page_type = classify_url(url)

    if page_type:
        page = get_page(url)
        return SUMMARY_FUNCTIONS[page_type](page)
    else:
        return {}