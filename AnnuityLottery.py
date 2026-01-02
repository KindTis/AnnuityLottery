import re
import urllib.request
import requests
import io
import numpy as np
from bs4 import BeautifulSoup
from collections import defaultdict

class AnnuityLotteryAnalysis:
    def __init__(self):
        self.Round = 0
        self.NumUnitList = {}

    def UpdateRecentStats(self):
        self.Round = 0
        self.NumUnitList = {}

        # 1. Get Latest Round
        url_result = 'https://dhlottery.co.kr/pt720/result'
        try:
            req = urllib.request.Request(url_result, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                # Use utf-8 with replace to handle potential encoding issues gracefully
                html = response.read().decode('utf-8', errors='replace') 
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all occurrences of "N회" and take the maximum
                # This covers "제296회", "296회", etc.
                matches = re.findall(r'(\d+)회', soup.get_text())
                if matches:
                    rounds = [int(m) for m in matches]
                    self.Round = max(rounds)
                
        except Exception as e:
            print(f"Error fetching latest round: {e}")
            return

        if self.Round == 0:
             print("Could not detect latest round number. Exiting.")
             return

        print(f"Latest Round: {self.Round}")

        # 2. Download Excel
        excel_url = f"https://dhlottery.co.kr/pt720/excelDownpstPt720Info.do?srchStrPsltEpsd=1&srchEndPsltEpsd={self.Round}&srchExcelYn=Y"
        
        try:
            print(f"Downloading data from {excel_url}...")
            res = requests.get(excel_url)
            res.raise_for_status()

            import pandas as pd
            
            # Try reading as excel first
            df = None
            try:
                df = pd.read_excel(io.BytesIO(res.content), header=None)
            except Exception as xl_err:
                print(f"Excel parsing failed (read_excel), trying HTML: {xl_err}")
                dfs = pd.read_html(io.BytesIO(res.content), header=None)
                if dfs:
                    df = dfs[0]
                else:
                    raise ValueError("Could not read data frame.")

            if df is None:
                raise ValueError("Data frame is empty after reading.")

            # Find header row
            header_row_index = -1
            for i, row in df.iterrows():
                # Check for key columns in the row
                row_values = [str(val) for val in row.values]
                if any('조' in v for v in row_values) and any('당첨번호' in v for v in row_values):
                    header_row_index = i
                    break
            
            if header_row_index != -1:
                # Set the found row as header
                df.columns = df.iloc[header_row_index]
                df = df.iloc[header_row_index+1:].reset_index(drop=True)
            else:
                # Fallback: assume first row is header if keywords not found (less robust but backup)
                print("Warning: Could not detect header row containing '조' and '당첨번호'. Using first row.")
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)

            print("Excel Columns:", df.columns.tolist())
            
            # Map columns by finding match
            col_joe = next((c for c in df.columns if '조' in str(c)), None)
            col_nums = next((c for c in df.columns if '당첨번호' in str(c)), None)
            
            if not col_joe or not col_nums:
                print("Could not find '조' or '당첨번호' columns.")
                return

            # Initialize NumUnitList
            for i in range(7):
                self.NumUnitList[i] = defaultdict(int)

            # Iterate rows
            for index, row in df.iterrows():
                # Process '조' (Unit 0)
                try:
                    joe_val = int(row[col_joe])
                    self.NumUnitList[0][joe_val] += 1
                except:
                    pass
                
                # Process '당첨번호' (Units 1-6)
                try:
                    num_str = str(row[col_nums])
                    # If it's an integer, it might be 123 (missing leading zeros) if excel treated as number
                    # We need 6 digits.
                    num_str = num_str.zfill(6)
                    
                    if len(num_str) >= 6:
                        # Take last 6 digits just in case
                        digits = num_str[-6:]
                        for i, digit in enumerate(digits):
                            # i=0 -> 100k -> Unit 1
                            # i=5 -> 1 -> Unit 6
                            self.NumUnitList[i+1][int(digit)] += 1
                except:
                    pass
            
            print(f'{self.Round}회 연금 복권 취합 됨')
            print('---------------------------------------------------------------------------------')
            print('')

        except Exception as e:
            print(f"Error processing excel: {e}")


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
        return r[0]


if __name__ == "__main__":
    lotto = AnnuityLotteryAnalysis()
    lotto.UpdateRecentStats()
    lotto.AnalysisAll()