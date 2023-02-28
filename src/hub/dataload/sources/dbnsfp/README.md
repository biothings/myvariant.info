## Dumper Design

This dumper uses both FTP and HTTP, according to Sebastien:

- FTP: to get the latest version
- HTTP: to actually download the file (because the FTP server is slow)

The FTP server is [dbnsfp.softgenetics.com](dbnsfp.softgenetics.com) and the latest version detection works quite straightforward.

The tricky part is parsing the HTTP download link from the dbNSFP [main page]( https://sites.google.com/site/jpopgen/dbNSFP). As this README is written, the latest academic release is `dbNSFP4.3a` and the main page lists three URLs for download, in the following order:

1. [Amazon AWS](https://www.google.com/url?q=https%3A%2F%2Fdbnsfp.s3.amazonaws.com%2FdbNSFP4.3a.zip&sa=D&sntz=1&usg=AOvVaw2jxs6oSlLKGuD0pfWzazXd)
2. [Box](https://www.google.com/url?q=https%3A%2F%2Fusf.box.com%2Fshared%2Fstatic%2F9r6iamhldji4c3vodwebh3947vgrvsng&sa=D&sntz=1&usg=AOvVaw0IxtlQigv3YxfO4zEGR3U3)
3. [Google Drive](https://drive.google.com/file/d/1p8zlODMg5RIdG2J_vU1292ZqSocS-lii/view?usp=sharing)

We decide to use the Box URLs for downloading because:

1. The Amazon AWS URLs may return a `403: AccessDenied`
2. The Google Drive URLs, when accessed by python code (e.g. our `GoogleDriveDumper`), may report `Google Drive - Quota exceeded` error and we may have to wait 24 hours and try again.

Challenges of finding the correct Box URLs are:

1. Only Amazon AWS URLs contain the filenames (e.g. `dbNSFP4.3a.zip`)
2. A Box URL might be wrapped as in `https://www.google.com/url?q=<Box_URL>`

Solutions: 

1. Given a filename, we have to pinpoint the Box URL with following assumption: the first Box URL right after the Amazon AWS URL containing the filename is the target URL.
2. We can use `urllib.parse.urlparse` to find the wrapped Box URL.

