import scrapy
import re

from toronto_data_portal.items import JkanOrganization, JkanDataset, JkanResource


FILETYPE_RE = re.compile(r'.+?(:?\.(?P<filetype>[0-9a-zA-Z]+?))?$')

PSEUDONYMS = {
    'Accounting Services Division': 'Accounting Services',
    'Transportation Services, Cycling Infrastructure & Programs': 'Transportation Services',
    'Transportation Services, Right of Way Management': 'Transportation Services',
    'Transportation Services - Traffic Management Centre': 'Transportation Services',
    'Right-of-Way Management': 'Transportation Services',
    'Traffic Safety Unit, Traffic Management Centre, Transportation': 'Transportation Services',
    'Toronto Building Plan Review Section': 'Toronto Building',
    'Shelter Support & Housing Administration - Hostel Services': 'Shelter, Support & Housing Administration',
    'Shelter, Support and Housing Administration': 'Shelter, Support & Housing Administration',
    'Economic Development & Culture': 'Economic Development & Culture',
    'Economic Development, Culture and Tourism': 'Economic Development & Culture',
    'Economic Development & Culture Division, Event Marketing & Visitor Services': 'Economic Development & Culture',
    'Economic Development': 'Economic Development & Culture',
    'Toronto Employment & Social Services': 'Employment & Social Services',
    '311 Contact Centre': '311 Toronto',
    "City Clerk's Office - Corporate Information Management Services": "City Clerk's Office",
    'City Clerks': "City Clerk's Office",
    'City Clerk': "City Clerk's Office",
    "City Clerks Office, Election & Registry Services": "City Clerk's Office",
    "City Clerk's Office, Secretariat": "City Clerk's Office",
    'Toronto Public Health, Healthy Public Policy': 'Toronto Public Health',
    'Public Health - Healthy Environments Program': 'Toronto Public Health',
    'Toronto Children\u2019s Services': "Children's Services",
    'Municipal Licensing & Standards - Toronto Animal Services': 'Municipal Licensing & Standards',
    'Municipal Licensing and Standards': 'Municipal Licensing & Standards',
    'Municipal Licensing & Standards, Investigative Services': 'Municipal Licensing & Standards',
    'Urban Forestry': 'Parks, Forestry & Recreation',
    'Parks, Forestry and Recreation': 'Parks, Forestry & Recreation',
    'Parks, Forestry & Recreation - Urban Forestry': 'Parks, Forestry & Recreation',
    'Revenue Services (Utility Billing, Meter Services and Parking Tags Section)': 'Revenue Services',
}

class PortalSpider(scrapy.Spider):
    name = 'portal'
    start_urls = ['http://www1.toronto.ca/wps/portal/contentonly?vgnextoid=1a66e03bb8d1e310VgnVCM10000071d60f89RCRD']

    def __init__(self):
        self.datasets_d = {}

    def parse(self, response):
        for a in response.css('.datacatalogue article.row h4 a'):
            href = a.xpath('./@href').extract_first()
            dataset_url = response.urljoin(href)
            request = scrapy.Request(dataset_url, callback=self.parse_dataset)
            request.meta['categories'] = []

            dataset_name = a.xpath('./text()').extract_first().strip()
            self.datasets_d[dataset_name] = request

        for dataset_name, request in self.datasets_d.items():
            yield request

        #for a in response.xpath('//nav[contains(@class, "media")]//ul/ul/li/a'):
        #    category_url = response.urljoin(a.xpath('./@href').extract_first())
        #    category = a.xpath('./text()').extract_first()
        #    request = scrapy.Request(category_url, callback=self.parse_category)
        #    request.meta['category'] = category

        #    yield request

    def parse_category(self, response):
        for href in response.css('.datacatalogue article.row h4 a::attr(href)'):
            dataset_url = response.urljoin(href.extract())
            request = scrapy.Request(dataset_url, callback=self.parse_dataset)
            request.meta['category'] = response.meta['category']

            yield request

    def parse_dataset(self, response):
        item = JkanDataset()

        owner = response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Owner")]/following::dd[1]/text()').extract_first(),
        if owner:
            owner, = owner
            owner = owner.strip()
            owner = PSEUDONYMS.get(owner, owner)
            item['organization'] = owner

        maintainer_email = response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Contact")]/following-sibling::dd/a/text()').extract_first()
        if maintainer_email:
            item['maintainer_email'] = maintainer_email.strip()

        item['title'] = response.css('h1[property=name]::text').extract()[0].strip()
        item['maintainer'] = response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Contact")]/following-sibling::dd/text()').extract()[0].strip()
        item['resources'] = [dict(resource) for resource in self.parse_resources(response)]
        item['source'] = response.url
        item['category'] = []

        yield item

    def parse_resources(self, response):
        item = JkanResource()
        unknown_filetype = ''

        resource_section = response.xpath('//section[contains(@class, "panel-default")]')[0]
        for li in resource_section.xpath('.//li'):
            item['url'] = response.urljoin(li.css('a::attr(href)')[0].extract())
            item['format'] = re.match(FILETYPE_RE, item['url']).groupdict(unknown_filetype).get('filetype').upper()
            item['name'] = li.xpath('./a/text()').extract()[0].strip()

            yield item
