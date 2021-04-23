import json
import os
import time
import requests
from os.path import join, dirname
from dotenv import load_dotenv
from src.extractor.scrape import Scraper

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Scrape_aliexpress(Scraper):
    def __init__(self, **kwargs):
        self.item = kwargs['item']
        self.product_api = {}

    def get_data(self):
        global time_start
        time_start = time.time()
        api_source = "https://magic-aliexpress1.p.rapidapi.com/api/products/search"

        querystring = {"name": self.item, "page": "1"}

        headers = {
            'x-rapidapi-key': os.environ.get("x-rapidapi-key"),
            'x-rapidapi-host': os.environ.get("x-rapidapi-host-500-mo")
        }

        response = requests.request("GET", api_source, headers=headers, params=querystring)

        with open("json_responses.txt", "a") as json_file:
            json_file.write(str(response.text))
            json_file.write('\nNew request\n')

        return json.loads(str(response.text))

    def api_generator(self, json_data):

        response = json_data

        item_list = response['docs']
        api = {'data': []}

        for item in item_list:
            title = item['product_title']
            price_value = item['app_sale_price']
            price_curr = item['app_sale_price_currency']
            url = item['product_detail_url']

            try:
                shipping = item['metadata']['logistics']['logisticsDesc']
                rating_val = item['evaluate_rate']
                rating = str(rating_val) + '/5'
            except:
                shipping = None
                rating_val = 0
                rating = None

            api['data'].append({
                'title': title,
                'price_val': price_value,
                'price_curr': price_curr,
                'url': url,
                'rating_val': rating_val,
                'rating_over': 5,
                'rating': rating,
                'shipping': shipping,
                'short_url': 'www.aliexpress.com'
            })

        time_end = time.time()

        api.update({
            'details': {
                'exec_time': round((time_end - time_start), 2),
                'total_num': len(api['data'])
            }
        })

        return api

    def get_api(self):
        json_data = self.get_data()
        self.product_api = self.api_generator(json_data=json_data)

        return self.product_api
