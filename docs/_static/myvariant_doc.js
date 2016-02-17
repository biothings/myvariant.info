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
});
