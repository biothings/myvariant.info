jQuery(document).ready(function() {
    if( jQuery(' .indexed-field-table ').length ) {
        jQuery.ajax({
            url: "http://myvariant.info/v1/indexed_fields",
            dataType: "JSONP",
            jsonpCallback: "callback",
            type: "GET",
            success: function(data) {
                jQuery.each(data, function(field, type) {
                    jQuery('.indexed-field-table > tbody:last').append('<tr><td>' + field + '</td><td><span class="italic">' + type + '</span></td><td>&nbsp;</td>');
                });
                jQuery('.indexed-field-table').DataTable({
                    "iDisplayLength": 50,
                    "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                    "columns": [
                        {"width":"290px"},
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
