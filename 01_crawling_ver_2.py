from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

from fake_useragent import UserAgent
ua = UserAgent()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
category = ['Policy', 'Bond', 'Global_Economy', 'China_Economy', 'IB', 'Stock', 'Real_Estate']

df_titles = pd.DataFrame()
re_title = re.compile('[^가-힣|a-z|A-Z|0-9|一-龥]')


for i in range(1, 41):

    # URL 접근
    url = 'https://news.einfomax.co.kr/news/articleList.html?page={}&total=139819&box_idxno=&sc_section_code=S1N17'.format(i)
    resp = requests.get(url, headers=headers)

    # 제목 태그 가져오기
    soup = BeautifulSoup(resp.text, 'html.parser')
    title_tags = soup.select('.list-titles')

    titles_1 = []
    for title_tag in title_tags:
        titles_1.append(re_title.sub(' ', title_tag.text))

    titles = []
    for i in titles_1:
        titles.append(i[:-5])
        # ex. [정책/금융] 이면 -7

    df_section_titles = pd.DataFrame(titles, columns=['title'])
    df_section_titles['category'] = category[-1]
    df_titles = pd.concat([df_titles, df_section_titles], axis='rows', ignore_index=True)

print(df_titles.head())

df_titles.to_csv('./crawling/news_Real_Estate_210204.csv')