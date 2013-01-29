# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
	## if NOT running on Google App Engine use SQLite or other DB
	db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
	## connect to Google BigTable (optional 'google:datastore://namespace')
	db = DAL('google:datastore')
	## store sessions and tickets there
	session.connect(request, response, db=db)
	## or store session in Memcache, Redis, etc.
	## from gluon.contrib.memdb import MEMDB
	## from google.appengine.api.memcache import Client
	## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)

from gluon.contrib.login_methods import oauth20_account as oauth

from gluon.contrib.login_methods.oauth10a_account import OAuthAccount

from tweepy import API, TweepError, OAuthHandler
#from  twitter_account import TwitterAccount

class TwitterAccount(object):
	"""
	"""

	def __redirect_uri(self, next=None):
		"""Build the uri used by the authenticating server to redirect
		the client back to the page originating the auth request.
		Appends the _next action to the generated url so the flows continues.
		"""
		r = self.request
		http_host = 'geekparty.su'#r.env.http_x_forwarded_for
		if not http_host:
			http_host = r.env.http_host

		url_scheme = 'http'#r.env.wsgi_url_scheme
		if next:
			path_info = next
		else:
			path_info = r.env.path_info
		uri = '%s://%s%s' % (url_scheme, http_host, path_info)
		if r.get_vars and not next:
			uri += '?' + urlencode(r.get_vars)
		return uri


	def __init__(self, g, client_id, client_secret, auth_url, token_url, access_token_url):
		self.globals = g
		self.client_id = client_id
		self.client_secret = client_secret
		self.code = None
		self.request = g['request']
		self.session = g['session']
		self.auth_url = auth_url
		self.token_url = token_url
		self.access_token_url = access_token_url


		print "new"
		self.handler = None



	def login_url(self, next="/"):
		self.__oauth_login(next)
		return next

	def logout_url(self, next="/"):
		print "logout"
		self.session.request_token = None
		self.session.access_token = None
		return next

	def get_user(self):
		'''Get user data.

		Since OAuth does not specify what a user
		is, this function must be implemented for the specific
		provider.
		'''
		raise NotImplementedError("Must override get_user()")

	def getApi(self):
		handler =  self.getAuthHandler()
		if not handler:
			return  None

		return API(handler)




	def accessToken(self):
		if self.session.access_token:
			# return the token (TODO: does it expire?)
			auth = OAuthHandler(self.client_id, self.client_secret);
			auth.set_access_token( self.session.access_token.key
								 , self.session.access_token.secret)

			return auth


		if self.session.request_token:
			# Exchange the request token with an authorization token.
			token = self.session.request_token
			self.session.request_token = None

			auth = OAuthHandler( self.client_id, self.client_secret )
			auth.set_request_token(token.key, token.secret)

			try:
				self.session.access_token = auth.get_access_token(self.request.vars.oauth_verifier)
			except tweepy.TweepError:

				print 'Error! Failed to get access token.'

			print self.session.access_token

			return auth

		return None


	def __oauth_login(self, next):
		'''This method redirects the user to the authenticating form
		on authentication server if the authentication code
		and the authentication token are not available to the
		application yet.

		Once the authentication code has been received this method is
		called to set the access token into the session by calling
		accessToken()
		'''

		if not self.accessToken():
			# setup the client
			auth = OAuthHandler( self.client_id
								, self.client_secret
								, callback=self.__redirect_uri(next) )

			redirect_url = None
			try:
				redirect_url = auth.get_authorization_url()
				self.session.request_token = auth.request_token

			except tweepy.TweepError:
				print 'Error! Failed to get request token.'


			if redirect_url:
				HTTP = self.globals['HTTP']
				raise HTTP(307,

					"You are not authenticated: you are being redirected to the <a href='" + redirect_url + "'> authentication server</a>",
					Location=redirect_url)


		return None


