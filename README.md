# spot
A few little scripts for experimenting with the spotify and flickr APIs.
The spotify stuff uses django, the flickr stuff uses standalone scripts.

For flickr, the steps are:
Use psql to empty the pics table in the pictures database
Run flickr-wallpaper.py --prepare
Run flickr-wallpaper.py --download
Run slideshow-text.py

=============================
Help for flickr-wallpaper.py:

usage: flickr-wallpaper.py [-h] [--download] [--prepare]

optional arguments:
  -h, --help  show this help message and exit
  --download  Download pictures tagged wallpaper or with > 100 views.
  --prepare   Populate database with info on all public pictures.

=============================
Table definition for pics in the pictures database:

CREATE TABLE public.pics
(
  pic_id character varying(20) NOT NULL,
  date_posted timestamp without time zone,
  date_taken timestamp without time zone,
  date_updated timestamp without time zone,
  view_count integer,
  source character varying(512) NOT NULL,
  title character varying(512),
  wallpaper boolean DEFAULT false,
  CONSTRAINT pics_pkey PRIMARY KEY (pic_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.pics
  OWNER TO mick;
