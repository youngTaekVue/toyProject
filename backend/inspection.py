# 수정할 부분
import selenium
from selenium import webdriver
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
driver.get('https://dhlottery.co.kr/store.do?method=topStore&pageGubun=L645')

fst_store = []
sec_store = []
drwNo = 262

while True:
    select_drw = Select(driver.find_element_by_id("drwNo"))
    try:
        time.sleep(0.5)
        select_drw.select_by_value(str(drwNo))
        driver.find_element_by_css_selector('.btn_common.mid.blu').click()

        # first store crowling
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.select('table.tbl_data.tbl_data_col > tbody')
        trs = tables[0].select('tr')
        for tr in trs:
            tds = tr.select('td')
            if not tr.select('.nodata'):
                fst_store.append([drwNo, tds[1].text, tds[2].text.strip(' \t\n'), tds[3].text])


        # second store crowling
        page = 1
        while True:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tables = soup.select('table.tbl_data.tbl_data_col > tbody')

            trs = tables[1].select('tr')
            for tr in trs:
                tds = tr.select('td')
                if not tr.select('.nodata'):
                    sec_store.append([drwNo, tds[1].text, tds[2].text])

            page = page + 1
            try:
                time.sleep(0.5)
                driver.find_element_by_xpath('//a[text()=' + str(page) + ']').click()
            except selenium.common.exceptions.NoSuchElementException:
                break


    except selenium.common.exceptions.NoSuchElementException:
        break

    drwNo = drwNo + 1

driver.close()



# Save data to excel format
import openpyxl

wb = openpyxl.Workbook()
fst_sheet = wb.active
fst_sheet.title = '1등 당첨점'

sec_sheet = wb.create_sheet('2등 당첨점')

for store in fst_store:
    fst_sheet.append(store)

for store in sec_store:
    sec_sheet.append(store)

wb.save('test.xlsx')