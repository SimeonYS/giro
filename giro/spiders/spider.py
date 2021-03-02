import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import GiroItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class GiroSpider(scrapy.Spider):
	name = 'giro'
	start_urls = ['http://www.girobank.cw/news']

	def parse(self, response):
		articles = response.xpath('//div[@class="girobox_intnav_news"]')
		for article in articles:
			date = article.xpath('.//em/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response,date):

		title = response.xpath('//div[@class="sfContentBlock"]/h2/text()').getall()
		title = ''.join([p.strip() for p in title if p.strip()])
		content = response.xpath('//div[@class="sf_colsIn sf_1col_1in_100"]/div[@class="sfContentBlock"]//text()[not (ancestor::h2)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=GiroItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
