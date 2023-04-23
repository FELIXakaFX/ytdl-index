#!/usr/bin/python3

from jinja2 import Template
import sys
import os
import json
from datetime import datetime
import urllib.parse
import argparse
import operator

fields = {
    "t": "title",
    "u": "uploader",
    "v": "views",
    "d": "date",
    "m": "mtime",
    "s": "size",
    "l": "length",
    "i": "index",
    "e": "extension"
}

video_ext=["mp4", "webm", "mkv", "flv", "m4a", "avi", "3gp"]
audio_ext=["mp3", "ogg", "wav", "aac"]
thumb_ext=["jpg", "webp", "png"]

parser = argparse.ArgumentParser(
                    description='Generate directory listing for files downloaded using youtube-dl / yt-dlp.',
                    epilog='available fields: '+', '.join(' = '.join([short, long]) for short, long in fields.items()))

parser.add_argument('directory',
                    nargs='*')
parser.add_argument('-s', '--sort', 
                    help="comma separated list of fields to sort videos by (prefix with + to sort ascending)",
                    default="v")
parser.add_argument('-n', '--natsort',
                    help="sort videos using natsort (useful for titles)",
                    action='store_true')
parser.add_argument('-t', '--title', 
                    help="page title")
parser.add_argument('-i', '--info',
                    help="comma separated list of fields to show below video title",
                    default="u,v,s")
parser.add_argument('-p', '--page-info',
                    help="comma separated list of fields to show below main title (available: (v)ideos, (s)ize, (d)ate)",
                    default="i,s")
parser.add_argument('-d', '--date-format',
                    help="date format to use",
                    default="%d.%m.%Y")
parser.add_argument('-a', '--show-all',
                    help="show all videos (including ones without info json)",
                    action='store_true')
parser.add_argument('-g', '--gen-thumb',
                    help="generate thumbnails for videos",
                    action='store_true')
parser.add_argument('-v', '--verbose',
                    action='store_true')

args = parser.parse_args()

def short_to_long(field):
    if len(field) == 1:
        if field in fields:
            return fields[field]
        print("Unknown field", '"%s"' % field)
        return None
    return field

def pluralize(number, name, plural=None):
    if number == 1:
        return '%d %s' % (number, name)
    if plural:
        return '%d %s' % (number, plural)
    return '%d %ss' % (number, name)

def format_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1000 or unit == 'PiB':
            break
        size /= 1000
    return f"{size:.{decimal_places}f} {unit}"

def get_duration(filename):
    import subprocess
    try:
        result = subprocess.check_output(
            f'ffprobe -v quiet -show_entries format=duration -select_streams v:0 -of default=noprint_wrappers=1:nokey=1 "{filename}"',
            shell=True).decode()
        return(round(float(result)))
    except:
        return 0

def generate_thumbnail(filename, thumbnail):
    import subprocess
    try:
        subprocess.run(
            f'ffmpeg -i "{filename}" -vframes 1 "{thumbnail}"',
            shell=True)
        return thumbnail
    except:
        return None

def format_duration(duration):
    h = duration // 3600
    m = duration // 60 % 60
    s = duration % 60
    if h > 0:
        return "%d:%02d:%02d" % (h, m, s)
    if m > 0:
        return "%d:%02d" % (m, s)
    if s > 0:
        return "%d" % (s)
    return ""

initial_path=os.getcwd()
script_dir = os.path.dirname(sys.argv[0])

page_title = args.title
sort_fields = args.sort.split(',')[::-1]
info_fields = args.info.split(',')
info_fields = list(short_to_long(field) or "-" for field in info_fields)
page_info_fields = args.page_info.split(',')

date_format = args.date_format
show_all = args.show_all
gen_thumb = args.gen_thumb
natsort = args.natsort
verbose = args.verbose

try:
    with open(os.path.join(script_dir, 'index.html.j2'), 'r') as f:
        template = Template(f.read())
except:
    print("Failed to load template:", os.path.join(script_dir, 'index.html.j2'))
    raise SystemExit

