# -*- coding: utf-8 -*-
import re
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
    regex = '^(https?|ftp)://'
    for node in tree.xpath('//*[@src]'):
        src = node.get('src')
        url = re.sub(regex, '//', src)
        node.set('src', url)
    for node in tree.xpath('//*[@href]'):
        href = node.get('href')
        url = re.sub(regex, '//', href)
        node.set('href', url)
    data = etree.tostring(tree,
                          pretty_print=True,
                          encoding="utf-8",
                          method='html')
    return data
