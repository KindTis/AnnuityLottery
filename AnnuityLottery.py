import re
import urllib.request
from bs4 import BeautifulSoup

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
        print(self.NumUnitList)

if __name__ == "__main__":
    lotto = AnnuityLotteryAnalysis()
    lotto.UpdateRecentStats()