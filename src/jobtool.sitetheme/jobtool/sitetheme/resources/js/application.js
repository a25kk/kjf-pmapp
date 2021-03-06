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
        if (!Modernizr.csstransitions) { // Test if CSS transitions are supported
            $(function () {
                $('div.window').on('load', function () {
                    $(this).animate({opacity: '1'}, {queue: false, duration: 500});
                });
            });
        }
        $('span[data-appui="prettydate"]').timeago();
        $('input[data-appui="knob"]').knob();
        $('a[data-appui="tooltip"]').tooltip();
        $('#form-widgets-category').chosen();
        $('a.popoverForm').prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: '#form',
            closeselector: '.overlayCloseAction, [name="form.button.Cancel"]',
            noform: 'reload',
            config: {
                closeOnClick: false,
                top: 80,
                mask: {
                    color: '#000000',
                    opacity: 0.8
                }
            },
            redirect: function () {
                return location.href;
            }
        });
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
                            active,
                            inactive;
                        if (data.success) {
                            state = data.results.state;
                            active = data.results.counter[0];
                            inactive = data.results.counter[1];
                            $('#counter-active').text(active);
                            $('#counter-inactive').text(inactive);
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
