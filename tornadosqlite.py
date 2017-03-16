from tornado import ioloop
import tornado.web
import sqlite3


#Connection With Database
def _execute(query):
        dbPath = 'chat.db'
        connection = sqlite3.connect(dbPath)
        cursorobj = connection.cursor()
        try:
                cursorobj.execute(query)
                result = cursorobj.fetchall()
                connection.commit()
        except Exception:
                raise
        connection.close()
        return result

#Index.html
class Main(tornado.web.RequestHandler):
    def get(self):
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            name=""
        else:
            name="Welcome,"+str(user_name_cookie)
        self.render("templates/index.html",title="Home",name=name)


#insert Into Person Tabel (Sign UP)
class AddPerson(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/registrationForm.html',title="Sign Up")

    def post(self):
        name = self.get_argument("username")
        # already_taken = self.application.syncdb['chat.db'].find_one( { 'person': name } )
        # if already_taken:
        #      error_msg = u"?error=" + tornado.escape.url_escape("Login name already taken")
        #      self.redirect(u"/login" + error_msg)

        #=== Check if this the name is already exists or not ====
        select=''' select name from person where name = '%s' ''' %(name);
        res=_execute(select)
        
        if len(res)==0:
            query = ''' insert into person (name) values ('%s') ''' %(name);
            print(query)
            _execute(query)
            self.render('templates/sucess.html')
            
            
        else:
            self.write("Exists")
       
#Show  All People
class ShowPeople(tornado.web.RequestHandler):
    def get(self):
        query = ''' select * from person '''
        rows = _execute(query)
        self._processresponse(rows)

    def _processresponse(self,rows):
        self.write("<b>Records</b> <br /><br />")
        for row in rows:
                self.write(str(row[0]) + "      " + str(row[1]) +" <br />" )

#Login
class Login(tornado.web.RequestHandler):
    def get(self):
        self.render('templates/login.html',title="Sign In")
    
    def post(self):
        name = self.get_argument("username")
        self.set_secure_cookie("user_name", name)
        self.redirect("/")
        
        query = ''' select * from person where name = '%s' ''' %(name);
        print(query)
        _execute(query)
        self.render('templates/index.html',title="Home",name=str(user_name_cookie))

class Logout(tornado.web.RequestHandler):
    def get(self):
        #self.render('templates/logout.html',title="Log Out")
        self.clear_cookie("user_name")
        self.redirect("/")
        


        


application = tornado.web.Application([
    (r"/", Main),
    (r"/signup" ,AddPerson),
    (r"/login",Login),
    (r"/show",ShowPeople),
    (r"/logout",Logout)
],debug=True,
static_path='static', cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=")

if __name__ == "__main__":
    application.listen(8000)
tornado.ioloop.IOLoop.instance().start()