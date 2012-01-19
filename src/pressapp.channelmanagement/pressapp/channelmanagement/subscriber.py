from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.interface import invariant, Invalid

from z3c.form import group, field
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget

from pressapp.channelmanagement.vocabulary import ChannelSourceBinder

from pressapp.channelmanagement import MessageFactory as _


class ISubscriber(form.Schema):
    """
    A single recipient/subscriber object
    """
    title = schema.TextLine(
        title=_(u"Contact Title"),
        required=True,
    )
    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
    )
    contact = schema.TextLine(
        title=_(u"Contact Person"),
        required=False,
    )
    phone = schema.TextLine(
        title=_(u"Phone"),
        required=False,
    )
    mobile = schema.TextLine(
        title=_(u"Mobile Phone"),
        required=False,
    )
    fax = schema.TextLine(
        title=_(u"Fax"),
        required=False,
    )
    comment = schema.Text(
        title=_(u"Comment"),
        required=False,
    )
    form.widget(channel=AutocompleteMultiFieldWidget)
    channel = schema.List(
        title=_(u"Channels"),
        description=_(u"Please select the channels this recipient "
                      u"is subscribed to."),
        value_type=schema.Choice(
            title=_(u"Channel"),
            source=ChannelSourceBinder(),
        )
    )


class View(grok.View):
    grok.context(ISubscriber)
    grok.require('zope2.View')
    grok.name('view')
