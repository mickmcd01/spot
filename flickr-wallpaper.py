import argparse
import flickrapi
import flickrapi.shorturl
import requests
import json
import os
import psycopg2
import configparser

def db_config(filename='/home/mick/flickr.ini'):
    # create a parser
    config = configparser.ConfigParser()
    # read config file
    config.read(filename)

    # get postgres database settings
    db = {}
    if config.has_section('postgresql'):
        params = config.items('postgresql')
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section postgresql not found in the {0} file'.format(filename))
 
    return db

def flickr_keys(filename='/home/mick/flickr.ini'):
    # create a parser
    config = configparser.ConfigParser()
    # read config file
    config.read(filename)

    # get flickr api key and secret
    flickr_keys = {}
    if config.has_section('flickr'):
        params = config.items('flickr')
        for param in params:
            flickr_keys[param[0]] = param[1]
    else:
        raise Exception('Section flickr not found in the {0} file'.format(filename))
 
    return flickr_keys

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = db_config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        conn.set_session(autocommit=True)
 
        # create a cursor
        cur = conn.cursor()
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None, None
    finally:
        if conn is None:
            print('Database connection closed.')
 

def disconnect(conn, cur):
    cur.close()
    conn.close()

def process_one_photo(cur, flickr, photo_id):
    info = flickr.photos.getInfo(photo_id=photo_id, format='json')
    info_dict = json.loads(info.decode("utf-8"))
    title = info_dict['photo']['title']['_content']
    views = int(info_dict['photo']['views'])
    sizes = flickr.photos.getSizes(photo_id=photo_id,
                                            format='json')
    sizes_dict = json.loads(sizes.decode("utf-8"))
    source = None
    for entry in sizes_dict['sizes']['size']:
        if entry['label'] == 'Original':
            source = entry['source']
            break
    if source:
        title = title.replace("'", '')
        title = title.replace('"', '')
        sql = "INSERT INTO pics(pic_id, view_count, source, title, wallpaper) VALUES ('%s', %d, '%s', '%s', TRUE)"
        final_sql = sql % (photo_id, views, source, title)
        try:
            cur.execute(final_sql)
            print('Added %s' % title)
        except psycopg2.IntegrityError:
            pass

def process_wallpaper(cur):
    keys = flickr_keys()
    flickr = flickrapi.FlickrAPI(keys['api_key'], keys['api_secret'])
    for photo in flickr.walk(user_id='mickmcd', tag_mode='all',
            tags='wallpaper'):
        photo_id = photo.get('id')
        process_one_photo(cur, flickr, photo_id)

def process_views(cur):
    keys = flickr_keys()
    flickr = flickrapi.FlickrAPI(keys['api_key'], keys['api_secret'])

    for photo in flickr.walk(user_id='mickmcd'):
        photo_id = photo.get('id')
        info = flickr.photos.getInfo(photo_id=photo_id, format='json')
        info_dict = json.loads(info.decode("utf-8"))
        views = int(info_dict['photo']['views'])
        if views > 100:
            process_one_photo(cur, flickr, photo_id)

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
        head, tail = os.path.split(row[5])
        dest_file = os.path.join(path, tail)
        if not os.path.isfile(dest_file):
            r = requests.get(row[5])
            with open(dest_file, "wb") as pic_file:
                pic_file.write(r.content)
                download_count += 1
        row = cur.fetchone()

    print('%d pictures downloaded.' % download_count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--views', action='store_true')
    parser.add_argument('--wallpaper', action='store_true')
    args = parser.parse_args()

    conn, cur = connect()


    if conn:
        if args.download:
            download(cur)
        elif args.views:
            process_views(cur)
        elif args.wallpaper:
            process_wallpaper(cur)
        else:
            parser.print_help()
        disconnect(conn, cur)

