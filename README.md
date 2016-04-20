# Toronto Data Portal Scraper

This scraper is a first attempt at scraping the datasets of the official
Toronto Data Catalogue into a format that can then be imported into a
community-maintained data portal.

For now, it does not actually fetch datasets, but simply URLs. We aspire
to cache and version the datasets in the future.

### Usage

```
mkvirtualenv toronto-portal --python=`which python3`
workon toronto-portal
pip install -r requirements.txt
scrapy crawl portal
```
