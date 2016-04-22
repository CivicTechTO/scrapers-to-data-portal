scrape:
	rm -f data/_*/*
	scrapy crawl portal
	cp -r data/_* /home/patcon/repos/jkan/

	rm data/open-data-catalogue-datasets.json
	scrapy runspider toronto_data_portal/spiders/portal.py -o data/open-data-catalogue-datasets.json
	mv data/open-data-catalogue-datasets.json data/open-data-catalogue-datasets.json.tmp
	cat data/open-data-catalogue-datasets.json.tmp | python -m json.tool > data/open-data-catalogue-datasets.json
	rm data/open-data-catalogue-datasets.json.tmp
