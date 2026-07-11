# Gospel of John — pocket booklets

Print-ready pocket booklets of the Gospel of John, typeset with
[texish](https://github.com/edadma/texish) for
[Christian Evangelism Media](https://christianevangelism.media).

Each booklet is A6 (105 × 148 mm) and imposed two-up in saddle-stitch folding
order onto A5-landscape sheets: print double-sided, fold each sheet down the
middle, nest and staple, and the pages read in order.

## Editions

| Script            | Text                              | Output   |
| ----------------- | --------------------------------- | -------- |
| `en.script`       | Berean Standard Bible (English)   | `en.pdf` |
| `fr.script`       | Louis Segond 1910 (French)        | `fr.pdf` |
| `es.script`       | Biblia Libre Latinoamericano (Spanish) | `es.pdf` |
| `pt.script`       | Bíblia Portuguesa Mundial (Portuguese) | `pt.pdf` |
| `it.script`       | Diodati 1885 (Italian)            | `it.pdf` |
| `zh-Hans.script`  | Chinese Union Version (Chinese, Simplified) | `zh-Hans.pdf` |
| `zh-Hant.script`  | Chinese Union Version (Chinese, Traditional) | `zh-Hant.pdf` |
| `ar.script`       | Smith–Van Dyck (Arabic)           | `ar.pdf` |

All eight Scripture texts are in the public domain. The book text lives in the
USFM files `en.usfm`, `fr.usfm`, `es.usfm`, `pt.usfm`, `it.usfm`, `zh-Hans.usfm`, `zh-Hant.usfm`, and `ar.usfm`; the `.script` files add the
covers, colophon, and imposition. `usfm-booklet.script` (with `john-1-2.usfm`)
is a two-chapter layout-test harness, not a release edition.

The Arabic edition (`ar.script`) is right-bound: it sets the text right-to-left
and imposes with `binding:right`, so the finished booklet binds on the right and
opens from what a left-bound reader would call the back.

## Rendering

Requires the texish CLI. From the texish project directory:

```sh
sbt "texishCli/run /path/to/gospel-of-john/en.script"
```

The PDF is written beside the script (`en.pdf`). PDFs are git-ignored.

## Releasing

`./release.sh` renders every edition and publishes them as a GitHub release
whose version is the current date (`YYYY.MM.DD`). Re-running on the same day
replaces that day's release. It needs the texish CLI and an authenticated
`gh`. Set `TEXISH_DIR` if texish is not at `~/dev/texish`.
