# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from toronto_data_portal.exporters import JkanOrganizationItemExporter
from slugify import slugify


class JkanPipeline(object):

    def __init__(self):
        self.files = {}

    def process_item(self, item, spider):
        if item['title']:
            filename = slugify(item['title'])
            self.files[filename] = open('data/_datasets/%s.md' % filename, 'w+b')
            self.exporter = JkanOrganizationItemExporter(self.files[filename])
            self.exporter.start_exporting()
            self.exporter.export_item(item)
            self.exporter.finish_exporting()
            file = self.files.pop(filename)
            file.close()

            return item
        else:
            raise DropItem("Missing title in %s" % item)


