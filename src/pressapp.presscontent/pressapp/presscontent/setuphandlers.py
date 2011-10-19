from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer

def addPressCenterMemberFolder(p):
    """ Setup a press center folder as member folder"""
    
    existing = p.keys()
    if 'presse-center' not in existing:
        item = createContentInContainer(p, 'pressapp.presscontent.presscenter',
                             id="presse-center",
                             title=u"Presse Center")
        item.reindexObject()
    mtool = getToolByName(p, 'portal_membership')
    mtool.memberareaCreationFlag = 1
    mtool.setMembersFolderById('presse-center')
    mtool.setMemberAreaType('pressapp.presscontent.pressroom')


def importVarious(context):
    """ Miscellanous steps import handle """
    
    if context.readDataFile('pressapp.presscontent-various.txt') is None:
        return
    portal = context.getSite()
    addPressCenterMemberFolder(portal)
