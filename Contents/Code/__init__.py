NAME = 'tvgry.pl'
BASE_URL = 'http://tvgry.pl'
GUIDE_URL = '%s/ajax/waypoint.asp?PART=1' % (BASE_URL)
TEMATY_URL = '%s/tematy.asp' % (BASE_URL)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'

import re

def RemoveCounts(str):
	return re.sub("\(([0-9]+)\)", "", str)
	
def SupplementURL(url):
	if (url[0] == '/'):
		return BASE_URL + url
	
	return url

	
####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	ObjectContainer.title2 = 'Telewizja dla graczy'
	ObjectContainer.user_agent = USER_AGENT
	
	HTTP.CacheTime = CACHE_1WEEK
	HTTP.Headers['User-Agent'] = USER_AGENT
	HTTP.Headers['Referer'] = 'http://tvgry.pl/'
	
	#Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
	
	ObjectContainer.view_group = 'Details'

###################################################################################################
@handler('/video/tvgry', NAME)
def MainMenu():
	return TopicsList(1)

def TopicsList(page_no):

	dir = ObjectContainer()
	
	page_url = TEMATY_URL + '?STRONA=' + str(page_no) if page_no > 1 else TEMATY_URL
	page = HTML.ElementFromURL(page_url, encoding = 'cp1250', cacheTime = 0)
	
	if page_no < 2:
		dir.add(
			DirectoryObject(
				key = Callback(MainPage, page_no = 1),
				title = 'Najnowsze',
				thumb = R('newest.png'),
				art = R('art-default.jpg')
			)
		)
		dir.add(
			DirectoryObject(
				key = Callback(MainPage, page_no = 1, popular = True),
				title = 'Popularne',
				thumb = R('popular.png'),
				art = R('art-default.jpg')
			)
		)
	
	for cat in page.xpath("//div[contains(@class, 'lista-w-kat')]/a"):
		title = RemoveCounts(cat.text_content().strip())
		thumb = SupplementURL(cat.xpath(".//img")[0].get('src'))
		url = cat.get('href')

		dir.add(
			DirectoryObject(
				key = Callback(Topic, url = url, page_no = 1),
				title = title,
				thumb = thumb.replace('N300', 'N1280'),
				art = thumb.replace('N300', 'N1280')
			)
		)

	for cat in page.xpath("//div[contains(@class, 'half-box promo-other')]"):
		title = RemoveCounts(cat.xpath(".//h2")[0].text_content().strip())
		thumb = SupplementURL(cat.xpath(".//img")[0].get('src'))
		url = cat.xpath('.//a')[0].get('href')
		
		try:
			lead = cat.xpath(".//p[contains(@class, 'lead')]")[0].text_content().strip()
		except:
			lead = None

		dir.add(
			DirectoryObject(
				key = Callback(Topic, url = url, page_no = 1),
				title = title,
				thumb = thumb.replace('N460', 'N1280'),
				art = thumb.replace('N460', 'N1280'),
				tagline = lead
			)
		)
		
	next_page = True
	try:
		check_next_page = page.xpath("//a[contains(@class, 'pagi-next')]")[0]
	except:
		next_page = False
		
	if next_page:
		dir.add(
			NextPageObject(
				key = Callback(TopicsList, page_no = page_no + 1),
				title = 'Dalej...'
			)
		)

	return dir
	
def Topic(url, page_no):
	dir = ObjectContainer()
	
	page_url = BASE_URL + '/' + url + '&STRONA=' + str(page_no) if page_no > 1 else BASE_URL + '/' + url
	page = HTML.ElementFromURL(page_url, encoding = 'cp1250', cacheTime = 0)
	
	for cat in page.xpath("//div[contains(@class, 'half-box promo')]"):
		title = RemoveCounts(cat.xpath(".//h2")[0].text_content().strip())
		thumb = SupplementURL(cat.xpath(".//img")[0].get('src'))
		art = thumb.replace('N460', 'N1280')
		video_url = BASE_URL + cat.xpath('.//a')[0].get('href')
		
		try:
			lead = cat.xpath(".//p[contains(@class, 'lead')]")[0].text_content().strip()
		except:
			lead = None

		dir.add(
			VideoClipObject(
				url = video_url,
				title = title,
				tagline = lead,
				thumb = Resource.ContentsOfURLWithFallback(art),
				art = Resource.ContentsOfURLWithFallback(art)
			)
		)
		
	next_page = True
	try:
		check_next_page = page.xpath("//a[contains(@class, 'pagi-next')]")[0]
	except:
		next_page = False
		
	if next_page:
		dir.add(
			NextPageObject(
				key = Callback(Topic, url = url, page_no = page_no + 1),
				title = 'Dalej...'
			)
		)

	return dir
	
def MainPage(page_no, popular = False):
	dir = ObjectContainer()
	
	if (page_no == 1):
		HTTP.Headers['Cookie'] = 'typlisty=1' if popular else ''

	page_url = BASE_URL + '/ajax/waypoint.asp?PART=' + str(page_no) if page_no > 1 else BASE_URL
	page = HTML.ElementFromURL(page_url, encoding = 'cp1250', cacheTime = 0)

	for movie in page.xpath("//div[contains(@id, 'movie-cnt-c-')]"):
		video_url = BASE_URL + movie.xpath(".//a[contains(@class, 'movie-link')]")[0].get('href')
		title = movie.xpath(".//h2[contains(@itemprop, 'name')]")[0].text_content().strip()
		summary = movie.xpath(".//p[contains(@itemprop, 'description')]")[0].text_content().strip()
		art_url = movie.xpath(".//img")[0].get('src')
		thumb_url = art_url.replace('N960', 'N1280')
	
		dir.add(
			VideoClipObject(
				url = video_url,
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(thumb_url),
				art = Resource.ContentsOfURLWithFallback(art_url)
			)
		)
		
	dir.add(
		NextPageObject(
			key = Callback(MainPage, page_no = page_no + 1, popular = popular),
			title = 'Dalej...'
		)
	)

	return dir