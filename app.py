#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# initialize migrate instance
migrate = Migrate(app, db)

# Done: connect to a local postgresql database
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'].replace(app.config['DB_NAME'], ''))
# Find all the existing dbs
cursor = engine.execute(f'SELECT datname FROM pg_database;')
all_dbs = [rowproxy[0] for rowproxy in cursor.fetchall()]
# Create db only if not exists
if app.config['DB_NAME'] not in all_dbs:
  from sqlalchemy.orm import sessionmaker
  session = sessionmaker(bind=engine)()
  session.connection().connection.set_isolation_level(0)
  session.execute(f'CREATE DATABASE {app.config["DB_NAME"]}')
  session.connection().connection.set_isolation_level(1)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from datetime import datetime
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Done: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean, default = False)
    genres = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref='Venue', cascade='all,delete,delete-orphan', lazy=True)
    # let's create created_at for sorting instead of sorting by id (might not be apt if id seq is resets)
    created_at = db.Column(db.DateTime, default = datetime.now(), nullable=False)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Done: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False),
    seeking_description = db.Column(db.String(500))
    artist_shows = db.relationship('Show', backref='Artist', cascade='all, delete, delete-orphan', lazy=True)
    # # let's create created_at for sorting instead of sorting by id (might not be apt if id seq is resets)
    created_at = db.Column(db.DateTime, default = datetime.now(), nullable=False)
    available_from = db.Column(db.DateTime, nullable=True)
    available_to = db.Column(db.DateTime, nullable=True)

# Done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'), nullable=False)
  venue_id =  db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
  start_time = db.Column(db.DateTime(timezone=True))

  # let's create created_at for sorting instead of sorting by id (might not be apt if id seq is resets)
  # created_at = db.Column(db.DateTime, default = datetime.now(), nullable=False)
# Create tables
db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------
def format_datetime(value, format='medium'):
  from babel.dates import format_datetime
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  formatted_date = format_datetime(date, 'medium', locale='en_US')
  return formatted_date

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = db.session.query(Venue).order_by(Venue.created_at.desc()).limit(10)
  artists = db.session.query(Artist).order_by(Artist.created_at.desc()).limit(10)
  return render_template('pages/home.html', venues = venues, artists = artists)


#  Venues
#  ----------------------------------------------------------------
def insert_dummy_values(model, dummy_values):
    instance = None
    if 'genres' in dummy_values:
      dummy_values['genres'] = ",".join(dummy_values['genres'])
    if model == 'Venue':
      instance = Venue(**dummy_values)
    if model == 'Artist':
      instance = Artist(**dummy_values)

    if model == 'Show' and type(dummy_values) == list:
      result = []
      for sample in dummy_values:
        show = Show(**sample)
        if show is not None:
          result.append(show)
      db.session.add_all(result)
      db.session.commit()
    if instance is not None:
      db.session.add(instance)
      db.session.commit()
