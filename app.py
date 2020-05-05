#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database (DONE)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    shows = db.relationship('Show', backref ='venue')



    # TODO: implement any missing fields, as a database migration using Flask-Migrate (DONE)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    shows = db.relationship('Show', backref='artist')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (DONE)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. (DONE)

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    start_time = db.Column(db.String(50), nullable = False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data. (DONE)
  # num_shows should be aggregated based on number of upcoming shows per venue.
  venue_data = []
  for venue in Venue.query.all():
    is_city_in_venue_data = False
    same_venue_data = ''
    for i in venue_data:
      if i['city']==venue.city and i['state']==venue.state:
        is_city_in_venue_data = True
        same_venue_data = i
    if not is_city_in_venue_data:
      area = {
        'city': venue.city,
        'state': venue.state,
        'venues': [venue]
      }
      venue_data.append(area)
    else:
      venue_data[venue_data.index(same_venue_data)]['venues'].append(venue)
  return render_template('pages/venues.html', areas=venue_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (DONE)
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_entry = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike(f'%{search_entry}'))
  count = data.count()
  response={
    'count': count,
    'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id (DONE)

  venue = Venue.query.filter_by(id = venue_id.first())
  data = {}
  data['id']=venue.id
  data["name"]=venue.name
  data["genres"]=venue.genres
  data["phone"]=venue.phone
  data["city"]=venue.city
  data["state"]=venue.state
  data["seeking_talent"]=venue.seeking_talent
  data["seeking_description"]=venue.seeking_description
  data["image_link"]=venue.image_link
  data["facebook_link"]=venue.facebook_link
  data["address"]=venue.address
  data["website"]=venue.website
  shows_there=Show.query.filter_by(venue_id=venue_id).all()
  shows_that_passed=[]
  count_of_past_shows =0
  shows_yet_to_come=[]
  count_of_upcoming_shows=0
  for show in shows_there:
    if dateutil.parser.parse(show.start_time)>datetime.now():
      shows_yet_to_come.append(show)
      count_of_upcoming_shows+=1
    else:
      shows_that_passed.append(show)
      count_of_past_shows+=1
  data['upcoming_shows']=shows_yet_to_come
  data["past_shows"]=shows_that_passed
  data["past_shows_count"]=count_of_past_shows
  data["upcoming_shows_count"]=count_of_upcoming_shows
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead (DONE)
  # TODO: modify data to be the data object returned from db insertion (DONE)

  try:
    name=request.form.get('name')
    city=request.form.get('city')
    state=request.form.get('state')
    address=request.form.get('address')
    phone=request.form.get('phone')
    genres=request.form.getlist('genres')
    facebook_link=request.form.get('facebook_link')
    image_link=request.form.get('image_link')
    website=request.form.get('website')
    if request.form.get('seeking_talent'):
      seeking_talent=True
    else:
      seeking_talent=False
    seeking_description=request.form.get('seeking_description')
    new_venue=Venue(image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description,name =name, city=city, state=state,address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead. (DONE)
  except:
    db.session.rollback()
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')

  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. (DONE)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that clicking that button delete it from the db then redirect the user to the homepage
  try:
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + Venue.query.filter_by(id=venue_id).name + ' could not be deleted.') 
  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database (DONE)
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (DONE)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_entry=request.form.get('search_term', '')
  data=Artist.query.filter(Artist.name.ilike(f'%{search_entry}%'))
  count=data.count()
  response={
    "count": count,
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id (DONE)
  artist = Artist.query.filter_by(id=artist_id).first()
  data={}
  data['id']=artist.id
  data["name"]=artist.name
  data["genres"]=artist.genres
  data["phone"]=artist.phone
  data["city"]=artist.city
  data["state"]=artist.state
  data["seeking_venue"]=artist.seeking_venue
  data["seeking_description"]=artist.seeking_description  
  data["image_link"]=artist.image_link
  data["facebook_link"]=artist.facebook_link
  data["website"]=artist.website

  shows_of_this_artist=Show.query.filter_by(artist_id=artist_id).all()
  shows_that_passed=[]
  count_of_past_shows=0
  shows_yet_to_come=[]
  count_of_upcoming_shows=0
  for show in shows_of_this_artist:
    if dateutil.parser.parse(show.start_time)>datetime.now():
      shows_yet_to_come.append(show)
      count_of_upcoming_shows+=1
    else:
      shows_that_passed.append(show)
      count_of_past_shows+=1
  data['upcoming_shows']=shows_yet_to_come
  data["past_shows"]=shows_that_passed
  data["past_shows_count"]=count_of_past_shows
  data["upcoming_shows_count"]=count_of_upcoming_shows
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id> (DONE)
  artist = Artist.query.filter_by(id = artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes (DONE)
  artist=Artist.query.filter_by(id=artist_id).first()
  try:
    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.genres=request.form.getlist('genres')
    artist.facebook_link=request.form.get('facebook_link')
    artist.image_link=request.form.get('image_link')
    artist.website=request.form.get('website')
    if request.form.get('seeking_venue'):
      artist.seeking_venue=True
    else:
      artist.seeking_venue=False
    artist.seeking_description=request.form.get('seeking_description')
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully edited')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' +request.form['name'] + ' could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id> (DONE)
  venue=Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing venue record with ID <venue_id> using the new attributes (DONE)
  try:
    venue.name=request.form.get('name')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.address=request.form.get('address')
    venue.phone=request.form.get('phone')
    venue.genres=request.form.getlist('genres')
    venue.facebook_link=request.form.get('facebook_link')
    venue.image_link=request.form.get('image_link')
    venue.website=request.form.get('website')
    if request.form.get('seeking_talent'):
      venue.seeking_talent=True
    else:
      venue.seeking_talent=False
    venue.seeking_description=request.form.get('seeking_description')
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully edited')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
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
  # TODO: insert form data as a new Venue record in the db, instead (DONE)
  # TODO: modify data to be the data object returned from db insertion (DONE)
  try:
    name=request.form.get('name')
    city=request.form.get('city')
    state=request.form.get('state')
    phone=request.form.get('phone')
    genres=request.form.getlist('genres')
    facebook_link=request.form.get('facebook_link')
    image_link=request.form.get('image_link')
    website=request.form.get('website')
    if request.form.get('seeking_venue'):
      seeking_venue=True
    else:
      seeking_venue=False
    seeking_description=request.form.get('seeking_description')
    new_artist=Artist(image_link=image_link,website=website,seeking_venue=seeking_venue,seeking_description=seeking_description,name=name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link)
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead. (DONE)
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. (DONE)
  # num_shows should be aggregated based on number of upcoming shows per venue.
  
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead (DONE)
  try:
    artist_id=request.form.get('artist_id')
    venue_id=request.form.get('venue_id')
    date=request.form.get('start_time')
    new_show=Show(artist_id=artist_id,venue_id=venue_id,start_time=date)
    db.session.add(new_show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
    app.run(debug = True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
