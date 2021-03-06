from five import grok
from plone import api

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from plone.i18n.normalizer import idnormalizer
from Products.CMFPlone.utils import safe_unicode

from jobtool.jobcontent import MessageFactory as _


class JobTypeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {_(u"Fulltime"): 'fulltime',
                 _(u"Parttime"): 'parttime',
                 _(u"Fulltime and Parttime"): 'fullandpart'}

        return SimpleVocabulary([SimpleTerm(value, title=title) for
                                title, value in TYPES.iteritems()])

grok.global_utility(JobTypeVocabulary,
                    name=u"jobtool.jobcontent.jobTypes")


class JobCategoryVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        CATS = {_(u"Education"): 'education',
                _(u"Psychology"): 'psychology',
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


class InstitutionsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        portal = api.portal.get()
        jobcenter = portal['jobcenter']
        # cats = catalog.uniqueValuesFor("institution")
        cats = jobcenter.institutions
        entries = []
        done = []
        for cat in cats:
            cat_unicode = safe_unicode(cat)
            cat_id = idnormalizer.normalize(cat_unicode)
            if cat_id not in done:
                entry = (cat_id, cat_unicode)
                entries.append(entry)
                done.append(cat_id)
        terms = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                 for pair in entries]
        return SimpleVocabulary(terms)


grok.global_utility(InstitutionsVocabulary,
                    name=u"jobtool.jobcontent.jobInstitutions")


class LocationsVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        portal = api.portal.get()
        jobcenter = portal['jobcenter']
        cats = jobcenter.locations
        entries = []
        done = []
        for cat in cats:
            cat_unicode = safe_unicode(cat)
            cat_id = idnormalizer.normalize(cat_unicode)
            if cat_id not in done:
                entry = (cat_id, cat_unicode)
                entries.append(entry)
                done.append(cat_id)
        terms = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                 for pair in entries]
        return SimpleVocabulary(terms)


grok.global_utility(LocationsVocabulary,
                    name=u"jobtool.jobcontent.jobLocations")
