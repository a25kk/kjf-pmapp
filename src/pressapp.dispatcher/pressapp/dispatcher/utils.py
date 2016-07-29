# -*- coding: utf-8 -*-
from lxml import etree
from lxml import html


def postprocess_emailtemplate(content):
    """ Replace links in rendered email templates

    Prevent 404 errors and unnecessary redirects by making the protocol
    scheme relative in the first place

    Note: this might put of old email clients like lotus notes
    """
    content = content.strip()
    tree = html.document_fromstring(content)
    for node in tree.xpath('//*[@src]'):
        src = node.get('src')
        if src.startswith('http://kjf-presse.de'):
            url = src.replace('http://', 'https://')
            node.set('src', url)
    for node in tree.xpath('//*[@href]'):
        href = node.get('href')
        if href.startswith('http://kjf-presse.de'):
            url = href.replace('http://', 'https://')
            node.set('href', url)
    data = etree.tostring(tree,
                          pretty_print=True,
                          encoding="utf-8",
                          method='html')
    return data
