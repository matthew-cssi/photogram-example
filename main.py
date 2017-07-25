import logging
import jinja2
import os
import webapp2

from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Photo(ndb.Model):
    title = ndb.StringProperty()
    photo_url = ndb.StringProperty()
    like_count = ndb.IntegerProperty(default=0)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        photos = Photo.query().fetch()

        template_vars = {
            'photos': photos,
        }

        template = jinja_environment.get_template('templates/home.html')
        self.response.write(template.render(template_vars))

class LikeHandler(webapp2.RequestHandler):
    # Handles increasing the likes when you click the button.
    def post(self):

        # === 1: Get info from the request. ===
        urlsafe_key = self.request.get('photo_key')

        # === 2: Interact with the database. ===

        # Use the URLsafe key to get the photo from the DB.
        photo_key = ndb.Key(urlsafe=urlsafe_key)
        photo = photo_key.get()

        # Fix the photo like count just in case it is None.
        if photo.like_count == None:
            photo.like_count = 0

        # Increase the photo count and update the database.
        photo.like_count = photo.like_count + 1
        photo.put()

        # === 3: Send a response. ===
        # Send the updated count back to the client.
        self.response.write(photo.like_count)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/likes', LikeHandler),
], debug=True)
