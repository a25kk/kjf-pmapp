/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

(function ($) {
    $(document).ready(function () {
        if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
            // it's not realistic to think we can deal with all the bugs
            // of IE 6 and lower. Fortunately, all this is just progressive
            // enhancement.
            return;
        }
        $('span[data-appui="prettydate"]').timeago();
        $('div[data-appui="state-switch"]').toggleSlide({
            onClick: function (evt, status) {
                console.log('.alternative changed to: ' + status, 'the reverse of: ' + !status);
            },
            text: {
                enabled: 'Aktiv',
                disabled: 'Inaktiv'
            },
            style: {
                enabled: 'success',
                disabled: 'danger'
            }
        });
        $('div[data-appui="preview-switch"]').toggleSlide({
            onClick: function (evt, status) {
                console.log('.alternative changed to: ' + status, 'the reverse of: ' + !status);
            },
            text: {
                enabled: 'An',
                disabled: 'Aus'
            },
            style: {
                enabled: 'success',
                disabled: 'danger'
            }
        });
    });
}(jQuery));
