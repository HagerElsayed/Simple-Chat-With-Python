from tornado import ioloop,web,websocket
import tornado
import os
import json
import sqlite3
#from spidermonkey import Runtime



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
            name=user_name_cookie
        self.render("templates/index.html",title="Home",name=name)


#insert Into Person Tabel (Sign UP)
class AddPerson(tornado.web.RequestHandler):
    def get(self):
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            name=""
        else:
            name="Welcome,"+str(user_name_cookie)
        self.render('templates/registrationForm.html',title="Sign Up",name=name)

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
            query = ''' insert into person (name,state) values ('%s',1) ''' %(name);
            print(query)
            _execute(query)
            self.render('templates/login.html',title="Login",name=name)


        else:
            # self.write("Exists")
            # rt = Runtime()
            # cx = rt.new_context()
            # result = cx.eval_script(eval(alert("Sorry this name is Already Exists")))
             self.render('templates/exists.html',title="Exists",name="")

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
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            name=""
        else:
            name="Welcome,"+str(user_name_cookie)
        self.render('templates/login.html',title="Login",name=name)

    def post(self):
        name = self.get_argument("username")


        query = ''' select name from person where name = '%s' ''' %(name);
        print(query)
        result=_execute(query)
        if len(result)==0:
            user_name_cookie = self.get_secure_cookie("user_name")
            if user_name_cookie==None:
                name=""
            else:
                name="Welcome,"+str(user_name_cookie)
            self.render('templates/login.html',title="Login",name=name)

        else:
            name = self.get_argument("username")
            query=''' update person set state=1 where name = '%s' ''' %(name);
            print(query)
            _execute(query)
            self.set_secure_cookie("user_name", name)
            self.redirect("/")


        # name=str(user_name_cookie)
        self.render('templates/index.html',title="Home",name=name)
class Logout(tornado.web.RequestHandler):
    def get(self):
        #self.render('templates/logout.html',title="Log Out")
        self.clear_cookie("user_name")
        self.redirect("/")
    def post(self):
        query=''' update person set state=0 where name = '%s' ''' %(name);
        print(query)
# class Group(tornado.web.RequestHandler):
#     def get(self):
#         user_name_cookie = self.get_secure_cookie("user_name")
#         if user_name_cookie==None:
#             name=""
#         else:
#             name=str(user_name_cookie)
#         self.render("templates/group.html",title="Groups", name=name)
# class People(tornado.web.RequestHandler):
#     def get(self):
#         user_name_cookie = self.get_secure_cookie("user_name")
#         if user_name_cookie==None:
#             name=""
#         else:
#             name=str(user_name_cookie)
#         self.render("templates/people.html",title="People",name=name)

#====== People Handlers =========

class RemoveFriend(tornado.web.RequestHandler):
    def post(self):
        name = self.get_argument("friendtodelete")
        nameID = self._RpersonID(name)
        nameIDINT= int(''.join([ "%d"%x for x in nameID]))
        query = '''delete  from friends where f_id = %d '''%(nameIDINT)
        _execute(query)
        self.redirect("/people")

    def _RpersonID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

class JoinFriend(tornado.web.RequestHandler):
    def post(self):
        name = str(self.get_secure_cookie("user_name"),'utf-8')
        nameId = self._RpersonID(name)
        nameIDINT= int(''.join([ "%d"%x for x in nameId]))
        print(nameIDINT)
        nameF = self.get_argument("friendtojoin")
        nameIdF = self._RpersonID(nameF)
        nameIDFINT= int(''.join([ "%d"%x for x in nameIdF]))
        print(nameIDFINT)
        query = '''insert into friends values (%d,%d) '''%(nameIDINT,nameIDFINT)
        print(query)
        _execute(query)
        self.redirect("/people")

    def _RpersonID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res
