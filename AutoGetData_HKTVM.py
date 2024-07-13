import datetime
import math
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

# Choose WebDriver (Chrome)
driver = webdriver.Chrome()

# put hktv mall link here 
driver.get("https://www.hktvmall.com/hktv/zh/search_a?keyword=%E9%A6%99%E6%B0%B4&page=0")

# wait WebDriverWait
wait = WebDriverWait(driver, 5)

# just a tracker
index = 1

# how many total page count , a count to help stop loop in the last page
Total_Page_element = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="search-result-wrapper"]/div/div[3]/div[3]/div/span'))
).text
page_TOP_num = int(re.search(r'\d+', Total_Page_element).group())

print (page_TOP_num )

# Webpage count tracker
web_page_count = 1

# make DataFrame
columns = ["Title", "Price", "Rate"]
data = pd.DataFrame(columns=columns)

while True:
    try:
        print(f"正在處理第 {web_page_count} 頁")
        # roll to the bottom to load full page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


        while True:
            try:

                open_page_btn = driver.find_element(By.XPATH, f'//*[@id="algolia-search-result-container"]/div/div/span[{index}]')
                open_page_btn.click()
                driver.switch_to.window(driver.window_handles[-1])
                
                time.sleep(2)
                #close add
                try:
                    click_add = driver.find_element(By.XPATH,'/html/body/div[2]/div[6]/div/i')
                    click_add.click()
                except:
                    pass
                # Get title
                try:
                    title = driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/div[2]/ul/li[2]/h1').text
                except:
                    title = "N/A"
                try:
                    #find_brand Name
                    product_name = driver.find_elements(By.XPATH, '//*[@id="breadcrumb"]/div[2]/ul/li[2]/h1')[0].text
                    brand_name = product_name.split(" - ")[0]
                except:
                    brand_name = 'N/A'
                try:
                    #fird price
                    price_text = driver.find_element(By.CLASS_NAME, 'price').text
                    price = price_text.split('\n')[0].strip('$')
                except:
                    price = "N/A"
                try:
                    #find Rate
                    rate = driver.find_element(By.CLASS_NAME, 'averageRating').text
                except:
                    rate = "N/A"
                # try:
                #      #help find discount 
                #     short_desc = driver.find_element(By.XPATH, "//span[contains(@class = 'short-desc')]").text
                # except:
                #     short_desc = "N/A"
                try:
                    origin = driver.find_elements(By.CLASS_NAME, 'productPackingSpec')[0].text
                    if '包裝' in origin:
                        origin = driver.find_elements(By.CLASS_NAME, 'productPackingSpec')[1].text
                    origin = origin.split(' ')[1]   
                except:
                    origin = "N/A"
                try: 
                    #open the graph and open 365 days
                    wait = WebDriverWait(driver, 1)
                    click_date = driver.find_element(By.XPATH, '//*[@id="pdp-graph-entrypoint-React"]/div/div[1]')
                    click_date.click()
                    click_year = driver.find_element(By.XPATH, '//*[@id="pdp-graph-entrypoint-React"]/div/div[2]/div/div[4]/div/div[5]')
                    click_year.click()
                    time.sleep(1)
                    action = webdriver.ActionChains(driver)

                    # Get the data points on the red line
                    data_points = driver.find_elements(By.XPATH, '//*[@id="pdp-graph-entrypoint-React"]/div/div[2]/div/div[3]/div[1]/div[2]/div[1]/svg/g[4]')
                    upload_date = driver.find_element(By.XPATH, '//*[@id="pdp-graph-entrypoint-React"]/div/div[2]/div/div[2]/div[1]/p[2]')
                    
                    #find the graph , detect red_line path 
                    line = driver.find_element(By.CLASS_NAME, 'recharts-cartesian-grid')
                    red_line = driver.find_element(By.CSS_SELECTOR, ".recharts-layer.recharts-line")
                    red_line_path = red_line.find_element(By.TAG_NAME, "path")
                    red_line_width = red_line_path.get_attribute("d")

                    
                    values = red_line_width.split(".")
                    Red_split = red_line_width.split("L")
                    time.sleep(1)

                    #get the red line number
                    for Red_number in Red_split:
                        if Red_number.startswith("M"):
                            Red_number_part, _ = Red_number[1:].split(",")
                            Red_number_output = math.ceil(float(Red_number_part))
                            round(Red_number_output)
                            
                    #move and point at graph get date       
                    action.move_to_element(line).move_by_offset(0, 0).perform()
                    Date_location = Red_number_output - 245

                    action.move_to_element(line).move_by_offset(Date_location, 0).perform()

                    time.sleep(1)

                    # small fix to get the date 
                    money_detect= driver.find_element(By.XPATH, '//*[@id="pdp-graph-entrypoint-React"]/div/div[2]/div/div[2]/div[2]').text
                    if "-" in money_detect  :
                        Date_location = Date_location + 1
                        action.move_to_element(line).move_by_offset(Date_location, 0).perform()

                    upload_date = upload_date.text
                except:
                    upload_date = "N/A"
                try:

                    date_month = datetime.datetime.strptime(upload_date, '%d/%m/%Y').date()
                    month = date_month.month

                    if 3 <= month <= 5:
                        season = "spring"
                    elif 6 <= month <= 8:
                        season = "summer"
                    elif 9 <= month <= 11:
                        season = "autumn"
                    else:
                        season = "winter"
                except:
                    season = "N/A"
                try :
                    today = datetime.date.today()

                    test_date_obj = datetime.datetime.strptime(upload_date, '%d/%m/%Y').date()

                    over_one_year= today - test_date_obj

                    if over_one_year.days > 364:
                        over_one_year_test = "more_then_1_year"   
                    else: 
                        over_one_year_test = "N/A"          
                except:
                    over_one_year_test = "N/A"
                time.sleep(1)
                try:
                    short_desc = "N/A"
                    if driver.find_element(By.XPATH, "//span[contains(@class, 'short-desc')]"):
                        span_element = driver.find_element(By.XPATH, "//span[contains(@class, 'short-desc')]")
                        p_elements = span_element.find_elements(By.TAG_NAME, "p")
                        p_texts = [p.text for p in p_elements]
                        short_desc = "\n".join(p_texts) 
                except:
                    short_desc = "N/A"
                    
                try:
                    full_desc = "N/A"
                    if driver.find_element(By.XPATH, '//*[@id="descriptionsTab"]/div[2]'):
                        div_element = driver.find_element(By.XPATH, '//*[@id="descriptionsTab"]/div[2]')
                        div_elements = div_element.find_elements(By.TAG_NAME, "div")
                        div_texts = [div.text for div in div_elements]
                        full_desc = "\n".join(div_texts)
                except:
                    full_desc = "N/A"

                try:
                    pattern = r"(?:前味[：:]|初味[：:]|香調[：:]|初調[：:]|前調是|[•*]?\s*前調[：:])(.*)"
                    match = re.findall(pattern, short_desc or full_desc)
                    if match:
                        front_note = match
                        front_note_str = ", ".join(front_note)
                    else:
                        front_note_str = "N/A"
                    if len(front_note_str) > 50:
                        pattern = r"初調[：:]|前味[：:]|前調[：:](.*)"
                        match = re.search(pattern, short_desc or full_desc)
                        if match:
                            front_note_str = match.group(1)
                except:
                    front_note_str = "N/A"
                    
                try :
                    pattern_mid = r"(?:中味[：:]|中調[：:]|中調是|[•*]?\s*中調[：:])(.*)"
                    match_mid = re.findall(pattern_mid, short_desc or full_desc)
                    if match_mid :
                        middle_note = match_mid 
                        middle_note_str = ", ".join(middle_note)
                    else:
                        middle_note_str  = "N/A" 
                    if len(middle_note_str) > 50:
                        pattern_mid = r"中味[：:]|中調[：:]|中調[：:](.*)"
                        match_mid  = re.search(pattern_mid, short_desc or full_desc)
                        if match_mid :
                            middle_note_str = match_mid.group(1)
                except:
                    middle_note_str  = "N/A"    

                try :
                    pattern_base = r"(?:後味[：:]|後味[：:]|後調[：:]|基調[：:]|後味是|後調是|[•*]?\s*後調[：:])(.*)"
                    match_base = re.findall(pattern_base, short_desc or full_desc)
                    if match_base:
                        base_note = match_base
                        base_note_str = ", ".join(base_note)
                    else:
                        base_note_str  = "N/A"
                    if len(base_note_str) > 50:
                        pattern_base = r"中味[：:]|中調[：:]|中調[：:](.*)"
                        match_base = re.search(pattern_base, short_desc or full_desc)
                        if match_base:
                            base_note_str = match_base.group(1)
                except:
                    base_note_str  = "N/A"
                    
                    
                    
                # add data to DataFrame
                new_row = pd.DataFrame({"Title": [title],"brand_name":[brand_name],"front_note":[front_note_str],"middle_note":[middle_note_str],"base_note":[base_note_str]
                                        , "Price": [price], "Rate": [rate], "Origin": [origin]
                                        , "upload_date": [upload_date], "season": [season], "over_one_year_test": [over_one_year_test]})
                data = pd.concat([data, new_row], ignore_index=True)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                index += 1
                
            except Exception as e:

                print(f"第 {web_page_count} 頁已經處理完所有產品或出現錯誤：", e)
                break

        # if no more page to click , BREAK
        web_page_count = web_page_count + 1
        print (f'{web_page_count}____________')
        print (page_TOP_num)
        # if get up to the max number of page , BREAK
        if web_page_count > page_TOP_num:
            break

        index = 1

        # Find next page button
        try:
            nextPageButton = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'paginationMenu_nextBtn')]")))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            nextPageButton.click()
            time.sleep(3)
            print ("Next _page _GO! ")
            
        except:
            print("已經到達最後一頁")
            break

    except Exception as e:
        print(f"已經處理完所有頁面或出現錯誤：", e)
        break

# close drive
driver.quit()

print(data)

#display(data) 

#use this in ipynb to output CSV file
#data.to_csv('HKTVMALL_DATE_TEXT.csv', index=False)
