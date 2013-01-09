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
        var statechanger = $('div[data-appui="state-switch"]');
        var statechanger_url = $(statechanger).data('target');
        $('div[data-appui="state-switch"]').toggleSlide({
            onClick: function (evt, status) {
                var error_msg = "There was an error updating this item - please try again!";
                var ajax_url = statechanger_url + '?state=' + status;
                $.ajax({
                    url: ajax_url,
                    method: "GET",
                    success: function (data) {
                        var state,
                            transition;
                        alert(data);
                        if (data.success) {
                            state = data.results.state;
                            transition = data.results.transitions[0];
                        } else {
                            alert(error_msg + "\n\nError:\n" + data.messages);
                        }
                    },
                    error: function (data) {
                        alert(error_msg);
                    }
                });
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
        var previewchanger = $('div[data-appui="preview-switch"]');
        var previewchanger_url = $(previewchanger).data('target');
        $(previewchanger).toggleSlide({
            onClick: function (evt, status) {
                var error_msg = "There was an error updating this item - please try again!";
                var ajax_url = previewchanger_url + '?state=' + status;
                $.ajax({
                    url: ajax_url,
                    method: "GET",
                    success: function (data) {
                        var state;
                        alert(data);
                        if (data.success) {
                            state = data.results.state;
                        } else {
                            alert(error_msg + "\n\nError:\n" + data.messages);
                        }
                    },
                    error: function (data) {
                        alert(error_msg);
                    }
                });
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
