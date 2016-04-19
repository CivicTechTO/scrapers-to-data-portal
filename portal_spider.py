import scrapy

class PortalSpider(scrapy.Spider):
    name = 'portal'
    start_urls = ['http://www1.toronto.ca/wps/portal/contentonly?vgnextoid=1a66e03bb8d1e310VgnVCM10000071d60f89RCRD']

    def parse(self, response):
        for href in response.css('.datacatalogue article.row h4 a::attr(href)'):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_dataset)

    def parse_dataset(self, response):
        dataset = {
                'title': response.css('h1[property=name]::text').extract()[0],
                'owner': response.css('section.metadata dd:nth-of-type(1)::text').extract()[0],
                'maintainer': response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Contact")]/following-sibling::dd/text()').extract()[0],
                'maintainer_email': response.xpath('//section[@class="metadata"]//dt[contains(./text(), "Contact")]/following-sibling::dd/a/text()').extract()[0],
                'resources': list(self.parse_resources(response)),
                'url': response.url,
                }

        yield dataset

    def parse_resources(self, response):
        resource_section = response.xpath('//section[contains(@class, "panel-default")]')[0]
        for li in resource_section.xpath('.//li'):
            resource = {
                    'name': li.xpath('./a/text()').extract()[0],
                    'url': li.css('a::attr(href)')[0].extract(),
                    }
            yield resource

