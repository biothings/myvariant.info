# dbNSFP

## What this plugin does

Parses the dbNSFP `_variant` files (per-chromosome TSVs bundled in the academic
release zip) into `dbnsfp` documents for both the `hg19` and `hg38` assemblies.
The `dbNSFP_gene` file is never parsed - only the variant-level scores/annotations
are indexed.

There are two parser flavors per dbNSFP version, e.g. `dbnsfp_parser_54a_v1.py` /
`dbnsfp_parser_54a_v2.py`. `dbnsfp_upload.py` currently registers 54a (the
newest version implemented here) - other version-suffixed parser/mapping files
in this directory are kept for reference but are not wired into any uploader.

- **v1**: per-transcript annotations (REVEL, SIFT, etc.) are flattened onto the
  document; when a variant has multiple transcript rows, only the first row's
  per-transcript values survive the merge (see "Known limitations" below).
- **v2**: per-transcript annotations are nested under a `protein` list, one entry
  per transcript, so multi-transcript variants keep every transcript's values.

Both are registered as separate uploaders in `dbnsfp_upload.py`
(`dbnsfp_hg19_v1`, `dbnsfp_hg38_v1`, `dbnsfp_hg19_v2`, `dbnsfp_hg38_v2`).

## Downloading a new release

dbNSFP no longer publishes a stable, scrapeable download URL. As of the 5.x
series, getting the data requires a **manual, human-gated request**:

1. Register at <https://www.dbnsfp.org/download> with an institutional email
   (a Google Form). A human reviews it and emails back an access code -
   this can take some time, it isn't instant.
2. Submit the "Request download" form (a second Google Form) with that email
   and access code. This emails back release-specific download links, e.g.:

   ```text
   https://dist.genos.us/academic/<token>/dbNSFP5.4a.zip
   https://dist.genos.us/academic/<token>/dbNSFP5.4a.zip.md5
   ```

   (There are also separate BGZF-format links for VEP/SnpSift and a
   `dbNSFP<version>_gene.gz` link - this plugin doesn't use either.)
3. Set `DBNSFP_RELEASE` and `DBNSFP_DOWNLOAD_URL` in `config.py` (gitignored -
   **never commit these**; `<token>` is tied to your specific request, and
   `biothings/myvariant.info` is a public repo) to the new version and the
   `.zip` link from step 2.
4. Run the dumper.

There is currently no way to auto-discover "is a newer release available" the
way the dumper used to (see `MIGRATION_NOTES.md` for why). `DBNSFPDumper.SCHEDULE`
still runs monthly, but it's a no-op until someone repeats steps 1-3 by hand for
the next release.

## Downloading itself is flaky - the dumper retries and resumes

The academic zip is ~45GiB. Connections to it break mid-transfer often enough
in practice (`ChunkedEncodingError` / `IncompleteRead`) that a plain single-shot
`requests.get(..., stream=True)` (what `biothings.hub.dataload.dumper.HTTPDumper`
does by default) isn't reliable enough on its own. `DBNSFPDumper.download()`
overrides the base implementation to retry (`MAX_DOWNLOAD_ATTEMPTS`, default 5)
and resume from the last byte written via an HTTP `Range` request, since the
source (Cloudflare-fronted) advertises `Accept-Ranges: bytes`. This matches
dbNSFP's own suggested `curl --http1.1 -C -` for large downloads - `-C -` is the
resume behavior; `--http1.1` is moot for us since plain `requests`/`urllib3` has
no HTTP/2 support to begin with.

`post_download()` then verifies the download: MD5 against the `.md5` sidecar
(non-fatal if that fetch itself fails - only a real mismatch raises), filename
contains the release tag, the zip's README filename contains the release tag,
and the release is the academic ("a") branch.

## Known limitations

- **v1 loses per-transcript data on multi-transcript variants.** When dbNSFP
  emits multiple rows for the same variant (one per transcript), v1's merge
  step (in `load_file()`) only extends the `aa` field; every other per-transcript
  value (REVEL, SIFT, etc.) from row 2 onward is discarded, keeping only the
  first row's. This is the root cause of
  [issue #179](https://github.com/biothings/myvariant.info/issues/179) and is
  unresolved in v1 by design - v2 exists specifically to fix it. See
  `src/tests/data/test_dbnsfp_parser.py` and `test_dbnsfp_parser_54a.py`.
- **hs1 (T2T-CHM13 v2.0) coordinates are captured but not queryable as their own
  assembly.** `hs1_pos(1-based)` is stored as an auxiliary `hs1: {start, end}`
  field on both the hg19 and hg38 documents (mirroring how `hg18_pos(1-based)`
  is already handled) rather than as a third `dbnsfp_hs1_v*` uploader/index,
  because no hs1 pipeline exists anywhere else in the codebase (no mapping, no
  uploader, no index) - building one was out of scope for the parser fix that
  added this. `hs1_chr` is intentionally left unparsed, same as `hg18_chr`.
- The huge per-population allele-frequency blocks (TOPMed, All of Us, RegeneronME,
  gnomAD2.1.1, gnomAD4.1 joint) are counted toward `VALID_COLUMN_NO` but never
  parsed into individual columns - this is a long-standing scope decision that
  predates 5.3.1a (gnomAD was never parsed in 4.8a either), not something new.

See `MIGRATION_NOTES.md` for the fuller history behind these decisions.
