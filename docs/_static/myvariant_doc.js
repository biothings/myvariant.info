function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

jQuery(document).ready(function() {
    if( jQuery(' .metadata-table ').length ) {
        // get the metadata information
        jQuery.ajax({
            url: "http://myvariant.info/v1/metadata",
            dataType: "JSONP",
            jsonpCallback: "callback",
            type: "GET",
            success: function(data) {
                // Set the total number of variants
                jQuery(' .metadata-table p strong ').html(numberWithCommas(data["stats"]["total"]));
                jQuery.each(jQuery(' .metadata-table tbody tr '), function(index, row) {
                    var thisRow = jQuery(' .metadata-table tbody tr:nth-child(' + (index + 1).toString() + ')');
                    var thisKey = thisRow.children(' :nth-child(4) ').text();
                    if(thisKey in data["src_version"]) {thisRow.children(' :nth-child(2) ').html(data["src_version"][thisKey]);}
                    if(thisKey in data["stats"]) {thisRow.children(' :nth-child(3) ').html(numberWithCommas(data["stats"][thisKey]));}
                });
                jQuery.ajax({
                    url: "http://myvariant.info/v1/metadata/fields",
                    dataType: "JSONP",
                    jsonpCallback: "callback",
                    type: "GET",
                    success: function(data) {
                        jQuery.each(data, function(field, d) {
                            var notes = indexed = '&nbsp;';
                            if(d.notes) {notes=d.notes;}
                            if(d.indexed) {indexed='&#x2714';}
                            jQuery('.indexed-field-table > tbody:last').append('<tr><td>' + field + '</td><td>' + indexed + '</td><td><span class="italic">' + d.type + '</span></td><td>' + notes + '</td>');
                        });
                        jQuery('.indexed-field-table').DataTable({
                            "iDisplayLength": 50,
                            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                            "columns": [
                                {"width":"290px"},
                                null,
                                null,
                                null
                            ],
                            "autoWidth": false,
                            "dom": "flrtip"
                        });
                    }
                });
                
            }
        });
    }
    if ((jQuery('#hg19').length) && (!(jQuery('#hg19').hasClass('loaded')))) {
        // create the list of releases from version.json
        jQuery.get('https://s3.amazonaws.com/biothings-diffs/myvariant.info-hg19/versions.json', function (data, Status, jqXHR) 
        {
            jQuery.each(data, function (index, val) {
                jQuery('#hg19').append('<div id="rp' + index + '" class="release-pane"><a href="javascript:;" class="release-link hg19">Release ' + val + '</a><div class="release-info"></div></div>');
                jQuery('#rp' + index + ' .release-link.hg19').click(function () {
                    if (!(jQuery('#rp' + index + ' .release-info').hasClass('loaded'))) {
                        jQuery.get('https://s3.amazonaws.com/biothings-diffs/myvariant.info-hg19/' + val + '.json', function(rdata, rStatus, rjqXHR) {
                            jQuery.get(rdata['changes']['txt']['url'], function (ndata, nStatus, njqXHR) {
                                jQuery('#rp' + index + ' .release-info').html('<pre>' + ndata + '</pre>');
                                jQuery('#rp' + index + ' .release-info').addClass('loaded');
                                jQuery('#rp' + index + ' .release-info').slideToggle();
                            });
                        });
                    }
                    else {
                        jQuery('#rp' + index + ' .release-info').slideToggle();
                    }
                });
            });
            jQuery('#hg19').addClass('loaded');
        });
    }
    if ((jQuery('#hg38').length) && (!(jQuery('#hg38').hasClass('loaded')))) {
        // create the list of releases from version.json
        jQuery.get('https://s3.amazonaws.com/biothings-diffs/myvariant.info-hg38/versions.json', function (data, Status, jqXHR) 
        {
            jQuery.each(data, function (index, val) {
                jQuery('#hg38').append('<div id="hg38rp' + index + '" class="release-pane"><a href="javascript:;" class="release-link hg38">Release ' + val + '</a><div class="release-info"></div></div>');
                jQuery('#hg38rp' + index + ' .release-link.hg38').click(function () {
                    if (!(jQuery('#hg38rp' + index + ' .release-info').hasClass('loaded'))) {
                        jQuery.get('https://s3.amazonaws.com/biothings-diffs/myvariant.info-hg38/' + val + '.json', function(rdata, rStatus, rjqXHR) {
                            jQuery.get(rdata['changes']['txt']['url'], function (ndata, nStatus, njqXHR) {
                                jQuery('#hg38rp' + index + ' .release-info').html('<pre>' + ndata + '</pre>');
                                jQuery('#hg38rp' + index + ' .release-info').addClass('loaded');
                                jQuery('#hg38rp' + index + ' .release-info').slideToggle();
                            });
                        });
                    }
                    else {
                        jQuery('#hg38rp' + index + ' .release-info').slideToggle();
                    }
                });
            });
            jQuery('#hg38').addClass('loaded');
        });
    }
});
