from lxml import etree
from lxml import html


def postprocess_emailtemplate(content):
    content = content.strip()
    tree = html.document_fromstring(content)
    for node in tree.xpath('//*[@src]'):
        src = node.get('src')
        if src.startswith('https://'):
            url = src.replace('https://', 'http://')
            node.set('src', url)
    for node in tree.xpath('//*[@href]'):
        href = node.get('href')
        if href.startswith('https://'):
            url = href.replace('https://', 'http://')
            node.set('href', url)
    data = etree.tostring(tree,
                          pretty_print=True,
                          encoding="utf-8",
                          method='html')
    return data
