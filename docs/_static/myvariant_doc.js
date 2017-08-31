function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// some vars to synchronize the downloading of release notes
var Releases = {};
var releaseTargetVersions = [];
var promises = [];
var hg19Release, hg38Release;

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
    if ((jQuery('#all-releases').length)) {
        // load hg19 releases
        jQuery.get('https://s3-us-west-2.amazonaws.com/biothings-releases/myvariant.info-hg19/versions.json', 
            function (data, Status, jqXHR) 
            {
                // for each data, add html to display header and handler to slide notes open/closed
                // assumes versions.json contains a list
                jQuery.each(data, 
                    function (index, val) {
                        // get the json object for this release
                        hg19Release = jQuery.get('https://s3-us-west-2.amazonaws.com/biothings-releases/myvariant.info-hg19/' + val + '.json', 
                        function (sData, sStatus, sjqXHR) {
                            if (!(sData['target_version'] in Releases)) {
                                Releases[sData['target_version']] = [{
                                    "title": sData['target_version'],
                                    "url": sData['changes']['txt']['url'],
                                    "assembly": "hg19"}];
                                releaseTargetVersions.push({'key': sData['target_version'], 
                                    'date': new Date(sData['target_version'].slice(0,4) + ' ' + sData['target_version'].slice(4,6) + ' ' + sData['target_version'].slice(6,8))});
                            }
                            else {
                                Releases[sData['target_version']] = [{
                                    "title": sData['target_version'],
                                    "url": sData['changes']['txt']['url'],
                                    "assembly": "hg19"}, Releases[sData['target_version']][0]];
                            }
                        });
                        promises.push(hg19Release);
                    }
                );
            }
        );
        // load hg38 releases
        jQuery.get('https://s3-us-west-2.amazonaws.com/biothings-releases/myvariant.info-hg38/versions.json', 
            function (data, Status, jqXHR) 
            {
                // for each data, add html to display header and handler to slide notes open/closed
                // assumes versions.json contains a list
                jQuery.each(data, 
                    function (index, val) {
                        // get the json object for this release
                        hg38Release = jQuery.get('https://s3-us-west-2.amazonaws.com/biothings-releases/myvariant.info-hg38/' + val + '.json', 
                        function (sData, sStatus, sjqXHR) {
                            if (!(sData['target_version'] in Releases)) {
                                Releases[sData['target_version']] = [{
                                    "title": sData['target_version'],
                                    "url": sData['changes']['txt']['url'],
                                    "assembly": "hg38"}];
                                releaseTargetVersions.push({'key': sData['target_version'], 
                                    'date': new Date(sData['target_version'].slice(0,4) + ' ' + sData['target_version'].slice(4,6) + ' ' + sData['target_version'].slice(6,8))});
                            }
                            else {
                                Releases[sData['target_version']].push({
                                    "title": sData['target_version'],
                                    "url": sData['changes']['txt']['url'],
                                    "assembly": "hg38"});
                            }
                        });
                        promises.push(hg38Release);
                    }
                );
                jQuery.when.apply(jQuery, promises).done(function () {displayReleases();});
            }
        );
    }
});

function displayReleases() {
    // everything should be loaded and ready to display, first reverse sort all releases by date...
    releaseTargetVersions.sort(function(a,b) {
        return b.date - a.date;
    });
    // now compile the html 
    var html = ''
    jQuery.each(releaseTargetVersions, function (index, val) {
        html += '<div id="' + val.key + '" class="release-pane"><p class="release-title">Release version: <span class="release-version">' + 
            val.key + '</span></p><p class="release-date-line">Released: <span class="release-date">' + 
            val.date.toString().split(" ").slice(0,4).join(" ") + '</span></p>';
        jQuery.each(Releases[val.key], function (iIndex, iVal) {
            var thisId = iVal.title + '-' + iVal.assembly;
            html += '<div><a href="javascript:;" id="' + iVal.title + '-' + iVal.assembly + 
                    '" class="release-link" data-url="' + iVal.url + '">' + iVal.assembly + 
                    '</a><div class="release-info"></div></div>';
        });
        html += '</div>'
    });
    // show the html
    jQuery('#all-releases').append(html);
    // attach click handlers for each pop down link
    jQuery('.release-link').click(function () {
        if (!(jQuery(this).siblings('.release-info').hasClass('loaded'))) {
            var that = this;
            jQuery.get(jQuery(this).data().url, function (ndata, nStatus, njqXHR) {
                jQuery(that).siblings('.release-info').html('<pre>' + ndata + '</pre>');
                jQuery(that).siblings('.release-info').addClass('loaded');
                jQuery(that).siblings('.release-info').slideToggle();
            });
        }
        else {
            jQuery(this).siblings('.release-info').slideToggle();
        }
    });
}
