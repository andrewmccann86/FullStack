#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(900))
    facebook_link = db.Column(db.String(900))

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    # increased string length of seeking_description to allow for longer descriptions
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(900))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(900)) 

    # one-to-many relationship setup with Venue as the parent & Show being the child.
    shows = db.relationship('Show', backref='venue', cascade='all, delete', lazy="joined")

    def __repr__(self):
      return'<Venue ID: {self.id} Venue: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(900))
    facebook_link = db.Column(db.String(900))

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    # increased string length of seeking_description to allow for longer descriptions
    website = db.Column(db.String(900))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(900)) 

    # one-to-many relationship setup with Artist as the parent & Show being the child.
    shows = db.relationship('Show', backref='artist',cascade='all, delete', lazy="joined")

    def __repr__(self):
      return'<Artist ID: {self.id} Artist: {self.name}>'

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__='Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='cascade'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='cascade'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)