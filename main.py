import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
				               autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Blog(db.Model):
	title = db.StringProperty(required = True)
	blog = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
	def render_main(self, title="", blog="", error=""):
		blogs = db.GqlQuery("SELECT * FROM Blog "
				            "ORDER BY created DESC ")
		self.render("blog-main.html", title=title, blog=blog, error=error, blogs=blogs)

	def get(self):
		self.render_main()

	def post(self):
		title = self.request.get("title")
		blog = self.request.get("blog")

		if title and blog:
			a = Blog(title = title, blog = blog)
			a.put()
			self.redirect("/blog/"+str(a.key().id()))
		else:
			error = "we need both a title and a real post!"
			self.render_main(title, blog, error)

class FiveRecent(Handler):
	def render_five(self, title="", blog="", error=""):
		blogs = db.GqlQuery("SELECT * FROM Blog "
				            "ORDER BY created DESC "
							"LIMIT 5 ")
		self.render("blog-main.html", title=title, blog=blog, error=error, blogs=blogs)

	def get(self):
		self.render_five()

class NewPost(Handler):
	def render_new(self, title="", blog="", error=""):
		self.render("newpost.html", title=title, blog=blog, error=error)

	def get(self):
		self.render_new()

	def post(self):
		title = self.request.get("title")
		blog = self.request.get("blog")

		if title and blog:
			a = Blog(parent = post_key(), title = title, blog = blog)
			a.put()
			self.redirect("/blog/%s" % str(a.key().id()))
		else:
			error = "We need both a title and a real post!"
			self.render_new(title, blog, error)

class ViewPostHandler(Handler):
	def get(self, id):
		find_post = Blog.get_by_id(int(id))
		if find_post:
			t = jinja_env.get_template("post.html")
			response = t.render(blog=find_post)
		else:
			error = "Sorry, that post does not appear to exist!"
			t = jinja_env.get_template("blog-main.html")
			response = t.render(error=error)

		self.response.write(response)

app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/blog', FiveRecent),
	('/newpost', NewPost),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
	], debug=True)
