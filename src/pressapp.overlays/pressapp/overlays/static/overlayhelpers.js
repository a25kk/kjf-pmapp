/*
    Code that runs inside the iframe menu

    XXX: Way too many globals created; needs a namespace
    Globals exported:
        CURRENT_OVERLAY_TRIGGER
        PloneQuickUpload
        TinyMCEConfig
        contractMenu
        createCookie
        eraseCookie
        expandMenu
        forceContractMenu
        menu_offset
        menu_size,
        readCookie
        toggleMenu

*/

 /*jslint white:false, onevar:true, undef:true, nomen:false, eqeqeq:true,
   plusplus:true, bitwise:true, regexp:false, newcap:true, immed:true,
   strict:false, browser:true */
/*global jQuery:false, $:false, document:false, window:false, location:false,
  common_content_filter:false, TinyMCEConfig:false */


var CURRENT_OVERLAY_TRIGGER = null;

(function ($) {
    // jquery method to load an overlay
    $.fn.loadOverlay = function(href, data, callback) {
        $(document).trigger('startLoadOverlay', [this, href, data]);
        var self = $(this),
            $overlay = this.closest('.pb-ajax');

        if(self.length === 0){
            $overlay = $('div.overlay-ajax:visible div.pb-ajax');
            self = $overlay;
        }
        self.load(href, data, function () {
            $overlay[0].handle_load_inside_overlay.apply(this, arguments);
            if (callback !== undefined) {
                callback.apply(this, arguments);
            }
            $(document).trigger('endLoadOverlay', [this, href, data]);
        });
        return this;
    };

    $().ready(function () {
        $('a.overlayLink,.configlets a').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            // Add this to a link or button to make it close the overlay e.g.
            // on cancel without reloading the page
            closeselector: '.overlayCloseAction',
            formselector: 'form.overlayForm,form.edit-form,#document-base-edit,form#form',
            noform: 'reload', // XXX : this will probably need to get smarter
            config: {
                closeOnClick: false,
                top: 130,
                mask: {
                    color: '#000000',
                    opacity: 0.5
                },
                onBeforeLoad: function (e) {
                    $('.dropdownItems').slideUp();
                    this.getOverlay().addClass($(CURRENT_OVERLAY_TRIGGER).closest('li').attr('id') + '-overlay');
                    $(document).trigger('beforeOverlay', [this, e]);
                    if (this.getOverlay().find('#form-widgets-ILayoutAware-content').length > 0) {
                        $.deco.init();
                        $('body', window.document).css('overflow', 'hidden');
                    } else {
                        expandMenu();
                        return true;
                    }
                },
                onLoad: function (e) {
                    if (this.getOverlay().find('#form-widgets-ILayoutAware-content').length > 0) {
                        $(".overlay").hide();
                        $('body', window.document).css('overflow', 'auto');
                    }
                    $.plone.showNotifyFromElements($(".overlay"));
                    $(document).trigger('loadOverlay', [this, e]);
                    return true;
                },
                onClose: function (e) {
                    CURRENT_OVERLAY_TRIGGER = null;
                    $(document).trigger('closeOverlay', [this, e]);
                    forceContractMenu();
                    return true;
                }
            }
        });
        $(document).bind('beforeAjaxClickHandled', function(event, ele, api, clickevent){
            if(ele === CURRENT_OVERLAY_TRIGGER){
                return event.preventDefault();
            }else{
                if(CURRENT_OVERLAY_TRIGGER !== null){
                    var overlays = $('div.overlay:visible');
                    overlays.fadeOut(function(){ $(this).remove(); });
                }
                CURRENT_OVERLAY_TRIGGER = ele;

            }
        });

        $("a.overlayLink,.configlets a").live('click', function(){
            $(document).trigger('overlayLinkClicked', [this]);
            var url = $(this).attr("href");
            $(this).closest('#overlay-content').loadOverlay(url + ' ' + common_content_filter);
            return false;
        });
        $('.dropdownLink').bind('click', function (e) {
            if (menu_size === 'menu') {
                // iframe is collapsed
                expandMenu();
                $(this).nextAll('.dropdownItems').slideToggle();
            }
            else {
                $(this).nextAll('.dropdownItems').slideToggle(function () {
                    contractMenu();
                });
            }
            e.preventDefault();
        });
    });

    // workaround this MSIE bug :
    // https://dev.plone.org/plone/ticket/10894
    if (jQuery.browser.msie) {jQuery("#settings").remove();}

}(jQuery));

/**
 * Initialize tinymce
 */
$(document).bind('loadInsideOverlay', function() {
    $('textarea.mce_editable').each(function() {
        var config = new TinyMCEConfig($(this).attr('id'));
        config.init();
    });
});
