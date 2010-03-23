from google.appengine.ext import db
from google.appengine.api import users

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

setkey_page = '/setkeys.html'

class ApiKey ( db.Model ):
    api_key = db.StringProperty(required=True)
    sec_key = db.StringProperty(required=True)
    when = db.DateProperty( auto_now_add = True )
    account = db.UserProperty()


class SetKeys(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            api_key = self.request.get ( "api_key" )
            sec_key = self.request.get ( "sec_key" )
            if api_key and len(api_key) == 4 and sec_key and len(sec_key) == 4:
                self.response.headers['Content-Type'] = 'text/plain'
                key = db.GqlQuery ( "select * from ApiKey where account = :1", user )
                for k in key:
                    k.delete()
                k = ApiKey ( api_key = api_key, sec_key = sec_key, account = user )
                k.put()
                self.redirect ( '/' );
            else:
                self.redirect ( setkey_page )
        else:
            self.redirect(users.create_login_url(self.request.uri))



class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            key = db.GqlQuery ( "select * from ApiKey where account = :1", user );
            if key.count() > 0:
                self.response.out.write ( key.count()  );
            else:
                self.redirect ( setkey_page );
        else:
            self.redirect(users.create_login_url(self.request.uri))

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/setkeys', SetKeys )],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
