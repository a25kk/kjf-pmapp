from five import grok
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from jobtool.jobcontent import MessageFactory as _


class JobTypeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {_(u"Fulltime"): 'fulltime', _(u"Parttime"): 'parttime'}

        return SimpleVocabulary([SimpleTerm(value, title=title) for
                                title, value in TYPES.iteritems()])

grok.global_utility(JobTypeVocabulary,
                    name=u"jobtool.jobcontent.jobTypes")


class JobCategoryVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        CATS = {_(u"Education"): 'education',
                _(u"Philosophy"): 'philosophy',
                _(u"Administration"): 'administration',
                _(u"Care"): 'care',
                _(u"Medicine"): 'medicine',
                _(u"Internship"): 'internship',
                _(u"Other"): 'other'
                }

        return SimpleVocabulary([SimpleTerm(value, title=title) for
                                title, value in CATS.iteritems()])

grok.global_utility(JobCategoryVocabulary,
                    name=u"jobtool.jobcontent.jobCategory")


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
            _(u"sankt-nikolaus.de"):
            'e1ee49115859acafec2ba2e28f9a2c7b9b093561'}
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value in
                                sorted(DISTRIBUTORS.iteritems())])

grok.global_utility(DistributorsVocabulary,
                    name=u"jobtool.jobcontent.externalDistributors")
