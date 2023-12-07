
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
import os


def webserver():
    # get直接返回，不再等待界面加载完成
    desired_capabilities = DesiredCapabilities.EDGE
    desired_capabilities["pageLoadStrategy"] = "none"

    # 设置微软驱动器的环境
    options = webdriver.EdgeOptions()
    # 设置浏览器不加载图片，提高速度
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    # 创建一个微软驱动器
    driver = webdriver.Edge(options=options)

    return driver

def open_page(driver, keyword):
    # 打开页面，等待两秒
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    time.sleep(2)

    # 修改属性，使下拉框显示
    opt = driver.find_element(By.CSS_SELECTOR, 'div.sort-list')  # 定位元素
    driver.execute_script("arguments[0].setAttribute('style', 'display: block;')", opt)  # 执行 js 脚本进行属性的修改；arguments[0]代表第一个属性

    # 鼠标移动到下拉框中的[通讯作者]
    ActionChains(driver).move_to_element(driver.find_element(By.CSS_SELECTOR, 'li[data-val="RP"]')).perform()

    # # 找到[关键词]选项并点击
    # WebDriverWait(driver, 100).until(
    #     EC.visibility_of_element_located((By.CSS_SELECTOR, 'li[data-val="KY"]'))).click()

    # 传入关键字
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '''//*[@id="gradetxt"]/dd[1]/div[2]/input'''))
    ).send_keys(keyword)

    # 点击搜索
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '''//*[@id="ModuleSearch"]/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/div[3]/input'''))
    ).click()

    print("正在搜索，请稍后...")

    # # 点击切换中文文献
    # WebDriverWait(driver, 100).until(
    #     EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/a[1]"))
    # ).click()

    # 获取总文献数和页数
    res_unm = WebDriverWait(driver, 100).until(EC.presence_of_element_located(
        (By.XPATH, '''//*[@id="countPageDiv"]/span[1]/em'''))
    ).text

    # 去除千分位里的逗号
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / 20) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")
    return res_unm

def get_info(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text
    except:
        return '无'
    
def get_choose_info(driver, xpath1, xpath2, str):
    try: 
        if WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath1))).text==str:
            return WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath2))).text
        else:
            return '无'
    except:
        return '无'

def crawl(driver, papers_need, theme):

    count = 1

    file_path = f"CNKI_{theme}.tsv"
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as file:
            lines = file.readlines()
            last_line = lines[-1].strip()
            count = int(last_line.split("\t")[0]) + 1
    
    for i in range((count-1) // 20):
        # 切换到下一页
        time.sleep(3)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='PageNext']"))).click()

    print(f"从第 {count} 条开始爬取\n")

    # 当爬取数量小于需求时，循环网页页码
    while count <= papers_need:
        # 等待加载完全，休眠3S
        time.sleep(3)

        title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        # 循环网页一页中的条目
        for i in range((count-1) % 20 + 1, 21):

            print(f"\n###正在爬取第 {count} 条(第{(count-1) // 20 + 1}页第{i}条)#######################################\n")

            try:
                term = (count-1) % 20 + 1  # 本页的第几个条目
                
                # 获取基础信息
                print('正在获取基础信息...')
                title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[2]'''
                author_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[3]'''
                source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[4]'''
                date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[5]'''
                database_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[6]'''
                quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[7]'''
                download_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[8]'''
                xpaths = [title_xpath, author_xpath, source_xpath, date_xpath, database_xpath, quote_xpath, download_xpath]
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                title, authors, source, date, database, quote, download = [future.result() for future in future_elements]
                if not quote.isdigit():
                    quote = '0'
                if not download.isdigit():
                    download = '0'
                print(f"{title} {authors} {source} {date} {database} {quote} {download}\n")
               
                # 点击条目
                title_list[i-1].click()
                
                # 获取driver的句柄
                n = driver.window_handles
                
                # driver切换至最新生产的页面
                driver.switch_to.window(n[-1])
                time.sleep(3)
                
                # 开始获取页面信息
                # 点击展开
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '''//*[@id="ChDivSummaryMore"]'''))
                    ).click()
                except:
                    pass
                
                # 获取作者单位
                print('正在获取institute...')
                try:
                    institute = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/div[3]/div/div/div[3]/div/h3[2]"))).text
                except:
                    institute = '无'
                print(institute+'\n')
                
                # 获取摘要、关键词、专辑、专题
                # 获取摘要
                print('正在获取abstract...')
                try:
                    abstract = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "abstract-text"))).text
                except:
                    abstract = '无'
                print(abstract+'\n')
                
                # 获取关键词
                print('正在获取keywords...')
                try:
                    keywords = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "keywords"))).text[:-1]
                except:
                    keywords = '无'      
                print(keywords+'\n')
                
                # 获取专辑
                print('正在获取publication...')
                xpaths = [
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/p")
                ]
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专辑：') for xpath1, xpath2 in xpaths]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                publication = next((result for result in results if result != '无'), '无')
                print(publication+'\n')
                
                # 获取专题
                print('正在获取topic...')
                xpaths = [
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/p"),
                    ("/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[2]/p")
                ]
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专题：') for xpath1, xpath2 in xpaths]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                topic = next((result for result in results if result != '无'), '无')
                print(topic+'\n')
                
                url = driver.current_url
                
                # 获取下载链接
                # link = WebDriverWait( driver, 10 ).until( EC.presence_of_all_elements_located((By.CLASS_NAME  ,"btn-dlcaj") ) )[0].get_attribute('href')
                # link = urljoin(driver.current_url, link)

                # 写入文件
                res = f"{count}\t{title}\t{authors}\t{institute}\t{date}\t{source}\t{publication}\t{topic}\t{database}\t{quote}\t{download}\t{keywords}\t{abstract}\t{url}".replace("\n", "") + "\n"

                try:
                    with open(file_path, 'a', encoding='gbk') as f:
                        f.write(res)
                        print('写入成功')
                except Exception as e:
                    print('写入失败:', str(e))
                    raise e
            except:
                print(f" 第{count} 条爬取失败\n")
                # 跳过本条，接着下一个
                continue
            
            finally:
                # 如果有多个窗口，关闭第二个窗口， 切换回主页
                n2 = driver.window_handles
                if len(n2) > 1:
                    driver.close()
                    driver.switch_to.window(n2[0])
                # 计数,判断需求是否足够
                count += 1
                if count == papers_need: break

        # 切换到下一页
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@id='PageNext']"))).click()
        
    print("爬取完毕！")


if __name__ == "__main__":
    
    keyword = "青少年抑郁"
    driver = webserver()
    
    # 设置所需篇数
    papers_need = 500
    res_unm = open_page(driver, keyword)
    
    # 判断所需是否大于总篇数
    papers_need = papers_need if (papers_need <= res_unm) else res_unm
    
    os.system("pause")
    
    # 开始爬取
    crawl(driver, papers_need, keyword)

    # 关闭浏览器
    driver.close()