import os
import jinja2
import webapp2
import string
import codecs
import re

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blogtext = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class NewPost(Handler):
    def get(self):
        self.render("newpost.html")
    
    def post(self):
        title = self.request.get("title")
        blogtext = self.request.get("blogtext")
        blogitem = Blog(title=title,blogtext=blogtext)
        blogitem.put()
        b_key =blogitem.put() # Key('Blog', id)
        self.redirect("/blog/%d" % b_key.id())


class BlogPost(Handler):
    def render_front(self):
        # blogs = db.GqlQuery("select * from Blog order by created desc")
        blogs = Blog.all().order('-created')
        self.render("basicblog.html",blogs=blogs)

    def get(self):
        blogs = db.GqlQuery("select * from Blog order by created desc")
        self.render("basicblog.html",blogs=blogs)

class Permalink(BlogPost):
    def get(self, blog_id):
        blogitem = Blog.get_by_id(int(blog_id))
        self.render("blogitem.html", title=blogitem.title,blogtext=blogitem.blogtext)

app = webapp2.WSGIApplication([('/blog', BlogPost),('/blog/newpost',NewPost), ('/blog/(\d+)', Permalink)], debug=True)