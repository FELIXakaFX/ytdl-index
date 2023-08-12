<div align="center">

# ytdl-index

*Generates index.html's for your downloaded videos.*

<img src="https://github.com/FelixKohlhas/ytdl-index/assets/18424307/c8dce070-0c16-475b-8f4a-7fae11ab64ea" width="75%">

</div>

## Installing

#### Clone repository and install requirements

    git clone ...
    cd ytdl-index
    pip3 install -r requirements.txt


## Example

#### Download video with metadata and thumbnail

    yt-dlp --write-info-json --no-clean-info-json --write-thumbnail https://www.youtube.com/watch?v=PkPSDOjhxwM

#### Generate index.html

    ./run.py .

## More examples

#### Sort videos by date (descending)

    ./run.py --sort date .

#### Sort videos by title (ascending, natsort)

    ./run.py --sort +title --natsort .

#### Sort videos by playlist position (ascending)

    ./run.py --sort +index .

#### Show all videos, generate thumbnails, sort by mtime, show mtime and size

    ./run.py --show-all --gen-thumb --sort mtime --info mtime,size

## Usage

```
usage: run.py [-h] [-s SORT] [-n] [-t TITLE] [-i INFO] [-p PAGE_INFO] [-d DATE_FORMAT] [-a] [-g] [-v] [directory ...]

Generate directory listing for files downloaded using youtube-dl / yt-dlp.

positional arguments:
  directory

optional arguments:
  -h, --help            show this help message and exit
  -s SORT, --sort SORT  comma separated list of fields to sort videos by (prefix with + to sort ascending)
  -n, --natsort         sort videos using natsort (useful for titles)
  -t TITLE, --title TITLE
                        page title
  -i INFO, --info INFO  comma separated list of fields to show below video title
  -p PAGE_INFO, --page-info PAGE_INFO
                        comma separated list of fields to show below main title (available: (v)ideos, (s)ize, (d)ate)
  -d DATE_FORMAT, --date-format DATE_FORMAT
                        date format to use
  -a, --show-all        show all videos (including ones without info json)
  -g, --gen-thumb       generate thumbnails for videos
  -v, --verbose

available fields: t = title, u = uploader, v = views, d = date, m = mtime, s = size, l = length, i = index, e = extension
```

## yt-dlp flags

    --write-info-json
    --no-clean-info-json
    --write-thumbnail
