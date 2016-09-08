#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
    post_list = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT {0} OFFSET {1}".format(limit,offset))
    return post_list


class Post(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    """ A generic parent class with conveniant shortcuts implemented
    """
    # clearly I didn't think anything was conveniant, lol.


class MainHandler(Handler):
    """ Redirects the user to the /blog
    """
    def get(self):
        self.redirect('/blog?page=1')
        return


class MainBlogHandler(Handler):
    """ Displays the viewer with the top 5 blog posts, and shows links to the other services
    """
    def get(self):
        page = int(self.request.get("page"))
        if page:
            offset = (page - 1) * 5
        else:
            offset = 0
        blogposts = get_posts(5, offset)
        post_total = blogposts.count()/5
        tmplt = jinja.get_template('main_blog.html')
        response = tmplt.render(blogposts = blogposts, page = page, post_total = post_total)
        self.response.write(response)


class NewPostHandler(Handler):
    """ A form for submitting a new post into the DB
    """
    def get(self):
        title = ""
        body = ""
        error = ""
        tmplt = jinja.get_template('new_post.html')
        response = tmplt.render(title=title,body=body,error=error)
        self.response.write(response)

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")
        error = ""
        if not title and not body:
            error = "Please fill out all of the fields"
            tmplt = jinja.get_template('new_post.html')
            response = tmplt.render(title=title,body=body,error=error)
            self.response.write(response)
        else:
            post = Post(title=title, body=body)
            post.put()
            self.redirect('/blog/{0}'.format(post.key().id()))
            return


class SinglePostViewer(Handler):
    """ Shows the user an individual blog post in it's own page.
    """
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        tmplt = jinja.get_template('single_post.html')
        response = tmplt.render(post=post)
        self.response.write(response)


class DeletePostHandler(Handler):
    """ Takes the user to confirmation of deletion page, and then deletes the post in question.
    """
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        tmplt = jinja.get_template('delete_post.html')
        response = tmplt.render(post=post)
        post.delete()
        self.response.write(response)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainBlogHandler),
    ('/blog/newpost', NewPostHandler),
    webapp2.Route('/blog/<post_id:\d+>', SinglePostViewer),
    webapp2.Route('/blog/delete/<post_id:\d+>', DeletePostHandler)
], debug=True)