class Person(tornado.web.RequestHandler):

    def get(self):
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            self.render("templates/people.html",title="Home",name="",friendsP="",allFriends="")
        else:
            name = str(self.get_secure_cookie("user_name"),'utf-8')
            resPersonID=self._personID(name)
            resPersonIdInt=int(''.join([ "%d"%x for x in resPersonID]))
            friendsID =[]
            friendsID = self._friends(resPersonIdInt)
            friendsName = self._friendsName(friendsID)
            allFriends = self._AllFriends()
            allFriends.remove(name);
            for value in friendsName:
                allFriends.remove(value);

            self.render("templates/people.html",title="Home",name=name,friendsP=friendsName,allFriends=allFriends)

    def _personID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

    def _friends(self,number):
        query=''' select f_id from friends where p_id = '%d' '''%(number)
        res=_execute(query)
        friendsID=[]
        for friend in res :
            friendInt = int(''.join([ "%d"%x for x in friend]))
            friendsID.append(friendInt)
        return friendsID

    def _friendsName(self,friendNumber):
        nameFriends = []
        for value in friendNumber:
            query='''select name from person where id = '%d' '''%(value)
            res=_execute(query)
            res1=str(''.join([ "%s"%x for x in res]))
            nameFriends.append(str(res1))
        return nameFriends

    def _AllFriends(self):
        selectAllFriends='''select name from person  '''
        res=_execute(selectAllFriends)
        allFriends=[]
        for friend in res :
            friend1=str(''.join([ "%s"%x for x in friend]))
            allFriends.append(friend1)
        return allFriends

# ---------------------------------  Group----------------------------#
class ShowGroup(tornado.web.RequestHandler):

    def get(self):
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            self.render("templates/group.html",title="Group",name="",groupsP="",allGroups="")
        else:
            name = str(self.get_secure_cookie("user_name"),'utf-8')
            resPersonID=self._personID(name)
            print(resPersonID)
            resPersonIdInt=int(''.join([ "%d"%x for x in resPersonID]))
            groupsID =[]
            groupsID = self._groups(resPersonIdInt)
            groupsName = self._groupsName(groupsID)
            allGroups = self._AllGroups()
            for value in groupsName:
                allGroups.remove(value);
            # if groupsP == "":
            #     self.render("templates/group.html",title="Group",name=name,groupsP="",allGroups=allGroups)
            self.render("templates/group.html",title="Group",name=name,groupsP=groupsName,allGroups=allGroups)

    def _personID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

    def _groups(self,number):
        query=''' select g_id from join_group where p_id = '%d' '''%(number)
        res=_execute(query)
        groupsID=[]
        for group in res :
            groupInt = int(''.join([ "%d"%x for x in group]))
            groupsID.append(groupInt)
        return groupsID

    def _groupsName(self,groupNumber):
        nameGroups = []
        for value in groupNumber:
            query='''select name from chatGroup where id = '%d' '''%(value)
            res=_execute(query)
            res1=str(''.join([ "%s"%x for x in res]))
            nameGroups.append(str(res1))
        return nameGroups

    def _AllGroups(self):
        selectAllGroups='''select name from chatGroup  '''
        res=_execute(selectAllGroups)
        allGroups=[]
        for group in res :
            group1=str(''.join([ "%s"%x for x in group]))
            allGroups.append(group1)
        return allGroups



class RemoveGroup(tornado.web.RequestHandler):
    def post(self):
        name = str(self.get_secure_cookie("user_name"),'utf-8')
        nameId = self._RpersonID(name)
        nameIDINT= int(''.join([ "%d"%x for x in nameId]))
        print(nameIDINT)
        nameG = self.get_argument("grouptoleave")
        nameIdG = self._RgroupID(nameG)
        nameIDGINT= int(''.join([ "%d"%x for x in nameIdG]))
        print(nameIDGINT)
        query = '''delete from join_group where p_id = %d and g_id = %d '''%(nameIDINT,nameIDGINT)
        _execute(query)
        self.redirect("/group")

    def _RpersonID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

    def _RgroupID(self,name):
        personId='''select id from chatGroup where name = '%s' '''%(name)
        res=_execute(personId)
        return res


