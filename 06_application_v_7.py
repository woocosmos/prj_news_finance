'''
예측값 가지고 해당 카테고리 페이지 들어가서 라이브 기사 출력
콤보 박스 5번으로 연결
'''


import sys

from PyQt5 import uic
from PyQt5.QtWidgets import *

from bs4 import BeautifulSoup
import requests
import re

import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pickle
from konlpy.tag import Okt
import time



form_window = uic.loadUiType('./news_classfication.ui')[0]


class Exam(QWidget, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = load_model('./news_finance.h5')
        self.stopwords = pd.read_csv('../datasets/stopwords.csv')
        self.setWindowTitle('Asia Economy Classification')
        with open('./news_token.pickle', 'rb') as f:
            self.token = pickle.load(f)
        self.predict_result = None
        pd.set_option('display.unicode.east_asian_width', True)

        # 하이퍼링크 이용해서 웹 페이지 열도록 설정
        self.live_news = [self.lbl_1, self.lbl_2, self.lbl_3, self.lbl_4, self.lbl_5,
                          self.lbl_6, self.lbl_7, self.lbl_8, self.lbl_9, self.lbl_10]
        for live in self.live_news:
            live.setOpenExternalLinks(True)

        # 함수 연결
        self.btn_input.clicked.connect(self.le_title_slot)
        self.cmb_list.currentIndexChanged.connect(self.cmb_list_slot)


        # 콤보 박스 세팅
        titles = ['채권/외환', '중국경제', '국제경제', 'IB/기업', '정책/금융', '부동산', '증권']
        for title in titles:
            self.cmb_list.addItem(title)



    def cmb_list_slot(self):
        #콤보 박스에서 선택된 것으로 실시간 뉴스 호출
        self.predict_result = self.cmb_list.currentText()
        self.lbl_result.setText('')
        self.live_slot()


    def le_title_slot(self):
        # 사용자가 입력한 내용 받아오기
        title = self.le_title.text()

        # 입력한 내용이 있을 때만
        if title == '':
            self.lbl_result.setText('기사 제목을 입력해주세요.')

        else:
            # 형태소 분석
            okt = Okt()
            title = okt.morphs(title)

            # 불용어, 한 글자 처리
            result = []
            for word in title:
                if (word not in self.stopwords) and len(word) > 1:
                    result.append(word)
            title = result
            title = ' '.join(title)

            # 토크나이징 (모델 기준 패딩)
            title = self.token.texts_to_sequences([title])
            title = pad_sequences(title, 17)

            # 예측 결과
            label = ['채권/외환', '중국경제', '국제경제', 'IB/기업', '정책/금융', '부동산', '증권']
            predict = self.model.predict(title)
            self.predict_result = label[np.argmax(predict)]

            # 결과 출력 및 함수 호출
            self.lbl_result.setText('이 기사는 "{}" 기사입니다.'.format(self.predict_result))
            self.live_slot()


    def live_slot(self):
        # 결과에 따라 url 셋팅
        dict_url = {'정책/금융': 15, '채권/외환': 16, '국제경제':4, '중국경제':18, 'IB/기업':7, '증권':2, '부동산':17}
        value = dict_url[self.predict_result]
        url_policy = "https://news.einfomax.co.kr/news/articleList.html?sc_section_code=S1N{}".format(value)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
        resp = requests.get(url_policy, headers=headers)

        # 태그 파싱
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 제목
        title_tags = soup.find_all(class_="clearfix")
        title_live = []
        for title in title_tags:
            title = title.get_text()
            if title[0:2] == '10':
                title = title[2:]
            else:
                title = title[1:]
            title_live.append(title)
        print(title_live)
        title_live = title_live[11:] # 인덱스 초기화
        print('제목 가져오기 성공')
        # print(title_live)

        # 링크
        url_tags = soup.find_all(class_="clearfix")
        url_live = []
        for link in url_tags:
            try:
                a = link.find("a")["href"]
                url_live.append(a)
            except:
                pass
        print(url_live)
        url_live = url_live[2:] # 인덱스 초기화
        print('링크 가져오기 성공')
        # print(url_live)

        # 세팅
        for k in range(10):
            try:
                urlLink = f'<a style="color:black;text-decoration:none;" href=\"https://news.einfomax.co.kr{url_live[k]}\">{title_live[k]}</a>'
                self.live_news[k].setText(urlLink)
            # 실시간 뉴스 없을시 공백처리
            except:
                self.live_news[k].setText('')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Exam()
    w.show()
    sys.exit(app.exec_())