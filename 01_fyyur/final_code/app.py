#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show

from flask_migrate import Migrate
# import datetime for use in num_upcoming_shows logic
from datetime import datetime
from dateutil import parser

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)

# DONE: connect to a local postgresql database
# Set for application instance & Flask-SQLAlchemy db instance
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  # Display most recently added venues/artists
  venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  venue_data = []
  # pull all venues
  venues = Venue.query.all()

  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
    venue_data.append({
      'city': place.city,
      'state': place.state,
      'venues': Venue.query.filter(Venue.city == place.city).filter(Venue.state == place.state).all(),
      'num_upcoming_shows': Show.query.filter(Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).count
      # cannot get num_upcoming shows to display on the venue page, not sure it's required 
      # as although present in dummy data it does not show as an output on venues page with dummy data used or even in video on project instructions page.
    })

  # changed so that matches above venue_data
  return render_template('pages/venues.html', areas=venue_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  # get the search term from the form
  # query the venue model & filter based on the search term, use ilike for case insensitivity
  # output the results
  search_term = request.form.get('search_term','')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response = {'count': len(venues), 'data': venues}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  # query to pull the venue id
  venue = Venue.query.get(venue_id)

  # set a variable for the datetime to be used for checks against past/upcoming shows
  current_time = datetime.now()

  # Join query
  shows = Show.query.join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).filter(Venue.id == venue_id).all()
  
  # create arrays for past & upcoming show data
  upcoming_shows = []
  past_shows = []
  

  # get the data to populate past/upcoming show arrays
  for show in shows:
    temp_show = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    }

    if show.start_time > current_time:
      upcoming_shows.append(temp_show)
    else:
      past_shows.append(temp_show)

  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] =len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  form = VenueForm()
  # Set error variable to False as default.
  error = False

  try:
    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )
  
    # commit to the db
    db.session.add(venue)
    db.session.commit()

  except ValueError as e:
    # rollback if error occurs
    print(e)
    error = True
    db.session.rollback()

  finally:
    # close db connection
    db.session.close()
    
  if error:
    # flash error on an unsuccessful insert 
    flash('Error when trying to list ' + request.form['name'] + '. Listing unsuccessful.')
    abort(400)
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # set error value to False as default.
  error = False

  try:
    # get venue by ID & store name for flash messages
    venue = Venue.query.get(venue_id)
    venue_name = venue.name

    db.session.delete(venue)
    db.session.commit()
  
  except ValueError as e:
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occured, unable to delete ' + venue_name + '.')
    abort(400)

  else:
    flash('Venue ' + venue_name + ' successfully deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data = Artist.query.order_by(Artist.name).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term','')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = {'count': len(artists), 'data': artists}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)

  #shows = Show.query.filter_by(artist_id=artist_id).all()
  # Join query
  shows = Show.query.join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).filter(Artist.id == artist_id).all()
  
  current_time = datetime.now()
  
  upcoming_shows = []
  past_shows = []

  for show in shows:
    temp_show = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    }

    if show.start_time > current_time:
      upcoming_shows.append(temp_show)
    else:
      past_shows.append(temp_show)

  data = vars(artist)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] =len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
 
  return render_template('pages/show_artist.html', artist=data)

#  Delete Artist
#  ----------------------------------------------------------------
#  delete artist functionality added to mirror venue deletion
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

  error = False

  try:
    # get venue by ID & store name for flash messages
    artist = Artist.query.get(artist_id)
    artist_name = artist.name

    db.session.delete(artist)
    db.session.commit()
  
  except ValueError as e:
    print(e)
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    flash('An error occured, unable to delete ' + artist_name + '.')
    abort(400)

  else:
    flash('Artist ' + artist_name + ' successfully deleted.')

  return redirect(url_for('index'))

#  Update/Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.image_link.data=artist.image_link
  form.facebook_link.data=artist.facebook_link
  form.genres.data=artist.genres
  form.website.data=artist.website
  form.seeking_venue.data=artist.seeking_venue
  form.seeking_description.data=artist.seeking_description


  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  error = False

  try:
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.facebook_link=form.facebook_link.data
    artist.image_link=form.image_link.data
    artist.website=form.website.data
    artist.seeking_venue=form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data
  
    # commit to the db
    db.session.commit()

  except ValueError as e:
    # rollback if error occurs
    print(e)
    error = True
    db.session.rollback()

  finally:
    # close db connection
    db.session.close()
    
  if error:
    # flash error on an unsuccessful insert 
    flash('Error when trying to update ' + request.form['name'] + '. Update unsuccessful.')
    abort(400)
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Update/Edit Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  # get the venue form & set venue ID 
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  # populate blank form with those associated with the venue ID
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.image_link.data=venue.image_link
  form.facebook_link.data=venue.facebook_link
  form.genres.data=venue.genres
  form.website.data=venue.website
  form.seeking_talent.data=venue.seeking_talent
  form.seeking_description.data=venue.seeking_description
 
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONES: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  error = False

  try:
    venue.name=form.name.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.address=form.address.data
    venue.phone=form.phone.data
    venue.genres=form.genres.data
    venue.facebook_link=form.facebook_link.data
    venue.image_link=form.image_link.data
    venue.website=form.website.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
  
    # commit to the db
    db.session.commit()

  except ValueError as e:
    # rollback if error occurs
    print(e)
    error = True
    db.session.rollback()

  finally:
    # close db connection
    db.session.close()
    
  if error:
    # flash error on an unsuccessful insert 
    flash('Error when trying to update ' + request.form['name'] + '. Update unsuccessful.')
    abort(400)
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

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
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  form = ArtistForm()
  # Set error variable to False as default.
  error = False

  try:
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )
  
    # commit to the db
    db.session.add(artist)
    db.session.commit()

  except ValueError as e:
    # rollback if error occurs
    print(e)
    error = True
    db.session.rollback()

  finally:
    # close db connection
    db.session.close()
    
  if error:
    # flash error on an unsuccessful insert 
    flash('Error when trying to list ' + request.form['name'] + '. Listing unsuccessful.')
    abort(400)
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # pull all shows
  shows = Show.query.order_by(Show.start_time.desc()).all()
  show_data = []

  for show in shows:
    show_data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link':show.artist.image_link,
      'start_time':format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead

  form = ShowForm()
  error = False

  try:
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
  
    # commit to the db
    db.session.add(show)
    db.session.commit()

  except ValueError as e:
    # rollback if error occurs
    print(e)
    error = True
    db.session.rollback()

  finally:
    # close db connection
    db.session.close()
    
  if error:
    # flash error on an unsuccessful insert 
    flash('An error occured, show could not be listed. Please try again.')
    abort(400)
  else:
    # on successful db insert, flash success
    flash('A new show was successfully listed!')

  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