class JoinGroup(tornado.web.RequestHandler):
    def post(self):
        name = str(self.get_secure_cookie("user_name"),'utf-8')
        nameId = self._RpersonID(name)
        nameIDINT= int(''.join([ "%d"%x for x in nameId]))
        print(nameIDINT)
        nameG = self.get_argument("grouptojoin")
        nameIdG = self._RgroupID(nameG)
        nameIDGINT= int(''.join([ "%d"%x for x in nameIdG]))
        print(nameIDGINT)
        query = '''insert into join_group values (%d,%d) '''%(nameIDINT,nameIDGINT)
        print(query)
        _execute(query)
        self.redirect("/group")

    def _RpersonID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

    def _RgroupID(self,name):
        personId='''select id from chatGroup where name = '%s' '''%(name)
        res=_execute(personId)
        return res


class PCreateGroup(tornado.web.RequestHandler):
    def post(self):
        name = str(self.get_secure_cookie("user_name"),'utf-8')
        nameId = self._RpersonID(name)
        nameIDINT= int(''.join([ "%d"%x for x in nameId]))
        print(nameIDINT)
        nameG = self.get_argument("createGroup")
        print(nameG)
        self._personCreateGroup(nameG,nameIDINT)
        nameIdG = self._groupID(nameG)
        nameIDGINT= int(''.join([ "%d"%x for x in nameIdG]))
        # print(nameIDGINT)

        query = '''insert into join_group values (%d,%d) '''%(nameIDINT,nameIDGINT)
        print(query)
        _execute(query)
        self.redirect("/group")

    def _RpersonID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

    def _personCreateGroup(arg,name,pID):
        personCreateGroup='''insert into chatGroup values( null, '%s' , '%d') '''%(name,pID)
        res=_execute(personCreateGroup)
        return res

    def _groupID(arg,name):
        groupId='''select id from chatGroup where name = '%s' '''%(name)
        res=_execute(groupId)
        return res

# ---------------------------------end of Group----------------------------#

#====== PRivate Chat Trial========
clients=[]

class ChatHandler(web.RequestHandler):
    def get(self):
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            self.render("templates/client.html",title="Private Chat",name="")
        else:
            name = str(self.get_secure_cookie("user_name"),'utf-8')
            resPersonID=self._personID(name)
            resPersonIdInt=int(''.join([ "%d"%x for x in resPersonID]))
            friendsID =[]
            friendsID = self._friends(resPersonIdInt)
            friendsName = self._friendsName(friendsID)
            # allFriends = self._AllFriends()
            # allFriends.remove(name);
            # for value in friendsName:
            #     allFriends.remove(value);
            self.render("templates/client.html",title="Private Chat",name=name,friendsName=friendsName)
    def _personID(self,name):
        personId='''select id from person where name = '%s' '''%(name)
        res=_execute(personId)
        return res

    def _friends(self,number):
        query=''' select f_id from friends where p_id = '%d' '''%(number)
        res=_execute(query)
        friendsID=[]
        for friend in res :
            friendInt = int(''.join([ "%d"%x for x in friend]))
            friendsID.append(friendInt)
        return friendsID

    def _friendsName(self,friendNumber):
        nameFriends = []
        for value in friendNumber:
            query='''select name from person where id = '%d' '''%(value)
            res=_execute(query)
            res1=str(''.join([ "%s"%x for x in res]))
            nameFriends.append(str(res1))
        return nameFriends

        # def _AllFriends(self):
        #     selectAllFriends='''select name from person  '''
        #     res=_execute(selectAllFriends)
        #     allFriends=[]
        #     for friend in res :
        #         friend1=str(''.join([ "%s"%x for x in friend]))
        #         allFriends.append(friend1)
        #     return allFriends

