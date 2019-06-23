# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeleniumdemoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()

    takeoffTime = scrapy.Field()
    landingTime = scrapy.Field()
    takeoffAirport = scrapy.Field()
    landingAirport = scrapy.Field()

    transferCity = scrapy.Field()
    transferCount = scrapy.Field()

    flight1 = scrapy.Field()
    flight2 = scrapy.Field()
    pass
