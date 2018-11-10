import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import psycopg2
import configparser
from flickr_utils import connect, disconnect, flickr_keys

conn, cur = connect()

margins = 50
font_path = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
slideshow_path = '/home/mick/Slideshow'
font = ImageFont.truetype(
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 32)
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

    draw.text((margins, margins), title, (255, 255, 255), font=font)
    draw.text((margins, margins*2), date, (255, 255, 255), font=font)

    img.save(img_path)
