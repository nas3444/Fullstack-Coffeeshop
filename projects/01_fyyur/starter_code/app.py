#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []

  areas = db.session.query(Venue.city, Venue.state).distinct()
  
  for area in areas:
    venues = Venue.query.filter_by(city=area.city, state=area.state).all()
    city = area.city
    state = area.state
    venue_record = []

    for venue in venues:
      num_upcoming_shows = len(venue.shows.filter(Show.start_time > datetime.now()).all())
      venue_record.append({
        "id" : venue.id,
        "name" : venue.name,
        "num_upcoming_shows" : num_upcoming_shows
      })

    data.append({
      "city" : city,
      "state" : state,
      "venues" : venue_record
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%' + term + '%')).all()
  
  venues_count = len(venues)
  venue_list = []
  for venue in venues:
    num_upcoming_shows = len(venue.shows.filter(Show.start_time > datetime.now()).all())
    venue_list.append({
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows" : num_upcoming_shows, 
    })
  
  response={
    "count": venues_count,
    "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  past_shows_list = venue.shows.filter(Show.start_time < datetime.now()).all()
  upcoming_shows_list = venue.shows.filter(Show.start_time > datetime.now()).all()
  past_shows_count = venue.shows.filter(Show.start_time < datetime.now()).count()
  upcoming_shows_count = venue.shows.filter(Show.start_time > datetime.now()).count()

  past_shows = []
  for show in past_shows_list:
    past_shows.append({
      "artist_id" : show.Artist.id,
      "artist_name" : show.Artist.name,
      "artist_image_link" : show.Artist.image_link,
      "start_time" : show.start_time
    })

  upcoming_shows = []
  for show in upcoming_shows_list:
    upcoming_shows.append({
      "artist_id" : show.Artist.id,
      "artist_name" : show.Artist.name,
      "artist_image_link" : show.Artist.image_link,
      "start_time" : show.start_time
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if 'seeking_talent' in request.form:
    seeking_talent = True
  else:
    seeking_talent = False

  try:
    venue = Venue(name=request.form.get('name'), city=request.form.get('city'),
            state=request.form.get('state'), address=request.form.get('address'),
            phone=request.form.get('phone'), genres=request.form.getlist('genres'),
            facebook_link=request.form.get('facebook_link'), image_link=request.form.get('image_link'),
            website_link=request.form.get('website_link'), seeking_talent=seeking_talent,
            seeking_description=request.form.get('seeking_description'))
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return redirect(url_for('create_venue_form'))
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%' + term + '%')).all()
  
  artists_count = len(artists)
  artist_list = []
  for artist in artists:
    num_upcoming_shows = len(artist.shows.filter(Show.start_time > datetime.now()).all())
    artist_list.append({
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows" : num_upcoming_shows, 
    })
  
  response={
    "count": artists_count,
    "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  past_shows_list = artist.shows.filter(Show.start_time < datetime.now()).all()
  upcoming_shows_list = artist.shows.filter(Show.start_time > datetime.now()).all()
  past_shows_count = artist.shows.filter(Show.start_time < datetime.now()).count()
  upcoming_shows_count = artist.shows.filter(Show.start_time > datetime.now()).count()

  past_shows = []
  for show in past_shows_list:
    past_shows.append({
      "venue_id" : show.Venue.id,
      "venue_name" : show.Venue.name,
      "venue_image_link" : show.Venue.image_link,
      "start_time" : show.start_time
    })

  upcoming_shows = []
  for show in upcoming_shows_list:
    upcoming_shows.append({
      "venue_id" : show.Venue.id,
      "venue_name" : show.Venue.name,
      "venue_image_link" : show.Venue.image_link,
      "start_time" : show.start_time
    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  """ artist={
    "id": artist_record.id,
    "name": artist_record.name,
    "genres": artist_record.genres,
    "city": artist_record.city,
    "state": artist_record.state,
    "phone": artist_record.phone,
    "website": artist_record.website_link,
    "facebook_link": artist_record.facebook_link,
    "seeking_venue": artist_record.seeking_venue,
    "seeking_description": artist_record.seeking_description,
    "image_link": artist_record.image_link
  } """
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)
 

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website_link = request.form.get('website_link')
    artist.seeking_description = request.form.get('seeking_description')

    seeking_checked = 'seeking_venue' in request.form
    if seeking_checked:
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_record = Venue.query.get(venue_id)
  form = VenueForm(obj=venue_record)
  """ venue={
    "id": venue_record.id,
    "name": venue_record.name,
    "genres": venue_record.genres,
    "city": venue_record.city,
    "state": venue_record.state,
    "phone": venue_record.phone,
    "website": venue_record.website_link,
    "facebook_link": venue_record.facebook_link,
    "seeking_talent": venue_record.seeking_talent,
    "seeking_description": venue_record.seeking_description,
    "image_link": venue_record.image_link
  } """
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_record)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.address = request.form.get('address')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website_link = request.form.get('website_link')
    venue.seeking_description = request.form.get('seeking_description')

    seeking_checked = 'seeking_talent' in request.form
    if seeking_checked:
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if 'seeking_venue' in request.form:
    seeking_venue = True
  else:
    seeking_venue = False

  try:
    artist = Artist(name=request.form.get('name'), city=request.form.get('city'),
            state=request.form.get('state'), phone=request.form.get('phone'), 
            genres=request.form.getlist('genres'), facebook_link=request.form.get('facebook_link'), 
            image_link=request.form.get('image_link'), website_link=request.form.get('website_link'), 
            seeking_venue=seeking_venue, seeking_description=request.form.get('seeking_description'))

    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return redirect(url_for('create_artist_form'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "venue_id" : show.Venue.id,
      "venue_name" : show.Venue.name,
      "artist_id": show.Artist.id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time" : show.start_time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:  
    show = Show(venue_id=request.form.get('venue_id'),
                artist_id=request.form.get('artist_id'),
                start_time=request.form.get('start_time'))

    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
    return redirect(url_for('index'))
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('create_shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
