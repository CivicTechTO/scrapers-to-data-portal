import yaml
from scrapy.exporters import BaseItemExporter
from scrapy.utils.python import to_bytes


class JekyllFrontmatterItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file

    def export_item(self, item):
        content = ''
        content += '---\n'
        content += yaml.dump(dict(item), default_flow_style=False)
        content += '---\n'
        self.file.write(to_bytes(content))
