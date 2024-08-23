import argparse
import csv
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from .db_operations import insert_raw_review, insert_store
import traceback

GM_WEBPAGE = 'https://www.google.com/maps/'
MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 5

class GoogleMapsScraper:

    def __init__(self, debug=False):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.driver.close()
        self.driver.quit()
        return True

    def sort_by(self, url, ind):
        self.driver.get(url)
        self.__click_on_cookie_agreement()

        wait = WebDriverWait(self.driver, MAX_WAIT)

        clicked = False
        tries = 0
        while not clicked and tries < MAX_RETRY:
            try:
                menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'排序\']')))
                menu_bt.click()
                clicked = True
                print('Sorted!')
                time.sleep(3)
            except Exception as e:
                tries += 1
                self.logger.warn('Failed to click sorting button')

            if tries == MAX_RETRY:
                return -1

        recent_rating_bt = self.driver.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[ind]
        recent_rating_bt.click()

        time.sleep(5)

        return 0
    
    def get_N_reviews(self, total, store_id):
        n = 0
        while n < total:
            print(f'[Review {n}]')
            len_reviews = self.get_reviews(n, store_id)
            if n >= total:
                break
            n += len_reviews
        if n < total:
            print(f'Only {n} reviews scraped. Try increasing scroll and wait times.')

    def get_reviews(self, offset, store_id):
        for _ in range(MAX_SCROLLS):
            self.__scroll()
            time.sleep(0.5)

        time.sleep(4)
        self.__expand_reviews()

        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        rblock = response.find_all('div', class_='jftiEf fontBodyMedium')
        parsed_reviews = []
        for index, review in enumerate(rblock):
            if index >= offset:
                r = self.__parse(review)
                parsed_reviews.append(r)
                print(r)
                if r['caption'] != None :
                    self.__save_review_to_db(r, store_id)
                else:
                    print('---NO CAPTION---')

        return len(parsed_reviews)

    def get_account(self, url):
        self.driver.get(url)
        self.__click_on_cookie_agreement()
        time.sleep(2)
        resp = BeautifulSoup(self.driver.page_source, 'html.parser')
        place_data = self.__parse_place(resp, url)
        return place_data

    def __parse(self, review):
        item = {}
        try:
            id_review = review['data-review-id']
        except Exception as e:
            id_review = None

        try:
            username = review['aria-label']
        except Exception as e:
            username = None

        try:
            review_text = self.__filter_string(review.find('span', class_='wiI7pd').text)
        except Exception as e:
            review_text = None

        try:
            rating = float(review.find('span', class_='kvMYJc')['aria-label'].split(' ')[0])
        except Exception as e:
            rating = None

        try:
            relative_date = review.find('span', class_='rsqaWe').text
        except Exception as e:
            relative_date = None

        try:
            n_reviews = review.find('div', class_='RfnDt').text.split(' ')[3]
        except Exception as e:
            n_reviews = 0

        item['id_review'] = id_review
        item['caption'] = review_text
        item['relative_date'] = relative_date
        item['retrieval_date'] = datetime.now()
        item['rating'] = rating
        item['username'] = username
        item['n_review_user'] = n_reviews

        return item

    def __expand_reviews(self):
        buttons = self.driver.find_elements(By.CSS_SELECTOR,'button.w8nwRe.kyuRq')
        for button in buttons:
            self.driver.execute_script("arguments[0].click();", button)

    def __scroll(self):
        scrollable_div = self.driver.find_element(By.CSS_SELECTOR,'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

    def __get_logger(self):
        logger = logging.getLogger('googlemaps-scraper')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('gm-scraper.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def __get_driver(self):
        options = Options()
        if not self.debug:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notifications")
        options.add_argument("--accept-lang=en-GB")
        input_driver = webdriver.Chrome(service=Service(), options=options)
        input_driver.get(GM_WEBPAGE)
        return input_driver

    def __click_on_cookie_agreement(self):
        try:
            agree = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Reject all")]')))
            agree.click()
            return True
        except:
            return False

    def __filter_string(self, str):
        strOut = str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        return strOut
    
    def __save_review_to_db(self, review, store_id):
        try:
            insert_raw_review(
                store_id=store_id,
                text=review['caption'],
                relative_date=review['relative_date'],
                rating=review['rating'],
                user_name=review['username']
            )
            print(f"Inserted review: {review['id_review']}")
        except Exception as e:
            self.logger.error(f"Failed to insert review {review['id_review']}: {str(e)}")

ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'url_user', 'url_source']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=250, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--sort_by', type=str, default='newest', help='most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()
    # writer = csv_writer(args.source, args.sort_by)
    # 初始化資料庫
    # print('Initializing db...')
    # init_db()
    # print('Done.')
    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open(args.i, 'r') as urls_file:
            store_count = 1
            for url in urls_file:
                if args.place:
                    print(scraper.get_account(url))
                else:
                    error = scraper.sort_by(url, ind[args.sort_by])
                    if error == 0:
                        store_id = insert_store('test' + str(store_count), url)
                        n = 0
                        while n < args.N:
                            print(f'[Review {n}]')
                            len_reviews = scraper.get_reviews(n, store_id)
                            if n >= args.N:
                                break
                            n += len_reviews
                        if n < args.N:
                            print(f'Only {n} reviews scraped. Try increasing scroll and wait times.')
