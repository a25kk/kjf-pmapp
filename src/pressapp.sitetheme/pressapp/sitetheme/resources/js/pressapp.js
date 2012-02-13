/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

(function($){
$(document).ready(function() {
    if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
        // it's not realistic to think we can deal with all the bugs
        // of IE 6 and lower. Fortunately, all this is just progressive
        // enhancement.
        return;
    }
    $('select.chosen-select').chosen();
    /* Apply to popup forms */
    $(document).bind('loadInsideOverlay', function(e){
        $('select.chosen-select', $(this)).chosen();
    });
    $(function() {
        $('a[rel=twipsy]').tooltip();
    });
    $(function() {
        $('a[rel=loading-indicator]').click(function() {
            $(this).button('loading');
        });
    });
    var statusURL = $("#status-placeholder a").attr("href");
    if (statusURL) {
        $('#status-placeholder').load(statusURL);
        var refreshId = setInterval(function() {
            $('#status-placeholder').load(statusURL).fadeIn('slow');
        }, 10000);
    }
    var current, toggleBoxes = $('.details').hide();
    $('a.show-details').click(function() {
        current = $(this).next('div.details');
        $('.details').not(current).slideUp('slow');
        current.toggle('slow');
    });
    $('#recipient-table').dataTable();
});
})(jQuery);