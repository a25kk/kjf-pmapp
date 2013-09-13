/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */
'use strict';

(function ($) {
    $(document).ready(function () {
        if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
            // it's not realistic to think we can deal with all the bugs
            // of IE 6 and lower. Fortunately, all this is just progressive
            // enhancement.
            return;
        }
        //$('span[data-appui="prettydate"]').timeago();
        $('input[data-appui="knob"]').knob();
        $('select.chosen-select').chosen();
        /* Apply to popup forms */
        $(document).on('loadInsideOverlay', function () {
            $('select.chosen-select', $(this)).chosen();
        });
        $('#form-widgets-selected2').chosen();
        $('#form-widgets-channel-from').chosen();
        $('#form-widgets-channel').chosen();
        $('#form-widgets-distributor').chosen();
        $(function () {
            $('a[rel=twipsy]').tooltip();
            $('span[rel=twipsy]').tooltip();
        });
        $('h5[data-appui="tooltip"]').tooltip();
        var previewchanger = $('div[data-appui="archive-switch"]');
        var previewchangerUrl = $(previewchanger).data('target');
        $(previewchanger).toggleSlide({
            onClick: function (evt, status) {
                var errorMsg = 'There was an error updating this item - please try again!';
                var ajaxUrl = previewchangerUrl + '?state=' + status;
                $.ajax({
                    url: ajaxUrl,
                    method: 'GET',
                    success: function (data) {
                        var state;
                        if (data.success) {
                            state = data.results.state;
                        } else {
                            alert(errorMsg + '\n\nError:\n' + data.messages);
                        }
                    },
                    error: function () {
                        alert(errorMsg);
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
        $(function () {
            $('a[rel=loading-indicator], input[rel=loading-indicator]').on('click', function () {
                $(this).button('loading');
            });
        });
        var statusURL = $("#status-placeholder a").attr("href");
        if (statusURL) {
            $('#status-placeholder').load(statusURL);
            var refreshId = setInterval(function () {
                $('#status-placeholder').load(statusURL).fadeIn('slow');
            }, 10000);
        }
        var current, toggleBoxes = $('.details').hide();
        $('a.show-details').on("click", function () {
            current = $(this).next('div.details');
            $('.details').not(current).slideUp('slow');
            current.toggle('slow');
        });
        //$('#recipient-table').dataTable();
        /* Default class modification */
        $.extend($.fn.dataTableExt.oStdClasses, {
            "sWrapper": "dataTables_wrapper form-inline"
        });
        /* API method to get paging information */
        $.fn.dataTableExt.oApi.fnPagingInfo = function (oSettings)
        {
            return {
                "iStart":         oSettings._iDisplayStart,
                "iEnd":           oSettings.fnDisplayEnd(),
                "iLength":        oSettings._iDisplayLength,
                "iTotal":         oSettings.fnRecordsTotal(),
                "iFilteredTotal": oSettings.fnRecordsDisplay(),
                "iPage":          Math.ceil(oSettings._iDisplayStart / oSettings._iDisplayLength),
                "iTotalPages":    Math.ceil(oSettings.fnRecordsDisplay() / oSettings._iDisplayLength)
            };
        };

        /* Bootstrap style pagination control */
        $.extend($.fn.dataTableExt.oPagination, {
            "bootstrap": {
                "fnInit": function (oSettings, nPaging, fnDraw) {
                    var oLang = oSettings.oLanguage.oPaginate;
                    var fnClickHandler = function (e) {
                        e.preventDefault();
                        if (oSettings.oApi._fnPageChange(oSettings, e.data.action)) {
                            fnDraw(oSettings);
                        }
                    };
                    $(nPaging).addClass('xpagination').append(
                        '<ul class="pagination">' +
                            '<li class="prev disabled"><a href="#">&larr; ' + oLang.sPrevious + '</a></li>' +
                            '<li class="next disabled"><a href="#">' + oLang.sNext + ' &rarr; </a></li>' +
                        '</ul>'
                    );
                    var els = $('a', nPaging);
                    $(els[0]).bind('click.DT', { action: "previous" }, fnClickHandler);
                    $(els[1]).bind('click.DT', { action: "next" }, fnClickHandler);
                },

                "fnUpdate": function (oSettings, fnDraw) {
                    var iListLength = 5;
                    var oPaging = oSettings.oInstance.fnPagingInfo();
                    var an = oSettings.aanFeatures.p;
                    var i, j, sClass, iStart, iEnd, iHalf = Math.floor(iListLength / 2);

                    if (oPaging.iTotalPages < iListLength) {
                        iStart = 1;
                        iEnd = oPaging.iTotalPages;
                    }
                    else if (oPaging.iPage <= iHalf) {
                        iStart = 1;
                        iEnd = iListLength;
                    } else if (oPaging.iPage >= (oPaging.iTotalPages - iHalf)) {
                        iStart = oPaging.iTotalPages - iListLength + 1;
                        iEnd = oPaging.iTotalPages;
                    } else {
                        iStart = oPaging.iPage - iHalf + 1;
                        iEnd = iStart + iListLength - 1;
                    }
                    for (i = 0, iLen = an.length ; i < iLen ; i++) {
                        // Remove the middle elements
                        $('li:gt(0)', an[i]).filter(':not(:last)').remove();
                        // Add the new list items and their event handlers
                        for (j = iStart ; j <= iEnd ; j++) {
                            sClass = (j == oPaging.iPage + 1) ? 'class="active"' : '';
                            $('<li ' + sClass + '><a href="#">' + j + '</a></li>')
                                .insertBefore($('li:last', an[i])[0])
                                .on('click', function () {
                                    oSettings._iDisplayStart = (parseInt($('a', this).text(), 10) - 1) * oPaging.iLength;
                                    fnDraw(oSettings);
                                });
                        }
                        // Add / remove disabled classes from the static elements
                        if (oPaging.iPage === 0) {
                            $('li:first', an[i]).addClass('disabled');
                        } else {
                            $('li:first', an[i]).removeClass('disabled');
                        }
                        if (oPaging.iPage === oPaging.iTotalPages - 1 || oPaging.iTotalPages === 0) {
                            $('li:last', an[i]).addClass('disabled');
                        } else {
                            $('li:last', an[i]).removeClass('disabled');
                        }
                    }
                }
            }
        });

        if ($('body').hasClass('template-recipient-list')) {
            var oTable;
            $(function () {
                /* Add a click handler to the rows - this could be used as a callback */
                $("#recipient-table tbody tr").click(function () {
                    if ($(this).hasClass('row_selected')) {
                        $(this).removeClass('row_selected');
                    }
                    else {
                        oTable.$('tr.row_selected').removeClass('row_selected');
                        $(this).addClass('row_selected');
                    }
                });
                /* Add a click handler for the delete row */
                $('#delete').on("click", function (e) {
                    e.preventDefault();
                    var anSelected = fnGetSelected(oTable);
                    oTable.fnDeleteRow(anSelected[0]);
                });
                $('#recipient-cleanup-form').on("submit", function () {
                    var sData = $('input', oTable.fnGetNodes()).serialize();
                    $('input', otable.fnGetNodes()).appendTo('#recipient-cleanup-form');
                });
                /* Init the table */
                oTable = $('#recipient-table').dataTable({
                    "bPaginate": false,
                    "bRetrieve": true,
                    "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
                    "sPaginationType": "bootstrap",
                    "oLanguage": {
                        "sLengthMenu": "_MENU_ records per page"
                    }
                });
            });
            /* Get the rows which are currently selected */
            function fnGetSelected( oTableLocal )
            {
                return oTableLocal.$('tr.row_selected');
            }
        }
        $('#table-contacts, #table-channels').dataTable({
            "bPaginate": true,
            "bRetrieve": true,
            "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span3'i><'span9'p>>",
            "sPaginationType": "bootstrap",
            "iDisplayLength": 50,
            "oLanguage": {
                "sLengthMenu": "_MENU_ pro Seite",
                "sInfo": "_START_ bis _END_ von _TOTAL_",
                "oPaginate": {
                    "sPrevious": "Letzte Seite",
                    "sNext": "Nächste Seite"
                },
                "sSearch": "Filter:"
            }
        });
    });
}(jQuery));