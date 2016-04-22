# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class JkanOrganization(Item):
    title = Field()
    logo = Field()
    website = Field()
    description = Field()
    official = Field()

class JkanDataset(Item):
    schema = Field()
    title = Field()
    source = Field()
    organization = Field()
    category = Field(serializer=list)
    notes = Field()
    resources = Field()
    maintainer = Field()
    maintainer_email = Field()

class JkanResource(Item):
    name = Field()
    url = Field()
    format = Field()
