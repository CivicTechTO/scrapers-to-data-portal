# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from toronto_data_portal.exporters import JkanDatasetItemExporter, JkanOrganizationItemExporter
from slugify import slugify


class JkanPipeline(object):

    def __init__(self):
        self.seen_orgs = []
        self.files = {}

    def process_item(self, item, spider):
        if item['title']:
            dataset_slug = slugify(item['title'])
            self.files[dataset_slug] = open('data/_datasets/%s.md' % dataset_slug, 'w+b')
            self.exporter = JkanDatasetItemExporter(self.files[dataset_slug])
            self.exporter.start_exporting()
            self.exporter.export_item(item)
            self.exporter.finish_exporting()
            file = self.files.pop(dataset_slug)
            file.close()

            org_slug = slugify(item['owner'])
            if org_slug not in self.seen_orgs:
                self.files[org_slug] = open('data/_organizations/%s.md' % org_slug, 'w+b')
                self.exporter = JkanOrganizationItemExporter(self.files[org_slug])
                self.exporter.start_exporting()
                self.exporter.export_item(item)
                self.exporter.finish_exporting()
                file = self.files.pop(org_slug)
                file.close()

            return item
        else:
            raise DropItem("Missing title in %s" % item)


