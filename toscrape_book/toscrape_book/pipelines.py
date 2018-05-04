# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import pymysql
import redis
from scrapy import Item

class BookPipeline(object):
    review_rating_map={
        'One':1,
        'Two':2,
        'Three':3,
        'Four':4,
        'Five':5
    }
    def process_item(self, item, spider):
        rating=item.get('rating')
        if rating:
            item['rating']=self.review_rating_map[rating]
        return item


class MongoPipeline(object):
    def __init__(self,mongo_uri,mongo_db):
        self.mongo_uri=mongo_uri
        self.mongo_db=mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_DB_URI'),
            mongo_db=crawler.settings.get('MONGO_DB_NAME')
            )

    def open_spider(self,spider):
        self.client=pymongo.MongoClient(self.mongo_uri)
        self.db=self.client[self.mongo_db]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self,item,spider):
        self.db['toscrape_books'].insert(dict(item))
        return item

class MySqlPipeline(object):
    def open_spider(self,spider):
        db=spider.settings.get('MYSQL_NAME')
        host=spider.settings.get('MYSQL_HOST')
        #port=spider.settings.get('MYSQL_PORT')
        user=spider.settings.get('MYSQL_USER')
        passwd=spider.settings.get('MYSQL_PASSWORD')

        self.db_conn=pymysql.connect(db=db,host=host
                                     ,user=user,passwd=passwd,charset='utf8')

        self.db_cursor=self.db_conn.cursor()

    def close_spider(self,spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self,item,spider):
        self.insert_db(item)

        return item

    def insert_db(self,item):
        values=(
            item['upc'],
            item['name'],
            item['price'],
            item['num'],
            item['rating'],
            item['stock'],
        )

        sql='INSERT INTO books(upc,name,price,num,rating,stock) VALUES (%s,%s,%s,%s,%s,%s)'
        self.db_cursor.execute(sql,values)


class RedisPipeline(object):
    def open_spider(self,spider):
        db_host=spider.settings.get('REDIS_HOST')
        db_port=spider.settings.get('REDIS_PORT')
        db_index=spider.settings.get('REDIS_INDEX')

        #建立与数据库的链接
        self.db_conn=redis.StrictRedis(host=db_host,port=db_port,db=db_index)
        #数据在数据库中的键
        self.item_i=0

    def close_spider(self,spider):
        self.db_conn.connection_pool.disconnect()

    def process_item(self,item,spider):
        self.insert_db(item)

        return item

    def insert_db(self,item):
        if isinstance(item,Item):
            item=dict(item)

        self.item_i+=1
        self.db_conn.hmset('book:%s'%self.item_i,item)
