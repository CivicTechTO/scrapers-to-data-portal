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

ORG_LOGOS = {
        'Toronto Public Library': 'https://pbs.twimg.com/profile_images/613701886332542976/LYqUsfK5_400x400.jpg',
        '311 Toronto': 'https://pbs.twimg.com/profile_images/1166094989/7241835f-5085-42e5-ba26-782176332e5e_400x400.jpg',
        'Fire Services': 'https://pbs.twimg.com/profile_images/2508679803/CBADGE_400x400.png',
        'Toronto Public Health': 'https://pbs.twimg.com/profile_images/3342712317/dd791e21d4a7a140b284a8cd533db848_400x400.jpeg',
        "Children's Services": 'https://pbs.twimg.com/profile_images/526469164651659264/eJCOnMU2_400x400.jpeg',
        'Geospatial Competency Centre': 'https://pbs.twimg.com/profile_images/499574134225907715/3ZqntHXB_400x400.jpeg',
        'City Planning': 'https://pbs.twimg.com/profile_images/378800000372590361/60a79d5a7044bd47ef162b2dca42aba1_400x400.jpeg',
        'Social Development, Finance & Administration': 'https://pbs.twimg.com/profile_images/378800000562670282/670cd1e2a68b34049ab32f55e48da4a5_400x400.jpegi',
        'Parks, Forestry & Recreation': 'https://pbs.twimg.com/profile_images/720968055153680384/lGArEG2p_400x400.jpg',
        'Employment & Social Services': 'https://pbs.twimg.com/profile_images/644235206/fb40_400x400.jpg',
        'Election Services': 'https://pbs.twimg.com/profile_images/596672804193316866/pq6LFk0W_400x400.jpg',
        }

ORG_LOGO_DEFAULT = 'https://pbs.twimg.com/profile_images/665208414969053185/uN82Bpqg_400x400.jpg'

class PortalSpider(scrapy.Spider):
    name = 'portal'
    start_urls = ['http://www1.toronto.ca/wps/portal/contentonly?vgnextoid=1a66e03bb8d1e310VgnVCM10000071d60f89RCRD']

    def __init__(self):
        self.datasets_d = {}
        self.seen_orgs = []

    def parse(self, response):
        # Create lookup dict of all datasets
        items_d = {}
        for article in response.xpath('//div[@class="datacatalogue"]//article'):
            href = article.xpath('./*/h4/a/@href').extract_first()
            dataset_url = response.urljoin(href)
            request = scrapy.Request(dataset_url, callback=self.parse_dataset)
            dataset_name = article.xpath('./*/h4/a/text()').extract_first().strip()
            notes = article.xpath('./div[1]/h4/following-sibling::p/text()').extract_first()

            item = JkanDataset()
            item['title'] = dataset_name
            item['category'] = []
            item['source'] = dataset_url
            item['notes'] = notes
            items_d[dataset_name] = item

        # Create list of all category links
        links = []
        for a in response.xpath('//nav[contains(@class, "media")]//ul/ul/li/a'):
            category = a.xpath('./text()').extract_first()
            category_url = response.urljoin(a.xpath('./@href').extract_first())
            links.append({ 'category': category, 'url': category_url })

        link_data = links.pop()
        request = scrapy.Request(link_data['url'], callback=self.parse_next_link)
        request.meta['category'] = link_data['category']
        request.meta['links'] = links
        request.meta['items_d'] = items_d

        yield request

    def parse_next_link(self, response):
        items_d = response.meta['items_d']
        links = response.meta['links']

        category = response.meta['category']

        for a in response.css('.datacatalogue article.row h4 a'):
            dataset_name = a.xpath('./text()').extract_first().strip()
            items_d[dataset_name]['category'].append(category)

        if len(links) > 0:
            link_data = links.pop()
            request = scrapy.Request(link_data['url'], callback=self.parse_next_link)
            request.meta['category'] = link_data['category']
            request.meta['links'] = links
            request.meta['items_d'] = items_d

            yield request
        else:
            # No more links so yield datasets
            for item in response.meta['items_d'].values():
                request = scrapy.Request(item['source'], callback=self.parse_dataset)
                request.meta['item'] = item
                yield request

    def parse_dataset(self, response):
        item = response.meta['item']

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

        if item['organization'] not in self.seen_orgs:
            self.seen_orgs.append(item['organization'])

            org = JkanOrganization()
            org['title'] = item['organization']
            org['logo'] = ORG_LOGOS.get(org['title'], ORG_LOGO_DEFAULT)
            org['official'] = True
            yield org

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