class MyTwitterAccount(TwitterAccount):
	'''OAuth impl for Twitter'''
	CLIENT_ID ="YtQaPMgAcsApV65GnsrRiQ"
	CLIENT_SECRET ="ZQGLlxIwtRgUiPu9uIdOE8Gsw2CL3ncq0Jx6lNUHs"

	AUTH_URL="https://api.twitter.com/oauth/authorize"
	ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
	TOKEN_URL="https://api.twitter.com/oauth/request_token"



	def __init__(self):
		TwitterAccount.__init__(self, globals(),
			client_id=self.CLIENT_ID,
			client_secret=self.CLIENT_SECRET,
			auth_url=self.AUTH_URL,
			token_url=self.TOKEN_URL,
			access_token_url = self.ACCESS_TOKEN_URL )

		self.api = None




	def get_user(self):
		'''
		 Returns the user using the Graph API.
		'''

		user = None

		auth = self.accessToken()
		if not auth:
			return None;

		api =  API(auth)
		try:
			user = api.me()
		except TweepError, e:
			self.session.access_token = None
			self.session.token = None
			return  None

		print user.__dict__.keys()

		if user:
			return dict( first_name = user.screen_name,
						 last_name = user.name,
						 username = user.screen_name,
						 registration_id = user.screen_name,
						 avatar = user.profile_image_url )



#auth.settings.login_methods = [oauth.OAuthAccount(client_id=)]

crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables

auth.settings.extra_fields['auth_user']= [
	Field('avatar')	]

auth.define_tables(username=False, signature=False)
#auth.settings.extra_fields[auth.settings.table_user_name] = [Field('avatar', length=128, default="")]

#auth.define_tables()

auth.settings.actions_disabled=['register',
								'change_password','request_reset_password']#,'profile']
auth.settings.login_form = MyTwitterAccount()

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')


#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
## test
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login

db.define_table( 'party'
				, Field('name', length=100, required=True, requires=IS_NOT_EMPTY())
				, Field('is_active', 'boolean', required=True)
				, Field('start_date', 'datetime', required=True, requires=IS_NOT_EMPTY())
				, Field('end_date',   'datetime', required=True, requires=IS_NOT_EMPTY())
				, Field('wikiSlug', length=100)
				, format='%(name)s')


db.define_table( 'entry'
				, Field('party', db.party, required=True, writable=False, readable=False)
			    , Field('creator', db.auth_user, required=True, requires=IS_NOT_EMPTY(), writable=False, readable=False)

				, Field('hashTag', length=50, required=True, requires=[ IS_NOT_EMPTY()
																	  , IS_MATCH('^#\S+$'
						, error_message='not a twitter hashtag: eg #myentry')]
						, unique=True
						, comment='twitter timeline hashtag')

				, Field('authors', 'list:string', required=True
												, requires=[IS_NOT_EMPTY()
															, IS_LIST_OF( [IS_NOT_EMPTY(), IS_MATCH('^@\S+$'
																	  , error_message='not a twitter user: eg @user')])]
												, comment='twitter timeline hashtag')
				, Field('teamDescription','text')
				, Field('teamLogoUrl', requires=IS_EMPTY_OR(IS_URL()), length=500)
				, Field('sourceUrl', required=True, requires=IS_URL(), length=500)
				, Field('embededTimeline','text', required=True, requires=IS_NOT_EMPTY())
				, Field('embededStream', 'text')


				#entry data
				, Field('name', length=100, label='Entry Name', comment='')
				, Field('description', 'text')
				, Field('entryUrl', length=500)
				, Field('screenShotUrl', length=500)

				, Field('update_date', 'datetime', default=request.now, writable=False, readable=False)
				, Field('pub_date',    'datetime', default=request.now, writable=False, readable=False)
				, Field('likes', 'integer', default=0, writable=False, readable=False)
				, Field('dislikes', 'integer', default=0, writable=False, readable=False)
				, format='%(hashTag)s')


globals()['currentParty'] = db.party(db.party.is_active==True)



