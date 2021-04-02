from selenium import webdriver
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup


def main(item, timeout, headless):
    if item:
        item = item
    else:
        return []
    timeout = timeout  # 0.4  # scroll timeout
    headless = headless  # False  # chrome start option(set False to see all actions )
    url = 'https://tap.az/elanlar?&keywords=' + item.replace(' ', '+')
    clean_url = 'https://tap.az/'

    # Starting chrome browser with defined options
    print(f'>> Starting Chrome in headless = {headless} mode..')
    options = ChromeOptions()
    options.add_argument("--window-size=1600, 490")
    options.headless = headless
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(30)

    start_time = time.time()

    print(f'>> Going to {url}..')
    driver.get(url)

    end1_time = time.time()

    # while loop will scroll down until it reaches the end of the page
    # this part is important, because dynamically loaded websites like tap.az
    # loads data while scrolling

    print('>> Scrolling pages until it reached the end of the page..')
    number_of_scrolls = 0
    reached_page_end = False
    last_height = driver.execute_script("return document.body.scrollHeight")
    while not reached_page_end:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(timeout)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            reached_page_end = True
        else:
            last_height = new_height
        number_of_scrolls += 1

    print('>> Getting page source..')
    final_page = driver.page_source

    end2_time = time.time()

    # the following code block will extract the part where the actual product data located
    # this is done because in tap.az there is 'vip elanlar' section, where they have
    # promotional products and we do not need them

    print('>> Extracting data from page source..')
    start_string = '<div class="js-endless-container products endless-products">'
    end_string = '<div class="pagination_loading">'
    main_html = str(final_page)[str(final_page).find(start_string):]
    main_html = main_html[:main_html.find(end_string)]

    product_api = []
    soup = BeautifulSoup(main_html, 'lxml')
    product_list = soup.select("div[class^=products-i]")

    for item in product_list:
        for link in item.find_all('a', target='_blank', href=True):
            try:
                base_url = clean_url + link['href']
                title = link.find('div', class_='products-name').text
                price = link.find('span', class_='price-val').text + link.find('span', class_='price-cur').text
            except:
                base_url = None
                title = None
                price = None

            product_api.append({
                'data': {
                    'title': title,
                    'price': price,
                    'url': base_url,
                    'rating': None,
                    'short_url': 'www.tap.az'
                },
                'total_num': '',
                'exec_time': ''
            })

    end_time = time.time()

    print('>> Quiting and closing the browser')
    driver.close()
    driver.quit()

    for num, i in enumerate(product_api):
        print(num, f"Title: {i['data']['title']}, Price: {i['data']['price']}")

    print('\n>> Full execution time:                      ', end_time - start_time)
    print('>> Time for resolving url and searching:     ', end1_time - start_time)
    print('>> Time for scrolling and loading full page: ', end2_time - end1_time)
    print('>> Number of total scrolls:                  ', number_of_scrolls)
    print('>> Time for fulfilling api list:             ', end_time - end2_time)
    print(">> Total items: ", len(product_api))

    return product_api