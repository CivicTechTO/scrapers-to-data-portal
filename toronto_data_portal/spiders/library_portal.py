import scrapy
import re

from toronto_data_portal.items import JkanOrganization, JkanDataset, JkanResource

FILETYPE_RE = re.compile(r'.+?(:?\.(?P<filetype>[0-9a-zA-Z]+?))?$')


class LibraryPortalSpider(scrapy.Spider):
    name = 'library_portal'
    start_urls = ['http://opendata.tplcs.ca/']

    def __init__(self):
        pass

    def parse(self, response):
        elems = response.xpath('//dl[@class="def-list-library"]/*[self::dd or self::dt]')
        definitions = zip(elems[::2], elems[1::2])
        for dt, dd in definitions:
            if 'Z39.50' in dt.extract(): continue
            item = JkanDataset()
            item['organization'] = 'Toronto Public Library'
            item['source'] = 'http://opendata.tplcs.ca/'
            item['resources'] = []
            item['category'] = ['Community services']
            item['maintainer'] = 'Toronto Public Library, Planning, Policy and E-Service Delivery'
            item['maintainer_email'] = 'answerline@torontopubliclibrary.ca'

            unknown_filetype = ''

            dt_link = dt.xpath('.//@href').extract_first()

            dt_text = dt.xpath('.//text()').extract_first().strip()
            if not dt_text:
                dt_text = dt.xpath('.//strong/text()').extract_first().strip()
            item['title'] = dt_text


            if dt_link:
                dt_link = response.urljoin(dt_link)
                resource_format = re.match(FILETYPE_RE, dt_link).groupdict(unknown_filetype).get('filetype').upper()
                item['resources'].append({'name': 'Data', 'url': dt_link, 'format': resource_format})
            else:
                li_resources = dd.xpath('.//li')
                for li in li_resources:
                    resource_name = li.xpath('./a/text()').extract_first()
                    resource_url = li.xpath('./a/@href').extract_first()
                    resource_url = response.urljoin(resource_url)
                    resource_format = re.match(FILETYPE_RE, resource_url).groupdict(unknown_filetype).get('filetype').upper()

                    item['resources'].append({'name': resource_name, 'url': resource_url, 'format': resource_format})

            yield item