# dummy samples
venue_sample_1 = {
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"}
venue_sample_2 = {
  "name": "The Dueling Pianos Bar",
  "genres": ["Classical", "R&B", "Hip-Hop"],
  "address": "335 Delancey Street",
  "city": "New York",
  "state": "NY",
  "phone": "914-003-1132",
  "website": "https://www.theduelingpianos.com",
  "facebook_link": "https://www.facebook.com/theduelingpianos",
  "seeking_talent": False,
  "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
}
venue_sample_3 = {
  "name": "Park Square Live Music & Coffee",
  "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  "address": "34 Whiskey Moore Ave",
  "city": "San Francisco",
  "state": "CA",
  "phone": "415-000-1234",
  "website": "https://www.parksquarelivemusicandcoffee.com",
  "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  "seeking_talent": False,
  "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
}
# Artists----------
artist_sample_1 = {
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"}
artist_sample_2 = {
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"}

artist_sample_3 = {
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"}

show_samples = [{
    "venue_id": 1,
    "artist_id": 1,
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "artist_id": 2,
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "artist_id": 3,
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "artist_id": 3,
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "artist_id": 3,
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
# -------------------End of samples ---------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues_list = []
  for state, city in db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city).all():
    venues = db.session.query(Venue).filter_by(state=state).filter_by(city=city).all()
    venues_template = {'state': state, 'city': city, 'venues': []}
    for venue in venues:
      venues_template['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': calculate_upcoming_past_shows(venue.venue_shows)
      })
    venues_list.append(venues_template)
  return render_template('pages/venues.html', areas=venues_list)


def calculate_upcoming_past_shows(shows, for_upcoming = True):
    """
    Returns upcoming/ past shows count
    :param shows: shows dbo
    :param for_upcoming: True for upcoming/ false for past
    :return: count (int)
    """
    import pytz
    if for_upcoming:
        num_upcoming_shows = sum([1 for show in shows if show.start_time > datetime.now(pytz.utc)])
        return num_upcoming_shows
    else:
        num_past_shows = sum([1 for show in shows if show.start_time > datetime.now(pytz.utc)])
        return num_past_shows



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  city_state_text = request.form.get('search_by_city_state', '')
  clause = None
  if not search_term:
      from sqlalchemy import and_
      result = city_state_text.split(',')
      if len(result) == 2:
          city = result[0].strip()
          state = result[1].strip()
          clause = and_(Venue.city.ilike(f'%{city}%'), Venue.state.ilike(f'%{state}%'))
  if clause is None and search_term is not None:
      clause = Venue.name.ilike(f'%{search_term}%')
  venues = db.session.query(Venue).filter(clause).all()
  count = len(venues)
  venue_list = []
  for venue in venues:
      selected_venue = {'id': venue.id, 'name': venue.name,
                         'num_upcoming_shows': calculate_upcoming_past_shows(venue.venue_shows)}
      venue_list.append(selected_venue)
  response = {
      "count": count,
      "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term = search_term, city_state_text = city_state_text)



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  import pytz
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  venue = db.session.query(Venue).filter_by(id = venue_id).first()
  past_shows, upcoming_shows = get_past_upcoming_shows(Show.venue_id == venue_id, 'artist')
  genres = []
  if venue.genres is not None:
      genres = venue.genres.split(',')
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Done: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion
  form_data = request.form.to_dict(flat=False)
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = ",".join(form_data['genres'])
    image_link = request.form['image_link']
    seeking_description = request.form['seeking_description']
    facebook_link = request.form['facebook_link']
    venue = Venue(name = name, city = city , state = state ,
            address = address, phone = phone, genres = genres, image_link = image_link,
            seeking_description = seeking_description,
            facebook_link = facebook_link)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    logging.error(f"Error in  [create_venue_submission]>>>> Reason: {str(e)}")
    # Done: on unsuccessful db insert, flash an error instead.
    flash(f'An error occurred. Reason: {str(e)} Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      db.session.query(Venue).filter_by(id = venue_id).delete()
      db.session.commit()
      flash('Successfully deleted the venue!!!!')
  except Exception as e:
      db.session.rollback()
      logging.error(f"Cannot delete venue : {venue_id}, Reason : {e}")
      flash('Cannot delete venue, plz try again later!!!!')
  finally:
      db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  artists = db.session.query(Artist).all()
  artists_list= []
  for artist in artists:
    artists_list.append({'id': artist.id, 'name': artist.name})
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  city_state_text = request.form.get('search_by_city_state', '')
  clause = None
  if not search_term:
      from sqlalchemy import and_
      result = city_state_text.split(',')
      if len(result) == 2:
          city = result[0].strip()
          state = result[1].strip()
          clause = and_(Artist.city.ilike(f'%{city}%'), Artist.state.ilike(f'%{state}%'))
  if clause is None and search_term is not None:
      clause = Artist.name.ilike(f'%{search_term}%')
  artists = db.session.query(Artist).filter(clause).all()
  count = len(artists)
  artists_list = []
  for artist in artists:
      selected_artist = {'id': artist.id, 'name': artist.name,
      'num_upcoming_shows': calculate_upcoming_past_shows(artist.artist_shows)}
      artists_list.append(selected_artist)
  response={
    "count": count,
    "data": artists_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term, city_state_text= city_state_text )

def get_past_upcoming_shows(where_clause, for_artists_venue:str):
    """
    Get past and upcoming artist shows/ venues
    :param where_clause: Artist or Venue where clause
    :param for_artists_venue: 'artist' or 'venue' events
    :return: (list)past, (list)upcoming events
    """
    import pytz
    past_shows = db.session.query(Show).filter(where_clause).filter(
        Show.start_time < datetime.now(pytz.utc)).all()
    upcoming_shows = db.session.query(Show).filter(where_clause).filter(
        Show.start_time >= datetime.now(pytz.utc)).all()
    past_shows_list = []
    upcoming_shows_list = []
    show_keys = ['start_time']
    if for_artists_venue == 'artist':
        show_keys.extend(['artist_id', 'artist_name', 'artist_image_link'])
    else:
        show_keys.extend(['venue_id', 'venue_name', 'venue_image_link'])
    for past_show in past_shows:

        if for_artists_venue == 'venue':
            past_show_template = dict(zip(show_keys,
                                          [str(past_show.start_time), past_show.venue_id, past_show.Venue.name, past_show.Venue.image_link,
                                           ]))
        else:
            past_show_template = dict(zip(show_keys,
                                          [str(past_show.start_time), past_show.artist_id, past_show.Artist.name, past_show.Artist.image_link,
                                           ]))

        past_shows_list.append(past_show_template)

    for upcoming_show in upcoming_shows:
        if for_artists_venue == 'venue':
            upcoming_show_template = dict(zip(show_keys,
                                              [str(upcoming_show.start_time), upcoming_show.venue_id, upcoming_show.Venue.name,
                                               upcoming_show.Venue.image_link,
                                               ]))
        else:
            upcoming_show_template = dict(zip(show_keys,
                                              [str(upcoming_show.start_time), upcoming_show.artist_id, upcoming_show.Artist.name,
                                               upcoming_show.Artist.image_link,
                                               ]))
        upcoming_shows_list.append(upcoming_show_template)
    return past_shows_list, upcoming_shows_list

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  past_shows, upcoming_shows = get_past_upcoming_shows(Show.artist_id == artist_id, 'venue')
  artist_shows={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(',') if artist.genres else [],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "available_from": artist.available_from,
    "available_to": artist.available_to,
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=artist_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  artist_data = None
  if artist is None:
      flash(f'No Artist with the the given artist id: {artist_id}, Please try to edit existing artist!!!!')
  else:
      artist_data = artist.__dict__
      form.state.data = artist.state
      form.genres.data = artist.genres.split(",") if artist.genres is not None else []
  # Done: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form_data = request.form.to_dict(flat=False)
  form_data['genres'] = ",".join(form_data['genres'])
  form_data = {key:value[0] if type(value) is list else value for key, value in form_data.items()}
  try:
    valid_keys = {}
    for key, value in form_data.items():
        if value is not None and value !="":
           valid_keys[key] = value
    db.session.query(Artist).filter(Artist.id == artist_id).update(valid_keys)
    db.session.commit()
    flash(f"Successfully update the artist with id: {artist_id}")
  except Exception as e:
    logging.error(f"Error in [edit_artist_submission]>>>>>> Reason: {str(e)}")
    flash(f"Cannot update artist with id: {artist_id}, please try again!!!!")
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # Done: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  venue_data = None
  if venue is None:
     flash(f'No Venue with the the given venue id: {venue_id}, Please try to edit existing venue!!!!')
  else:
     venue_data = venue.__dict__
     form.state.data = venue.state
     form.genres.data = venue.genres.split(",") if venue.genres is not None else []
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)





@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form_data = request.form.to_dict(flat=False)
  form_data['genres'] = ",".join(form_data['genres'])
  form_data = {key:value[0] if type(value) is list else value for key, value in form_data.items()}
  try:
    db.session.query(Venue).filter(Venue.id == venue_id).update(form_data)
    db.session.commit()
    flash(f"Successfully update the venue with id: {venue_id}")
  except Exception as e:
    logging.error(f"Error in [edit_venue_submission]>>>>>> Reason: {str(e)}")
    flash(f"Cannot update venue with id: {venue_id}, please try again!!!!")
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
  # Done: insert form data as a new Venue(should be artists!!!) record in the db, instead
  # Done: modify data to be the data object returned from db insertion
  form_data = request.form.to_dict(flat=False)
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = ",".join(form_data['genres'])
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      seeking_description = request.form['seeking_description']
      available_from = request.form['available_from'] if request.form['available_from']!="" else None
      available_to = request.form['available_to'] if request.form['available_to']!="" else None
      availability ={}
      if available_from is not None and available_to is not None:
          availability['available_from'] = available_from
          availability['available_to'] = available_to
      artist = Artist(name=name, city=city, state=state,
                    phone=phone, genres=genres, image_link = image_link,
                    seeking_description = seeking_description,
                    facebook_link=facebook_link, **availability)
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
      db.session.rollback()
      logging.error(f"Error in [create_artist_submission]>>>> Reason: {str(e)}")
      # Done: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
      db.session.close()
      return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Show).all()
  shows_list = []
  for show in shows:
    show_template ={
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.Artist.id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": str(show.start_time)
    }
    shows_list.append(show_template)
  return render_template('pages/shows.html', shows=shows_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # Done: insert form data as a new Show record in the db, instead
  try:
      form_data = request.form
      venue_id = form_data['venue_id']
      artist_id = form_data['artist_id']
      start_time = form_data['start_time']
      artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
      # Check if artist has availability constraint
      if artist.available_to is not None and artist.available_from is not None:
          date_format = '%Y-%m-%d %H:%M:%S'
          show_starts_at = datetime.strptime(start_time, date_format)
          if not (show_starts_at >= artist.available_from and show_starts_at <= artist.available_to):
              av_from = artist.available_from.strftime(date_format)
              av_to = artist.available_to.strftime(date_format)
              flash(f'Cannot book shows outside artist availability, Artist is available from {av_from} to {av_to} ')
              raise Exception("Artist availability exception.....")
      show = Show(venue_id = venue_id, artist_id = artist_id, start_time = start_time)
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except Exception as e:
      # Done: on unsuccessful db insert, flash an error instead.
      logging.error(f"Error in [create_show_submission]>>>>> Reason: {str(e)}")
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
      return redirect(url_for('index'))

  

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
