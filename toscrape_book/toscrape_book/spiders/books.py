# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from toscrape_book.items import BooksItem

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    #书籍列表页面解析
    def parse(self, response):
        #提取每本书的连接
        le=LinkExtractor(restrict_css='article.product_pod h3')
        links=le.extract_links(response)
        for link in links:
            yield scrapy.Request(url=link.url,callback=self.parse_books)#回调函数，将每本书的链接交给书籍解析函数来处理

        #提取下一页链接
        le=LinkExtractor(restrict_css='ul.pager li.next')
        links=le.extract_links(response)
        if links:
            next_url=links[0].url
            yield scrapy.Request(url=next_url,callback=self.parse)

     #书籍解析函数       
    def parse_books(self,response):
        book=BooksItem()
        sel=response.css('div[class*=product_main]')
        book['name']=sel.xpath('./h1/text()').extract_first()
        book['price']=sel.css('p.price_color::text').extract_first()
        book['rating']=sel.css('p[class*=star-rating]::attr(class)').re_first('star-.*?([A-Z][a-z]+)')
            #book['rating']=sel.xpath('.//p[contains(@class,"star-rating")]').re_first('star-.*?([A-Z][a-z]+)')
        sell=response.css('table[class*=table-striped]')
        book['upc']=sell.xpath('.//tr[1]/td/text()').extract_first()
        book['stock']=sell.xpath('.//tr[6]/td/text()').re_first('\((\d+).*?ble\)')
        book['num']=sell.xpath('.//tr[last()]/td/text()').extract_first()
        yield book




