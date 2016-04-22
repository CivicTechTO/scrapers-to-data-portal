# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from toronto_data_portal.exporters import JekyllFrontmatterItemExporter
from toronto_data_portal.items import JkanOrganization, JkanDataset
from slugify import slugify

LOOKUP = {
        JkanDataset: '_datasets',
        JkanOrganization: '_organizations',
        }


class JkanPipeline(object):

    def __init__(self):
        self.files = {}

    def process_item(self, item, spider):
        if type(item) in [JkanDataset, JkanOrganization]:
            if item['title']:
                slug = slugify(item['title'])
                self.files[slug] = open('data/%s/%s.md' % (LOOKUP[type(item)], slug), 'w+b')
                self.exporter = JekyllFrontmatterItemExporter(self.files[slug])
                self.exporter.start_exporting()
                self.exporter.export_item(item)
                self.exporter.finish_exporting()
                file = self.files.pop(slug)
                file.close()
            else:
                raise DropItem("Missing title in %s" % item)

        return item
