import re
import urllib.request
import numpy as np
from bs4 import BeautifulSoup
from collections import defaultdict

class AnnuityLotteryAnalysis:
    def __init__(self):
        self.NumUnitList = {}

    def UpdateRecentStats(self):
        url = 'https://dhlottery.co.kr/gameResult.do?method=index720&wiselog=H_C_10_1'
        urllib.request.urlretrieve(url, 'AnnuityLotteryStats.html')
        with open('AnnuityLotteryStats.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            tables = soup.find_all(id='printTarget')
            numUnit = 0;
            for table in tables:
                trs = table.tbody.find_all('tr')
                self.NumUnitList[numUnit] = {}
                num = 0;
                for tr in trs:
                    tds = tr.find_all('td')
                    findNum = re.search('(\d)', tds[2].text).group(0)
                    self.NumUnitList[numUnit][num] = int(findNum)
                    num += 1
                numUnit += 1

    def AnalysisAll(self):
        result = np.zeros(len(self.NumUnitList), dtype=int)
        for i in range(1, len(self.NumUnitList)):
            result[i] = self.Analysis(i)
        print("이번주 연금 복권 번호")
        print('---------------------------------------------------------------------------------')
        print('십만\t| 만\t| 천\t| 백\t| 십\t| 일')
        print(f'{result[1]}\t| {result[2]}\t| {result[3]}\t| {result[4]}\t| {result[5]}\t| {result[6]}')

    def Analysis(self, unitNum, test=False):
        numList = self.NumUnitList[unitNum]
        diffNum = np.zeros(10, dtype=int)
        weightList = np.zeros(10)
        maxNum = 0
        minNum = 999
        sumDiff = 0
        for i in range(len(numList)):
            if numList[i] > maxNum:
                maxNum = numList[i]
            if numList[i] < minNum:
                minNum = numList[i]
        maxNum += ((maxNum - minNum) / 2)

        for i in range(len(numList)):
            diffNum[i] = maxNum - numList[i]
            sumDiff += diffNum[i]

        for i in range(len(numList)):
            weightList[i] = diffNum[i] / sumDiff

        v = np.arange(0, 10)
        r = np.random.choice(v, 1, p=weightList)

        title = {0: '조 단위', 1: '십만 단위', 2: '만 단위', 3: '천 단위', 4: '백 단위', 5: '십 단위', 6: '일 단위'}
        print('{0} 번호 출현 리스트 횟수'.format(title[unitNum]))
        print('---------------------------------------------------------------------------------')
        print('0\t| 1\t| 2\t| 3\t| 4\t| 5\t| 6\t| 7\t| 8\t| 9')
        print('---------------------------------------------------------------------------------')
        print(f'{numList[0]}\t| {numList[1]}\t| {numList[2]}\t| {numList[3]}\t| {numList[4]}\t| {numList[5]}\t| {numList[6]}\t| {numList[7]}\t| {numList[8]}\t| {numList[9]}')
        print(f'{weightList[0]:.3f}\t| {weightList[1]:.3f}\t| {weightList[2]:.3f}\t| {weightList[3]:.3f}\t| {weightList[4]:.3f}\t| {weightList[5]:.3f}\t| {weightList[6]:.3f}\t| {weightList[7]:.3f}\t| {weightList[8]:.3f}\t| {weightList[9]:.3f}')

        # 테스트
        if test == True:
            testL = np.zeros(10, dtype=int)
            rt = np.random.choice(v, 1000, p=weightList)
            for i in rt:
                testL[i] += 1
            print(f'{testL[0]}\t| {testL[1]}\t| {testL[2]}\t| {testL[3]}\t| {testL[4]}\t| {testL[5]}\t| {testL[6]}\t| {testL[7]}\t| {testL[8]}\t| {testL[9]}')

        print(f'추출값: {r}')
        print('')
        return r

if __name__ == "__main__":
    lotto = AnnuityLotteryAnalysis()
    lotto.UpdateRecentStats()
    lotto.AnalysisAll()