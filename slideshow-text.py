import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
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


def db_connect():
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

conn, cur = db_connect()

margins = 50
font_path = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
slideshow_path = '/home/mick/Slideshow'
font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 32)
db_dict = {}

# read the pics table and use the id as the key for a dictionary
sql = 'SELECT * from pics'
cur.execute(sql)
row = cur.fetchone()

# for each row, if the file does not yet exist, download it from
# flickr and write it to the slideshow directory.
while row is not None:
    head, tail = os.path.split(row[5])
    date_taken = row[2].strftime('%B %d, %Y')
    db_dict[tail] = (row[6], date_taken) 
    row = cur.fetchone()

disconnect(conn, cur)

for filename in os.listdir(slideshow_path):
    img_path = os.path.join(slideshow_path, filename)
    title = db_dict[filename][0]
    date = db_dict[filename][1]
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    draw.text((margins, margins), title, (255,255,255), font=font)
    draw.text((margins, margins*2), date, (255,255,255), font=font)

    img.save(img_path)


