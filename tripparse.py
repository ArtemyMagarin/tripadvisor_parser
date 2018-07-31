import re
import requests
from pprint import pprint
from bs4 import BeautifulSoup 

s = requests.session()


def getIdFromSoup(elem):
	return elem['data-reviewid']

def getIndexedUrl(url, index):
	return url.replace('Reviews-', 'Reviews-or{}-'.format(index))

def soupToDate(elem, mask="YYYY-MM-DD"):
	# YYYY-MM-DD
	text = elem['title']
	if not text:
		text = elem.text
	if not text:
		return ''

	year = re.findall(r'\d{4}', text)
	if year:
		year = year[0]
	else:
		return ''

	day = '0' + str(re.findall(r'\d{1,2}', text)[0])
	
	if "января" in text:
		month = '01'
	if "февраля" in text:
		month = '02'
	if "марта" in text:
		month = '03'
	if "апреля" in text:
		month = '04'
	if "мая" in text:
		month = '05'
	if "июня" in text:
		month = '06'
	if "июля" in text:
		month = '07'
	if "августа" in text:
		month = '08'
	if "сентября" in text:
		month = '09'
	if "октября" in text:
		month = '10'
	if "ноября" in text:
		month = '11'
	if "декабря" in text:
		month = '12'

	return mask.replace("YYYY", year).replace("MM", month).replace("DD", day[-2:])

def soupToRank(elem):
	return int(int(re.findall(r'\d{2}', elem['class'][1])[0])/10)

def getReviewIds(url):
	
	ids = []

	r = s.get(url)
	PUID = r.text[-38:-12].strip()

	soup = BeautifulSoup(r.text, "html.parser")

	ids += [getIdFromSoup(elem) for elem in soup.findAll('div', {'class': 'review-container'})]	

	lastIndex = int(soup.find('a', {'class': 'last'})['data-offset'])

	s.headers["user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
	s.headers["authority"] = "www.tripadvisor.ru"
	s.headers["method"] = "POST"
	s.headers["scheme"] = "https"
	s.headers["x-puid"] = PUID
	s.headers['x-requested-with'] = 'XMLHttpRequest'

	for index in range(10, lastIndex+1, 10):
		s.headers["path"] = getIndexedUrl(url, index).replace('https://www.tripadvisor.ru', '')

		r = s.post(getIndexedUrl(url, index), data={
				'reqNum': '1',
				'isLastPoll': 'false',
				'paramSeqId': '0',
				'changeSet': 'REVIEW_LIST',
				'puid': PUID,
			})
		soup = BeautifulSoup(r.text, "html.parser")
		ids += [getIdFromSoup(elem) for elem in soup.findAll('div', {'class': 'review-container'})]

	return ids


def getReviewsByIds(ids):
	data = {
		'reviews': ','.join(ids),
		'widgetChoice': 'EXPANDED_REVIEW_RESPONSIVE'
	}

	r = s.post("https://www.tripadvisor.ru/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS&metaReferer=Attraction_Review", data=data)
	
	soup = BeautifulSoup(r.text, "html.parser")

	texts, dates, rates = [], [], []
	texts += [elem.text for elem in soup.findAll('p', {'class': 'partial_entry'})]
	dates += [soupToDate(elem) for elem in soup.findAll('span', {'class': 'ratingDate'})]
	rates += [soupToRank(elem) for elem in soup.findAll('span', {'class': 'ui_bubble_rating'})]

	# IDK why but dates and rates duplicated
	del dates[1::2]
	del rates[1::2]

	result = []

	for d, r, t in zip(dates, rates, texts):
		result.append({
				'date': d,
				'rating': r,
				'text': t
			})

	return result
	
	
TEST_URL = 'https://www.tripadvisor.ru/Attraction_Review-g298507-d302241-Reviews-Trinity_Bridge-St_Petersburg_Northwestern_District.html'
ids = getReviewIds(TEST_URL)
pprint(getReviewsByIds(ids))






