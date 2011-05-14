import re

class Address(object):
	"""
	>>> a1 = Address('sip:john@example.org')
	>>> b1 = Address('<sip:john@example.org>')
	>>> c1 = Address('John Doe <sip:john@example.org>')
	>>> d1 = Address('"John Doe" <sip:john@example.org>')
	>>> print(str(a1) == str(b1) and str(c1) == str(d1))
	True
	"""
	_syntax = [
		re.compile('^(?P<name>[a-zA-Z0-9\-\.\_\+\~\ \t]*)<(?P<uri>[^>]+)>'), 
		re.compile('^(?:"(?P<name>[a-zA-Z0-9\-\.\_\+\~\ \t]+)")[\ \t]*<(?P<uri>[^>]+)>'),
		re.compile('^[\ \t]*(?P<name>)(?P<uri>[^;]+)')
	]

	def __init__(self, value = None):
		self.must_quote = False
		if value != None:
			self.loads(value)

	def __repr__(self):
		return self.dumps()

	def loads(self, value):
		"""
		Parse an address

		:return: length used
		:rtype: Integer
		"""
		for s in self._syntax:
			m = s.match(value)
			if m:
				self.display_name = m.groups()[0].strip()
				self.uri = URI(m.groups()[1].strip())
				return m.end()

		return 0

	def dumps(self):
		r = ''
		if self.display_name:
			r = '"' + self.display_name + '"'
			if self.uri:
				r = r + ' '
			else:
				r = r + ''

		if not self.uri:
			return r
	
		if self.must_quote:
			r = r + '<' + str(self.uri) + '>'
		else:
			r = r + str(self.uri)

		return r

class URI(object):
	"""
	>>> print(URI("sip:john@example.org"))
	sip:john@example.org
	>>> u = URI("sip:foo:bar@example.org:5060;transport=udp;novalue;param=pval?header=val&second=sec_val")
	>>> print(u.scheme, u.user, u.password, u.host, u.port, len(u.params), len(u.headers))
	sip foo bar example.org 5060 3 2
	>>> d = u.dumps()
	>>> u = URI(d)
	>>> print(u.dumps() == d)
	True
	"""


	_syntax = re.compile('^(?P<scheme>[a-zA-Z][a-zA-Z0-9\+\-\.]*):'  # scheme
		+ '(?:(?:(?P<user>[a-zA-Z0-9\-\_\.\!\~\*\'\(\)&=\+\$,;\?\/\%]+)' # user
		+ '(?::(?P<password>[^:@;\?]+))?)@)?' # password
		+ '(?:(?:(?P<host>[^;\?:]*)(?::(?P<port>[\d]+))?))'  # host, port
		+ '(?:;(?P<params>[^\?]*))?' # parameters
		+ '(?:\?(?P<headers>.*))?$') # headers

	def __init__(self, value = None):
		self.scheme = None
		self.user = None
		self.password = None
		self.host = None
		self.port = None
		self.params = {}
		self.headers = []

		self.loads(value)

	def __repr__(self):
		return self.dumps()

	def __str__(self):
		return self.dumps()

	def dumps(self):
		r = self.scheme + ":"
		if self.user:
			r = r + self.user
			if self.password:
				r = r + ":" + self.password

			r = r + "@"
		if self.host:
			r = r + self.host
			if self.port:
				r = r + ":" + str(self.port)

		if len(self.params) > 0:
			r = r + ";" + "j".join([n + "=" + v for n,v in self.params.items()])

		if len(self.headers) > 0:
			r = r + "?" + "&".join(self.headers)

		return r

	def loads(self, value):
		if value:
			m = self._syntax.match(value)
			if not m:
				print("value", value)
				# ToDo: error handling
				return
			self.scheme = m.group("scheme")
			self.user = m.group("user")
			self.password = m.group("password")
			self.host = m.group("host")
			self.port = m.group("port")
			params = m.group("params")
			headers = m.group("headers")

			# ToDo: error check
			try:
				self.port = int(self.port)
			except:
				pass

			if params:
				for param in params.split(";"):
					t = param.partition("=")
					n = t[0].strip()
					v = t[2].strip()
					self.params[n] = v

			if headers:
				self.headers = headers.split("&")