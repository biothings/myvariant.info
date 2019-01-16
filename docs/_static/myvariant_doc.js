function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var Releases = {};
var DATA_FORMAT_VERSION = "1.0";

jQuery(document).ready(function() {
    if( jQuery(' .metadata-table ').length ) {
        // get the hg19 metadata information
        jQuery.ajax({
            url: "//myvariant.info/v1/metadata",
            dataType: "JSONP",
            jsonpCallback: "callback",
            type: "GET",
            success: function(data) {
                // Set the total number of variants
                if (('stats' in data) && ('total' in data['stats'])) {
                    jQuery(' .hg19-table p strong ').html(numberWithCommas(data["stats"]["total"]));
                }
                // get all keys and stats from object
                var versionMap = {};
                for (thisSrcKey in data['src']) {
                    var thisSrc = data['src'][thisSrcKey];
                    if ('stats' in thisSrc) {
                        for (collection in thisSrc['stats']) {
                            var tmp = collection.replace('_hg19', '');
                            // hard coded for now
                            if (tmp == 'gnomad_exomes') {tmp = 'gnomad_exome';}
                            if (tmp == 'gnomad_genomes') {tmp = 'gnomad_genome';}
                            versionMap[tmp] = {'total': thisSrc['stats'][collection]};
                            if ('version' in thisSrc) {
                                versionMap[tmp]['version'] = thisSrc['version'];
                            }
                        }
                    }
                }
                jQuery.each(jQuery(' .hg19-table tbody tr '), function(index, row) {
                    var thisRow = jQuery(' .hg19-table tbody tr:nth-child(' + (index + 1).toString() + ')');
                    var thisKey = thisRow.children(' :nth-child(4) ').text();
                    if (thisKey in versionMap) {
                        if  ('version' in versionMap[thisKey]) {
                            thisRow.children(' :nth-child(2) ').html(versionMap[thisKey]["version"]);
                        }
                        if ('total' in versionMap[thisKey]) {
                            thisRow.children(' :nth-child(3) ').html(numberWithCommas(versionMap[thisKey]["total"]));
                        }
                    }
                });
                // get the hg38 metadata information
                jQuery.ajax({
                    url: "//myvariant.info/v1/metadata?assembly=hg38",
                    dataType: "JSONP",
                    jsonpCallback: "callback",
                    type: "GET",
                    success: function(data) {
                        // Set the total number of variants
                        if (('stats' in data) && ('total' in data['stats'])) {
                            jQuery(' .hg38-table p strong ').html(numberWithCommas(data["stats"]["total"]));
                        }
                        // get all keys and stats from object
                        var versionMap = {};
                        for (thisSrcKey in data['src']) {
                            var thisSrc = data['src'][thisSrcKey];
                            if ('stats' in thisSrc) {
                                for (collection in thisSrc['stats']) {
                                    var tmp = collection.replace('_hg38', '');
                                    // hard coded for now
                                    if (tmp == 'gnomad_exomes') {tmp = 'gnomad_exome';}
                                    if (tmp == 'gnomad_genomes') {tmp = 'gnomad_genome';}
                                    versionMap[tmp] = {'total': thisSrc['stats'][collection]};
                                    if ('version' in thisSrc) {
                                        versionMap[tmp]['version'] = thisSrc['version'];
                                    }
                                }
                            }
                        }
                        jQuery.each(jQuery(' .hg38-table tbody tr '), function(index, row) {
                            var thisRow = jQuery(' .hg38-table tbody tr:nth-child(' + (index + 1).toString() + ')');
                            var thisKey = thisRow.children(' :nth-child(4) ').text();
                            if (thisKey in versionMap) {
                                if  ('version' in versionMap[thisKey]) {
                                    thisRow.children(' :nth-child(2) ').html(versionMap[thisKey]["version"]);
                                }
                                if ('total' in versionMap[thisKey]) {
                                    thisRow.children(' :nth-child(3) ').html(numberWithCommas(versionMap[thisKey]["total"]));
                                }
                            }
                        });
                        jQuery.ajax({
                            url: "//myvariant.info/v1/metadata/fields",
                            dataType: "JSONP",
                            jsonpCallback: "callback",
                            type: "GET",
                            success: function(data) {
                                jQuery.each(data, function(field, d) {
                                    var notes = indexed = searchedByDefault = '&nbsp;';
                                    if(d.notes) {notes=d.notes;}
                                    if(d.index) {indexed='&#x2714';}
                                    if(d['searched_by_default']) {searchedByDefault='&#x2714';}
                                    jQuery('.indexed-field-table > tbody:last').append('<tr><td>' + field + '</td><td>' + indexed + '</td><td>' + searchedByDefault + '</td><td><span class="italic">' + d.type + '</span></td><td>' + notes + '</td></tr>');
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
    }
    if ((jQuery('#all-releases').length)) {
        // load releases
        jQuery.ajax({
            url: 'https://s3-us-west-2.amazonaws.com/biothings-releases/myvariant.info-hg19/versions.json',
            cache: false,
            type: "GET",
            dataType: "json",
            success: function (data, Status, jqXHR) 
            {
                if (data.format == DATA_FORMAT_VERSION) {appendResponses(Releases, data.versions, "hg19");}
                jQuery.ajax({
                    url: 'https://s3-us-west-2.amazonaws.com/biothings-releases/myvariant.info-hg38/versions.json',
                    dataType: "json",
                    type: "GET",
                    cache: false,
                    success: function (nData, nStatus, njqXHR) {
                        if (nData.format == DATA_FORMAT_VERSION) {appendResponses(Releases, nData.versions, "hg38");}
                        // display the releases
                        displayReleases();
                    }
                });
            }
        });
    }
});

function appendResponses(rel, res, assembly) {
    jQuery.each(res, function (index, val) {
        var t = new Date(val["release_date"].split("T")[0].split('-'));
        if (!(t in rel)) {rel[t] = [];}
        val['assembly'] = assembly;
        rel[t].push(val);
    }); 
}

function displayReleases() {
    // everything should be loaded and ready to display, first reverse sort all releases by date...
    var releaseDates = Object.keys(Releases);
    releaseDates.sort(function(a,b) {
        return new Date(b) - new Date(a);
    });
    // now compile the html 
    var html = '<p class="release-control-line"><a href="javascript:;" class="release-expand">Expand All</a>|<a href="javascript:;" class="release-collapse">Collapse All</a></p>'
    jQuery.each(releaseDates, function (index, val) {
        var tDate = val.toString().split(" ").slice(1,4); tDate[1] += ","; tDate = tDate.join(" ");
        html += '<div class="release-pane"><p class="release-date">' + tDate + '</p>'; 
        jQuery.each(Releases[val], function (rIndex, rVal) {
            html += '<div><a href="javascript:;" class="release-link" data-url="' + rVal.url + '">' + rVal.assembly + ' version <span class="release-version">' + rVal['target_version'] + '</span></a><div class="release-info"></div></div>';
        });
        html += '</div>'
    });
    // show the html
    jQuery('#all-releases').html(html);
    // attach click handlers for each pop down link
    jQuery('.release-link').click(function () {
        if (!(jQuery(this).siblings('.release-info').hasClass('loaded'))) {
            var that = this;
            jQuery.ajax({
                url: jQuery(this).data().url,
                cache: false,
                type: "GET",
                dataType: "json", 
                success: function (ndata, nStatus, njqXHR) {
                    jQuery.ajax({
                        url: ndata.changes.txt.url, 
                        cache: false,
                        type: "GET",
                        success: function (edata, eStatus, ejqXHR) {
                            jQuery(that).siblings('.release-info').html('<pre>' + edata + '</pre>');
                            jQuery(that).siblings('.release-info').addClass('loaded');
                            jQuery(that).siblings('.release-info').slideToggle();
                        }
                    });
                }
            });
        }
        else {
            jQuery(this).siblings('.release-info').slideToggle();
        }
    });
    // add expand collapse click handlers
    jQuery('.release-collapse').click(function () {jQuery('.release-info').slideUp();});
    jQuery('.release-expand').click(function () {
        jQuery('.release-info.loaded').slideDown();
        jQuery('.release-info:not(.loaded)').siblings('.release-link').click();
    });
}
