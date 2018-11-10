import argparse
import flickrapi
import flickrapi.shorturl
import flickrapi.exceptions
import requests
import json
import os
import psycopg2
import configparser
import time
from flickr_utils import connect, disconnect, flickr_keys


def process_one_photo(cur, flickr, photo_id, info_dict):
    title = info_dict['photo']['title']['_content']
    taken = info_dict['photo']['dates']['taken']
    posted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                            int(info_dict['photo']['dates']['posted'])))
    updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                             int(info_dict['photo']['dates']['lastupdate'])))
    views = int(info_dict['photo']['views'])
    wallpaper = 'FALSE'
    tags = info_dict['photo']['tags']
    for tag in tags['tag']:
        if tag['raw'] == 'wallpaper':
            wallpaper = 'TRUE'
            break
    retries = 5
    while retries > 0:
        try:
            sizes = flickr.photos.getSizes(photo_id=photo_id,
                                           format='json')
            retries = 0
            sizes_dict = json.loads(sizes.decode("utf-8"))
            source = None
            for entry in sizes_dict['sizes']['size']:
                if entry['label'] == 'Original':
                    source = entry['source']
                    break
            if source:
                title = title.replace("'", '')
                title = title.replace('"', '')
                sql = '''INSERT INTO
                         pics(pic_id, date_taken, date_posted,
                         date_updated, view_count, source, title,
                         wallpaper) VALUES
                         ('%s', '%s', '%s', '%s', %d, '%s', '%s', %s)'''
                final_sql = sql % (photo_id, taken, posted,
                                   updated, views, source, title,
                                   wallpaper)
                try:
                    cur.execute(final_sql)
                    print('Added %s' % title)
                except psycopg2.IntegrityError:
                    pass
        except flickrapi.exceptions.FlickrError:
            print('retry %d' % retries)
            retries -= 1
            time.sleep(0.1)


def prepare(cur):
    keys = flickr_keys()
    flickr = flickrapi.FlickrAPI(keys['api_key'], keys['api_secret'])

    for photo in flickr.walk(user_id='mickmcd'):
        photo_id = photo.get('id')
        retries = 5
        while retries > 0:
            try:
                info = flickr.photos.getInfo(photo_id=photo_id, format='json')
                info_dict = json.loads(info.decode("utf-8"))
                if info_dict['photo']['visibility']['ispublic'] == 1:
                    process_one_photo(cur, flickr, photo_id, info_dict)
                retries = 0
            except flickrapi.exceptions.FlickrError:
                print('retry %d' % retries)
                retries -= 1
                time.sleep(0.1)


def download(cur):
    download_count = 0
    path = '/home/mick/Slideshow'

    # get all the rows in the pics table
    sql = 'SELECT * from pics'
    cur.execute(sql)
    row = cur.fetchone()

    # for each row, if the file does not yet exist, download it from
    # flickr and write it to the slideshow directory.
    while row is not None:
        # column 4 is the view count, column 5 is the url, column 6
        # is the title, and column 7 is the wallpaper flag
        if row[4] > 100 or row[7] is True:
            head, tail = os.path.split(row[5])
            dest_file = os.path.join(path, tail)
            if not os.path.isfile(dest_file):
                r = requests.get(row[5])
                with open(dest_file, "wb") as pic_file:
                    pic_file.write(r.content)
                    download_count += 1
                    print('Downloaded %s' % row[6])
        row = cur.fetchone()

    print('%d pictures downloaded.' % download_count)


if __name__ == "__main__":
    down_hlp = 'Download pictures tagged wallpaper or with > 100 views.'
    prep_hlp = 'Populate database with info on all public pictures.'
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true', help=down_hlp)
    parser.add_argument('--prepare', action='store_true', help=prep_hlp)
    args = parser.parse_args()

    conn, cur = connect()

    if conn:
        if args.download:
            download(cur)
        elif args.prepare:
            prepare(cur)
        else:
            parser.print_help()
        disconnect(conn, cur)
