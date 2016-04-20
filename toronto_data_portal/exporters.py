import yaml
from scrapy.exporters import BaseItemExporter
from scrapy.utils.python import to_bytes


class JkanDatasetItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file

    def export_item(self, item):
        frontmatter = {
                'schema': 'default',
                'title': item['title'],
                'organization': item['owner'],
                'notes': '',
                'resources': item['resources'],
                'category': '',
                'maintainer': item['maintainer'],
                'maintainer_email': item['maintainer_email'],
                }
        content = ''
        content += '---\n'
        content += yaml.safe_dump(frontmatter, default_flow_style=False)
        content += '---\n'
        self.file.write(to_bytes(content))


class JkanOrganizationItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file

    def export_item(self, item):
        frontmatter = {
            'title': item['owner'],
            'description': None,
            'website': None,
            'logo': None,
        }
        content = ''
        content += '---\n'
        content += yaml.safe_dump(frontmatter, default_flow_style=False)
        content += '---\n'
        self.file.write(to_bytes(content))
