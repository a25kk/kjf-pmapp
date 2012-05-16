from five import grok
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from pressapp.presscontent import MessageFactory as _


class DistributorsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        DISTRIBUTORS = {
            _(u"kjf-augsburg.de"):
                '5445caf06d034e95f474924fac5ec7607dd9dc82',
            _(u"josefinum.de"):
                '1982c4b16d9f292750c3d7924c296a918413f39a',
            _(u"kinderzentrum-augsburg.de"):
                'c643191e6ab591b3a896e35954cae269a1f3baeb',
            _(u"sanktelisabeth.de"):
                '5d01382073f2461fb31f1321821da02b54591546',
            _(u"sankt-georg-kempten.de"):
                'e1ee49115859acafec2ba2e28f9a2c7b9b093561',
            _(u"ejv-aichach-friedberg.de"):
                '60d99866dd53c6fb1754fb723619812a0f0ab2d0',
            _(u"ejv-augsburg.de"):
                '87b0342f80abe497f72943676b0fa4e2319f01b9',
            _(u"ejv-memmingen-unterallgaeu.de"):
                '5975ca7ee68ea80307c71fd05cb892c57691a120',
            _(u"ejv-ostallgaeu.de"):
                '421e5c8dbc1611a321c1757da6bcca3dd5d1bb20'}
        return SimpleVocabulary([SimpleTerm(value, title=title)
            for title, value in sorted(DISTRIBUTORS.iteritems())])

grok.global_utility(DistributorsVocabulary,
                    name=u"pressapp.presscontent.externalDistributors")