for media_dir in args.directory:

    os.chdir(initial_path)
    try:
        os.chdir(media_dir)
    except:
        print("Invalid directory:", media_dir)
        continue

    if not page_title:
        page_title = os.path.basename(os.getcwd())

    if verbose:
        print("Directory:", media_dir)
        print("Title:", page_title)
        print("Info fields:", ', '.join(info_fields))
        print("Page info fields:", ', '.join(page_info_fields))

    items = []

    total_items = 0
    total_size = 0

    for file in os.listdir('.'):
        base, ext = file.rsplit('.', 1)
        ext = ext.lower()

        is_video=False
        is_audio=False

        if ext in video_ext:
            is_video=True
        elif ext in audio_ext:
            is_audio=True

        if is_video or is_audio:
            if verbose:
                print("Parsing:", base)

            thumb=None
            for e in thumb_ext:
                t = base + '.' + e
                if os.path.isfile(t):
                    thumb=t
                    break

            if not thumb and gen_thumb:
                thumb = generate_thumbnail(file, base + '.jpg')

            try:
                with open(base + '.info.json', 'r') as f:
                    json_data = json.load(f)
                mtime = os.path.getmtime(base + '.info.json')
            except:
                if not show_all:
                    continue
                json_data = {}
                mtime = os.path.getmtime(file)

            title=[json_data.get('title', base)]
            if is_audio:
                title.append("&#127911;")

            date_str = json_data.get('upload_date')
            if date_str:
                date = datetime.strptime(date_str, '%Y%m%d')
            else:
                date = datetime.fromtimestamp(json_data.get('epoch', 0))

            views           = json_data.get('view_count',       0)
            index           = json_data.get('playlist_index',   0)
            uploader        = json_data.get('uploader',         '')
            duration_string = json_data.get('duration_string',  '')

            #mtime = os.path.getmtime(file)
            size = os.path.getsize(file)
            length = int(duration_string.replace(':', '') or 0)

            if not length:
                length = get_duration(file)
                duration_string = format_duration(length)

            total_items += 1
            total_size += size

            info = []
            for field in info_fields:
                if field == "uploader":
                    info.append(uploader)
                if field == "views":
                    info.append('{:,} views'.format(views))
                if field == "date":
                    info.append(date.strftime(date_format))
                if field == "mtime":
                    info.append(datetime.fromtimestamp(mtime).strftime(date_format))
                if field == "size":
                    info.append(format_size(size, 0))
                if field == "length":
                    info.append(duration_string)
                if field == "index":
                    info.append(index or "-")
                if field == "extension":
                    info.append(ext)

            items.append({
                'file': urllib.parse.quote(file),
                'title': ' '.join(title),
                'thumb': urllib.parse.quote(thumb) if thumb else "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=",

                'uploader': uploader,
                'duration': duration_string,

                'info': ' • '.join(info),

                'views': views,
                'date': date,
                'mtime': mtime,
                'size': size,
                'length': length,
                'index': index or 0,
                'extension': ext
            })


    for field in sort_fields:
        reverse = True
        if field[0] == "+":
            reverse = False
            field = field[1:]

        field = short_to_long(field) or "views"

        if verbose:
            print("Sorting by", field, "-", "descending" if reverse else "ascending")
            
        if natsort:
            from natsort import natsorted
            items = natsorted(items, key=operator.itemgetter(field), reverse=reverse)
        else:
            items = sorted(items, key=operator.itemgetter(field), reverse=reverse)

    page_info = []
    for field in page_info_fields:
        if field == "i":
            page_info.append(pluralize(total_items, "item"))
        if field == "s":
            page_info.append(format_size(total_size, 0))
        if field == "d":
            page_info.append(datetime.today().strftime(date_format))

    meta = {
        "page_title": page_title,
        "page_info": ' • '.join(page_info)
    }

    if items:
        with open('index.html', 'w') as f:
            f.write(template.render(items=items, meta=meta))