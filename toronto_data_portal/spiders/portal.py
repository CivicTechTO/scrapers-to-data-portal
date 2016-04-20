import scrapy
import re


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

    def parse(self, response):
        for href in response.css('.datacatalogue article.row h4 a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_dataset)

    def parse_dataset(self, response):
        owner = response.css('section.metadata dd:nth-of-type(1)::text').extract()[0].strip()
        owner = PSEUDONYMS.get(owner, owner)
        dataset = {
                'title': response.css('h1[property=name]::text').extract()[0].strip(),
                'owner': owner,
                'maintainer': response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Contact")]/following-sibling::dd/text()').extract()[0].strip(),
                'maintainer_email': response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Contact")]/following-sibling::dd/a/text()').extract()[0].strip(),
                'resources': list(self.parse_resources(response)),
                'url': response.url,
                }

        yield dataset

    def parse_resources(self, response):
        resource_section = response.xpath('//section[contains(@class, "panel-default")]')[0]
        for li in resource_section.xpath('.//li'):
            url = response.urljoin(li.css('a::attr(href)')[0].extract())
            unknown_filetype = ''
            filetype = re.match(FILETYPE_RE, url).groupdict(unknown_filetype).get('filetype').upper()
            resource = {
                    'name': li.xpath('./a/text()').extract()[0].strip(),
                    'url': url,
                    'format': filetype,
                    }
            yield resource


