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
    created = ndb.DateTimeProperty(auto_now_add=True)


def add_default_photos():
    # Photo URLs from Wikipedia.
    cat_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_March_2010-1.jpg/1280px-Cat_March_2010-1.jpg'
    llama_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Lama_Portrait_06072007_01.jpg/2560px-Lama_Portrait_06072007_01.jpg'

    cat = Photo(title='Cat', photo_url=cat_url, like_count=0)
    llama = Photo(title='Llama', photo_url=llama_url, like_count=0)

    cat.put()
    llama.put()

    return [llama, cat]

class MainHandler(webapp2.RequestHandler):
    def get(self):
        photos = Photo.query().order(-Photo.created).fetch()

        # If there are no photos in the database, add defaults.
        # This will only happen one time (on the first run).
        if not photos:
            photos = add_default_photos()

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
