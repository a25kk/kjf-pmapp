from lxml import etree
from lxml import html


def cleanup_links(content):
    content = content.strip()
    tree = html.document_fromstring(content)
    for node in tree.xpath('//*[@src]'):
        url = node.get('src')
        if url.startswith('https://'):
            url.replace('https://', 'http://')
        node.set('src', url)
    for node in tree.xpath('//*[@href]'):
        href = node.get('href')
        if href.startswith('https://'):
            href.replace('https://', 'http://')
        node.set('href', href)
    data = etree.tostring(tree, pretty_print=False, encoding="utf-8")
    return data
