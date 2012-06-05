from Acquisition import aq_inner
from five import grok
from plone.directives import form

from zope import schema
from zope.schema.vocabulary import getVocabularyRegistry
from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.app.component.hooks import getSite
from plone.app.textfield import RichText
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName

from plone.app.contentlisting.interfaces import IContentListing
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IAboveContent

from pressapp.presscontent import MessageFactory as _


class IPressRelease(form.Schema, IImageScaleTraversable):
    """
    A press release content type.
    """
    kicker = schema.TextLine(
        title=_(u"Kicker"),
        description=_(u"Enter optional kicker / teaser line."),
        required=False,
    )
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    subtitle = schema.TextLine(
        title=_(u"Subtitle"),
        description=_(u"Please enter an optional subtitle here."),
        required=False,
    )
    location = schema.TextLine(
        title=_(u"Location"),
        description=_(u"Provide a location for this press release that will "
                      u"be prepended to the main body text."),
        required=False,
    )
    text = RichText(
        title=_(u"Text"),
        required=True,
    )
    form.primary('image')
    image = NamedBlobImage(
        title=_(u"Image Attachment"),
        description=_(u"Upload an image for this press release. The "
                      u"image should be already optimized since sending "
                      u"a large image file via E-mail is not recommended"),
        required=True,
    )
    imagename = schema.TextLine(
        title=_(u"Image Title"),
        required=True,
    )
    caption = schema.TextLine(
        title=_(u"Image Attachment Caption"),
        description=_(u"Enter optional caption describing the image"),
        required=False,
    )
    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"Optional summary that is useful as a preview text "
                      u"in email clients that support this feature."),
        required=False,
    )
    archive = schema.Bool(
        title=_(u"Visible in Archive?"),
        description=_(u"Mark this press release as visible in the archive."),
        required=False,
        default=True,
    )
    distributor = schema.List(
        title=_(u"Selected Dsitributors"),
        description=_(u"Select external distributors to filter display in "
                      u"the press archive listing"),
        value_type=schema.Choice(
            title=_(u"Distributor"),
            vocabulary='pressapp.presscontent.externalDistributors',
        ),
        required=False,
    )


@grok.adapter(IPressRelease, name="archive")
@indexer(IPressRelease)
def archiveIndexer(context):
    """ Catalog indexer registered as an adapter """
    return context.archive


class View(grok.View):
    grok.context(IPressRelease)
    grok.implements(IViewView)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_files = len(self.contained_attachments()) > 0

    def has_channel_info(self):
        context = aq_inner(self.context)
        channel = getattr(context, 'channel', None)
        if channel:
            return True

    def channel_names(self):
        context = aq_inner(self.context)
        names = []
        registry = queryUtility(IRegistry)
        if registry:
            records = registry['pressapp.channelmanagement.channelList']
        channels = getattr(context, 'channel', None)
        for channel in channels:
            info = {}
            info['channel'] = channel
            try:
                channelname = records[channel]
            except KeyError:
                channelname = channel
            info['channelname'] = channelname
            names.append(info)
        return names

    def distributors(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        dist_vocab = vr.get(context,
                            'pressapp.presscontent.externalDistributors')
        distributor = context.distributor
        data = []
        if distributor:
            for item in distributor:
                info = {}
                term = dist_vocab.getTerm(item)
                info['title'] = term.title
                info['value'] = term.value
                data.append(info)
            return data

    def has_recipients_info(self):
        context = aq_inner(self.context)
        recipients = getattr(context, 'recipients', None)
        if recipients:
            return True

    def constructPreviewURL(self):
        context = aq_inner(self.context)
        portal = getSite()
        portal_url = portal.absolute_url()
        uuid = IUUID(context, None)
        url = portal_url + '/@@pressitem-view?uid=' + uuid
        return url

    def contained_attachments(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        items = catalog(portal_type=['pressapp.presscontent.fileattachment',
                                     'pressapp.presscontent.imageattachment',
                                     'Image'],
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1))
        results = IContentListing(items)
        return results


class Preview(grok.View):
    grok.context(IPressRelease)
    grok.require('zope2.View')
    grok.name('pressrelease-preview')


class AsHtmlView(grok.View):
    grok.context(IPressRelease)
    grok.require('zope2.View')
    grok.name('asHTML')

    def additional_data(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getMemberById(context.Creator())
        data = {}
        data['location'] = context.location
        data['img'] = self.getImageTag(context)
        data['date'] = context.Date()
        data['org'] = member.getProperty('organization', '')
        data['link'] = member.getProperty('home_page', '')
        return data

    def getImageTag(self, item):
        obj = item
        scales = getMultiAdapter((obj, self.request), name='images')
        scale = scales.scale('image', scale='mini')
        imageTag = None
        if scale is not None:
            imageTag = scale.tag()
        return imageTag

    def queryAttachments(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        items = catalog(portal_type=['pressapp.presscontent.fileattachment',
                                     'pressapp.presscontent.imageattachment'],
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1))
        #results = IContentListing(items)
        return items


class PressReleaseActions(grok.Viewlet):
    grok.name('pressapp.membercontent.PressReleaseActions')
    grok.context(IPressRelease)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()

    def homefolder_url(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        home_folder = member.getHomeFolder().absolute_url()
        return home_folder
