from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'Geek Party'
settings.subtitle = 'creative'
settings.author = 'geekparty.ru'
settings.author_email = 'nulldivide@gmail.com'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Customize'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '4fccd00b-c2ee-444c-94fe-6aa8485fa8d3'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = ['wiki', 'comments', 'tagging', 'rating']