class WSHandler(websocket.WebSocketHandler):
    def open(self):
        self.name="Unknown Person"
        clients.append(self)

        online=[]
        for client in clients:
            online.append(client.name)


        onlinedict={}
        onlinedict["code"]=2
        onlinedict["list"]=online

        for client in clients:

            client.write_message(json.dumps(onlinedict))

    def on_message(self,message):
        receivedMessage=[]
        #print(receivedMessage)
        receivedMessage=message.split("/")
        code=receivedMessage[0]
        #print(receivedMessage[0])
        if code == "0":
            for client in clients:
                if client is self:

                    client.name=receivedMessage[1]
            online=[]
            for client in clients:
                online.append(client.name)


            onlinedict={}
            onlinedict["code"]=2
            onlinedict["list"]=online

            for client in clients:

                client.write_message(json.dumps(onlinedict))
        if code == "1":
            for client in clients:
                client.write_message(json.dumps(self.name+": "+receivedMessage[1]))
        if code == "2":
            targetPerson=receivedMessage[2]
            for client in clients:
                if client.name==targetPerson:
                    # client.write_message(json.dumps("Private Message: "+self.name+": "+receivedMessage[1]+"\n"))
                    client.write_message(json.dumps(receivedMessage[1]+"\n"))

    def on_close(self):
        clients.remove(self)
clientsG = {}
class SocketHandler(websocket.WebSocketHandler):
	def open(self):
		clientsG[id(self)] = self
		print("Connection Opened")

	def on_message(self,msg):
		for c in clientsG.keys():
				clientsG[c].write_message(msg)

	def on_close(self):
		del clientsG[id(self)]

class ChatHandlerG(tornado.web.RequestHandler):
    def get(self):
        user_name_cookie = self.get_secure_cookie("user_name")
        if user_name_cookie==None:
            self.render("templates/group.html",title="Group",name="",groupsP="",allGroups="")
        else:
            name = str(self.get_secure_cookie("user_name"),'utf-8')
            nameG = self.get_query_argument("startchat")
            # print (nameG)
            nameIdG = self._RgroupID(nameG)
            nameIDGINT= int(''.join([ "%d"%x for x in nameIdG]))
            Gmembers=[]
            friendsName=[]
            Gmembers = self._groupMembers(nameIDGINT)
            friendsName = self._friendsName(Gmembers)
            self.render("templates/chat.html",title="chat",name=name,nameG=nameG,friendsName=friendsName)
    def _groupMembers(self,number):
        query=''' select p_id from join_group where g_id = '%d' '''%(number)
        res=_execute(query)
        allMem=[]
        for mem in res :
            mem1=str(''.join([ "%s"%x for x in mem]))
            allMem.append(mem1)
        return allMem
    def _friendsName(self,friendNumber):
        nameFriends = []
        for value in friendNumber:
            value=int(value)
            query='''select name from person where id = '%d' '''%(value)
            res=_execute(query)
            res1=str(''.join([ "%s"%x for x in res]))
            nameFriends.append(str(res1))
        return nameFriends
    def _RgroupID(self,name):
        personId='''select id from chatGroup where name = '%s' '''%(name)
        res=_execute(personId)
        return res


application = tornado.web.Application([
    (r"/", Main),
    (r"/signup" ,AddPerson),
    (r"/login",Login),
    (r"/show",ShowPeople),
    (r"/pchat",ChatHandler),
    (r"/ws",WSHandler),
    (r"/logout",Logout),
    (r"/people",Person),
    (r"/remove",RemoveFriend),
    (r"/join",JoinFriend),
    (r"/group",ShowGroup),
    (r"/leave",RemoveGroup),
    (r"/joinG",JoinGroup),
    (r"/createG",PCreateGroup),
    (r"/ws1",SocketHandler),
    (r"/chat",ChatHandlerG),

    # (r"/delete",RemoveFriend)
],debug=True,
static_path='static', cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=")

if __name__ == "__main__":
    application.listen(8000)
tornado.ioloop.IOLoop.instance().start()
