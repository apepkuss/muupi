
def cpreprocess_parse(stateStruct, input):
	"""
	:type stateStruct: State
	:param str | iterable[char] input: not-yet preprocessed C code
	:returns preprocessed C code, iterator of chars
	This removes comments and can skip over parts, which is controlled by
	the C preprocessor commands (`#if 0` parts or so).
	We will not do C preprocessor macro substitutions here.
	The next func which gets this output is cpre2_parse().
	"""
	cmd = ""
	arg = ""
	state = 0
	statebeforecomment = None
	for c in input:
		breakLoop = False
		while not breakLoop:
			breakLoop = True

			if state == 0:
				if c == "#":
					cmd = ""
					arg = None
					state = 1
				elif c == "/":
					statebeforecomment = 0
					state = 20
				elif c == '"':
					if not stateStruct._preprocessIgnoreCurrent: yield c
					state = 10
				elif c == "'":
					if not stateStruct._preprocessIgnoreCurrent: yield c
					state = 12
				else:
					if not stateStruct._preprocessIgnoreCurrent: yield c
			elif state == 1: # start of preprocessor command
				if c in SpaceChars: pass
				elif c == "\n": state = 0
				else:
					cmd = c
					state = 2
			elif state == 2: # in the middle of the preprocessor command
				if c in SpaceChars:
					if arg is None: arg = ""
					else: arg += c
				elif c == "(":
					if arg is None: arg = c
					else: arg += c
				elif c == "/":
					state = 20
					statebeforecomment = 2
				elif c == '"':
					state = 3
					if arg is None: arg = ""
					arg += c
				elif c == "'":
					state = 4
					if arg is None: arg = ""
					arg += c
				elif c == "\\": state = 5 # escape next
				elif c == "\n":
					for c in handle_cpreprocess_cmd(stateStruct, cmd, arg): yield c
					state = 0
				else:
					if arg is None: cmd += c
					else: arg += c
			elif state == 3: # in '"' in arg in command
				arg += c
				if c == "\n":
					stateStruct.error("preproc parse: unfinished str")
					state = 0
				elif c == "\\": state = 35
				elif c == '"': state = 2
			elif state == 35: # in esp in '"' in arg in command
				arg += c
				state = 3
			elif state == 4: # in "'" in arg in command
				arg += c
				if c == "\n":
					stateStruct.error("preproc parse: unfinished char str")
					state = 0
				elif c == "\\": state = 45
				elif c == "'": state = 2
			elif state == 45: # in esp in "'" in arg in command
				arg += c
				state = 4
			elif state == 5: # after escape in arg in command
				if c == "\n": state = 2
				else: pass # ignore everything, wait for newline
			elif state == 10: # after '"'
				if not stateStruct._preprocessIgnoreCurrent: yield c
				if c == "\\": state = 11
				elif c == '"': state = 0
				else: pass
			elif state == 11: # escape in "str
				if not stateStruct._preprocessIgnoreCurrent: yield c
				state = 10
			elif state == 12: # after "'"
				if not stateStruct._preprocessIgnoreCurrent: yield c
				if c == "\\": state = 13
				elif c == "'": state = 0
				else: pass
			elif state == 13: # escape in 'str
				if not stateStruct._preprocessIgnoreCurrent: yield c
				state = 12
			elif state == 20: # after "/", possible start of comment
				if c == "*": state = 21 # C-style comment
				elif c == "/": state = 25 # C++-style comment
				else:
					state = statebeforecomment
					statebeforecomment = None
					if state == 0:
						if not stateStruct._preprocessIgnoreCurrent:
							yield "/"
							yield c
					elif state == 2:
						if arg is None: arg = ""
						arg += "/" + c
					else:
						stateStruct.error("preproc parse: internal error after possible comment. didn't expect state " + str(state))
						state = 0 # best we can do
			elif state == 21: # C-style comment
				if c == "*": state = 22
				else: pass
			elif state == 22: # C-style comment after "*"
				if c == "/":
					state = statebeforecomment
					statebeforecomment = None
				elif c == "*": pass
				else: state = 21
			elif state == 25: # C++-style comment
				if c == "\n":
					state = statebeforecomment
					statebeforecomment = None
					breakLoop = False # rehandle return
				else: pass
			else:
				stateStruct.error("internal error: invalid state " + str(state))
				state = 0 # reset. it's the best we can do

		if c == "\n": stateStruct.incIncludeLineChar(line=1)
		elif c == "\t": stateStruct.incIncludeLineChar(char=4, charMod=4)
		else: stateStruct.incIncludeLineChar(char=1)

	# yield dummy additional new-line at end
	yield "\n"


class _CBase(object):
	def __init__(self, content=None, rawstr=None, **kwargs):
		self.content = content
		self.rawstr = rawstr
		for k,v in kwargs.items():
			setattr(self, k, v)
	def __repr__(self):
		if self.content is None: return "<" + self.__class__.__name__ + ">"
		return "<" + self.__class__.__name__ + " " + repr(self.content) + ">"
	def __eq__(self, other):
		return self.__class__ is other.__class__ and self.content == other.content
	def __ne__(self, other):
		return not self == other
	def __hash__(self): return hash(self.__class__) + 31 * hash(self.content)
	def asCCode(self, indent=""): return indent + self.content


class CStr(_CBase):
	def __repr__(self): return "<" + self.__class__.__name__ + " " + repr(self.content) + ">"

	def asCCode(self, indent=""): return indent + '"' + escape_cstr(self.content) + '"'


class CChar(_CBase):
	def __init__(self, content=None, rawstr=None, **kwargs):
		if isinstance(content, (unicode, str)): content = ord(content)
		assert isinstance(content, int), "CChar expects int, got " + repr(content)
		assert 0 <= content <= 255, "CChar expects number in range 0-255, got " + str(content)
		_CBase.__init__(self, content, rawstr, **kwargs)

	def __repr__(self):
		return "<" + self.__class__.__name__ + " " + repr(self.content) + ">"

	def asCCode(self, indent=""):
		if isinstance(self.content, str):
			return indent + "'" + escape_cstr(self.content) + "'"
		else:
			assert isinstance(self.content, int)
			return indent + "'" + escape_cstr(chr(self.content)) + "'"


class CNumber(_CBase):
	typeSpec = None  # prefix like "f", "i" or so, or None

	def asCCode(self, indent=""): return indent + self.rawstr


class CIdentifier(_CBase): pass


class COp(_CBase): pass


class CSemicolon(_CBase):
	def asCCode(self, indent=""): return indent + ";"


class COpeningBracket(_CBase): pass


class CClosingBracket(_CBase): pass


def cpre2_parse_number(stateStruct, s):
	if len(s) > 1 and s[0] == "0" and s[1] in NumberChars:
		try:
			s = s.rstrip("ULul")
			return long(s, 8)
		except Exception as e:
			stateStruct.error("cpre2_parse_number: " + s + " looks like octal but got error " + str(e))
			return 0
	if len(s) > 1 and s[0] == "0" and s[1] in "xX":
		try:
			s = s.rstrip("ULul")
			return long(s, 16)
		except Exception as e:
			stateStruct.error("cpre2_parse_number: " + s + " looks like hex but got error " + str(e))
			return 0
	try:
		s = s.rstrip("ULul")
		return long(s)
	except Exception as e:
		stateStruct.error("cpre2_parse_number: " + s + " cannot be parsed: " + str(e))
		return 0


def _cpre2_parse_args(stateStruct, input, brackets, separator=COp(",")):
	"""
	:type stateStruct: State
	:param iterable[char] input: like cpre2_parse
	:param list[str] brackets: opening brackets stack
	:param sep_type: the separator type, e.g. CSemicolon or COp
	:returns list of args, where each arg is a list of tokens from cpre2_parse.
	:rtype: list[list[token]]
	"""
	initial_bracket_len = len(brackets)
	args = []
	for s in cpre2_parse(stateStruct, input, brackets=brackets):
		if len(brackets) < initial_bracket_len:
			# We got the final closing bracket. We have finished parsing the args.
			assert isinstance(s, CClosingBracket)
			assert len(brackets) == initial_bracket_len - 1
			return args
		if len(brackets) == initial_bracket_len and s == separator:
			args.append("")
		else:
			if not args: args.append("")
			if args[-1]: args[-1] += " "
			args[-1] += s.asCCode()
	stateStruct.error("cpre2 parse args: runaway")
	return args


class _Pre2ParseStream:
	def __init__(self, input):
		self.input = input
		self.macro_blacklist = set()
		self.buffer_stack = [[None, ""]]  # list[(macroname,buffer)]

	def next_char(self):
		for i in reversed(range(len(self.buffer_stack))):
			if not self.buffer_stack[i][1]: continue
			c = self.buffer_stack[i][1][0]
			self.buffer_stack[i][1] = self.buffer_stack[i][1][1:]
			# finalize handling will be in finalize_char()
			return c
		try:
			return next(self.input)
		except StopIteration:
			return None

	def add_macro(self, macroname, resolved, c):
		self.buffer_stack += [[macroname, resolved]]
		self.macro_blacklist.add(macroname)
		self.buffer_stack[-2][1] = c + self.buffer_stack[-2][1]

	def finalize_char(self, laststr):
		# Finalize buffer_stack here. Here because the macro_blacklist needs to be active
		# in the code above.
		if not laststr and len(self.buffer_stack) > 1 and not self.buffer_stack[-1][1]:
			self.macro_blacklist.remove(self.buffer_stack[-1][0])
			self.buffer_stack = self.buffer_stack[:-1]


def cpre2_parse(stateStruct, input, brackets=None):
	"""
	:type stateStruct: State
	:param str | iterable[char] | _Pre2ParseStream input: chars of preprocessed C code.
		except of macro substitution. usually via cpreprocess_parse().
	:param list[str] | None brackets: opening brackets stack
	:returns token iterator. this will also substitute macros
	The input comes more or less from cpreprocess_parse().
	This output will be handled by cpre3_parse().
	"""
	state = 0
	if brackets is None: brackets = []
	if not isinstance(input, _Pre2ParseStream):
		input = _Pre2ParseStream(input)
	laststr = ""
	macroname = ""
	macroargs = []
	while True:
		c = input.next_char()
		if c is None:
			break
		breakLoop = False
		while not breakLoop:
			breakLoop = True
			if state == 0:
				if c in SpaceChars + "\n":
					pass
				elif c in NumberChars:
					laststr = c
					state = 10
				elif c == '"':
					laststr = ""
					state = 20
				elif c == "'":
					laststr = ""
					state = 25
				elif c in LetterChars + "_":
					laststr = c
					state = 30
				elif c in OpeningBrackets:
					yield COpeningBracket(c, brackets=list(brackets))
					brackets.append(c)
				elif c in ClosingBrackets:
					if len(brackets) == 0 or ClosingBrackets[
										len(OpeningBrackets) - OpeningBrackets.index(brackets[-1]) - 1] != c:
						stateStruct.error("cpre2 parse: got '" + c + "' but bracket level was " + str(brackets))
					else:
						brackets[:] = brackets[:-1]
						yield CClosingBracket(c, brackets=list(brackets))
				elif c in OpChars:
					laststr = ""
					state = 40
					breakLoop = False
				elif c == ";":
					yield CSemicolon()
				elif c == "\\":
					state = 1
				else:
					stateStruct.error("cpre2 parse: didn't expected char %r in state %i" % (c, state))
			elif state == 1:  # escape without context
				if c != "\n":
					stateStruct.error("cpre2 parse: didn't expected char %r in state %i" % (c, state))
				# Just ignore it in any case.
				state = 0
			elif state == 10:  # number (no correct float handling, will be [number, op("."), number])
				if c in NumberChars:
					laststr += c
				elif c in LetterChars + "_":
					laststr += c  # error handling will be in number parsing, not here
				else:
					yield CNumber(cpre2_parse_number(stateStruct, laststr), laststr)
					laststr = ""
					state = 0
					breakLoop = False
			elif state == 20:  # "str
				if c == '"':
					yield CStr(laststr)
					laststr = ""
					state = 0
				elif c == "\\":
					state = 21
				else:
					laststr += c
			elif state == 21:  # escape in "str
				laststr += simple_escape_char(c)
				state = 20
			elif state == 25:  # 'str
				if c == "'":
					if len(laststr) > 1 and laststr[0] == '\0':  # hacky check for '\0abc'-like strings.
						yield CChar(int(laststr[1:], 8))
					else:
						yield CChar(laststr)
					laststr = ""
					state = 0
				elif c == "\\":
					state = 26
				else:
					laststr += c
			elif state == 26:  # escape in 'str
				laststr += simple_escape_char(c)
				state = 25
			elif state == 30:  # identifier
				if c in NumberChars + LetterChars + "_":
					laststr += c
				else:
					if laststr in stateStruct.macros and laststr not in input.macro_blacklist:
						macroname = laststr
						macroargs = []
						state = 31
						if stateStruct.macros[macroname].args is None:
							state = 32  # finalize macro directly. there can't be any args
						breakLoop = False
						laststr = ""
					else:
						if laststr == "__FILE__":
							yield CStr(stateStruct.curFile())
						elif laststr == "__LINE__":
							yield CNumber(stateStruct.curLine())
						else:
							yield CIdentifier(laststr)
						laststr = ""
						state = 0
						breakLoop = False
			elif state == 31:  # after macro identifier
				if c in SpaceChars + "\n":
					pass
				elif c in OpeningBrackets:
					if c != "(":
						state = 32
						breakLoop = False
					else:
						macroargs = _cpre2_parse_args(stateStruct, input, brackets=brackets + [c])
						state = 32
					# break loop, we consumed this char
				else:
					state = 32
					breakLoop = False
			elif state == 32:  # finalize macro
				try:
					resolved = stateStruct.macros[macroname].eval(stateStruct, macroargs)
				except Exception as e:
					stateStruct.error("cpre2 parse unfold macro " + macroname + " error: " + repr(e))
					resolved = ""
				input.add_macro(macroname, resolved, c)
				state = 0
			elif state == 40:  # op
				if c in OpChars:
					if laststr != "" and laststr + c not in LongOps:
						yield COp(laststr)
						laststr = ""
					laststr += c
				else:
					yield COp(laststr)
					laststr = ""
					state = 0
					breakLoop = False
			else:
				stateStruct.error("cpre2 parse: internal error. didn't expected state " + str(state))
		input.finalize_char(laststr)


def cpre2_tokenstream_asCCode(input):
	needspace = False
	wantnewline = False
	indentLevel = ""
	needindent = False

	for token in input:
		if wantnewline:
			if isinstance(token, CSemicolon):
				pass
			else:
				yield "\n"
				needindent = True
			wantnewline = False
			needspace = False
		elif needspace:
			if isinstance(token, CSemicolon):
				pass
			elif token == COpeningBracket("("):
				pass
			elif token == CClosingBracket(")"):
				pass
			elif token == COpeningBracket("["):
				pass
			elif token == CClosingBracket("]"):
				pass
			elif token in [COp("++"), COp("--"), COp(",")]:
				pass
			else:
				yield " "
			needspace = False

		if token == CClosingBracket("}"): indentLevel = indentLevel[:-1]
		if needindent:
			yield indentLevel
			needindent = False

		yield token.asCCode()

		if token == COpeningBracket("{"): indentLevel += "\t"

		if token == CSemicolon():
			wantnewline = True
		elif token == COpeningBracket("{"):
			wantnewline = True
		elif token == CClosingBracket("}"):
			wantnewline = True
		elif isinstance(token, COpeningBracket):
			pass
		elif isinstance(token, CClosingBracket):
			pass
		else:
			needspace = True


class CBody(object):
	def __init__(self, parent):
		self.parent = parent
		self._bracketlevel = []
		self.typedefs = {}
		self.structs = {}
		self.unions = {}
		self.enums = {}
		self.funcs = {}
		self.vars = {}
		self.enumconsts = {}
		self.contentlist = []

	def __str__(self): return "CBody %s" % self.contentlist

	def __repr__(self): return "<%s>" % self

	def asCCode(self, indent=""):
		s = indent + "{\n"
		for c in self.contentlist:
			s += asCCode(c, indent + "\t", fullDecl=True) + ";\n"
		s += indent + "}"
		return s


class CEnumBody(CBody):
	def asCCode(self, indent=""):
		s = indent + "{\n"
		for c in self.contentlist:
			s += asCCode(c, indent + "\t") + ",\n"
		s += indent + "}"
		return s


def findIdentifierInBody(body, name):
	if name in body.enumconsts:
		return body.enumconsts[name]
	if body.parent is not None:
		return findIdentifierInBody(body.parent, name)
	return None


def make_type_from_typetokens(stateStruct, curCObj, type_tokens):
	if not type_tokens:
		return None
	if len(type_tokens) == 1 and isinstance(type_tokens[0], _CBaseWithOptBody):
		t = type_tokens[0]
	elif tuple(type_tokens) in stateStruct.CBuiltinTypes:
		t = CBuiltinType(tuple(type_tokens))
	elif len(type_tokens) > 1 and type_tokens[-1] == "*":
		t = CPointerType(make_type_from_typetokens(stateStruct, curCObj, type_tokens[:-1]))
	elif len(type_tokens) == 1:
		assert isinstance(type_tokens[0], (str, unicode))
		t = findObjInNamespace(stateStruct, curCObj, type_tokens[0])
		if not isType(t):
			stateStruct.error("type token is not a type: %s" % t)
			t = None
	elif type_tokens == [".", ".", "."]:
		t = CVariadicArgsType()
	else:
		stateStruct.error("type tokens not handled: %s" % type_tokens)
		t = None
	return t


def asCCode(stmnt, indent="", fullDecl=False):
	if not fullDecl:
		if isinstance(stmnt, CFunc): return indent + stmnt.name
		if isinstance(stmnt, CStruct): return indent + "struct " + stmnt.name
		if isinstance(stmnt, CUnion): return indent + "union " + stmnt.name
		if isinstance(stmnt, CEnum): return indent + "enum " + stmnt.name
	if hasattr(stmnt, "asCCode"):
		return stmnt.asCCode(indent)
	assert False, "don't know how to handle " + str(stmnt)


class _CBaseWithOptBody(object):
	NameIsRelevant = True
	AutoAddToContent = True
	AlwaysNonZero = False
	StrOutAttribList = [
		("args", bool, None, str),
		("arrayargs", bool, None, str),
		("body", None, None, lambda x: "<...>"),
		("value", None, None, str),
		("defPos", None, "@", str),
	]

	def __init__(self, **kwargs):
		self._type_tokens = []
		self._bracketlevel = None
		self._finalized = False
		self.defPos = None
		self.type = None
		self.attribs = []
		self.name = None
		self.args = []
		self.arrayargs = []
		self.body = None
		self.value = None
		self.parent = None
		for k, v in kwargs.items():
			setattr(self, k, v)

	@classmethod
	def overtake(cls, obj):
		obj.__class__ = cls

	# no cls.__init__ because it would overwrite all our attribs!

	def isDerived(self):
		return self.__class__ != _CBaseWithOptBody

	def __str__(self):
		if self.NameIsRelevant:
			name = ("'" + self.name + "' ") if self.name else "<noname> "
		else:
			name = ("name: '" + self.name + "' ") if self.name else ""
		t = self.type or self._type_tokens
		l = []
		if self.attribs: l += [("attribs", self.attribs)]
		if t: l += [("type", t)]
		for attrName, addCheck, displayName, displayFunc in self.StrOutAttribList:
			a = getattr(self, attrName)
			if addCheck is None: addCheck = lambda x: x is not None
			if addCheck(a):
				if displayName is None: displayName = attrName
				l += [(displayName, displayFunc(a))]
		return \
			self.__class__.__name__ + " " + \
			name + \
			", ".join(map((lambda a: a[0] + ": " + str(a[1])), l))

	def __repr__(self):
		return "<" + str(self) + ">"

	def __nonzero__(self):
		return \
			self.AlwaysNonZero or \
			bool(self._type_tokens) or \
			bool(self.type) or \
			bool(self.name) or \
			bool(self.args) or \
			bool(self.arrayargs) or \
			bool(self.body)

	def finalize(self, stateStruct, addToContent=None):
		if self._finalized:
			stateStruct.error("internal error: " + str(self) + " finalized twice")
			return
		self._finalized = True
		if self.defPos is None:
			self.defPos = stateStruct.curPosAsStr()
		if not self: return

		if addToContent is None: addToContent = self.AutoAddToContent

		# print "finalize", self, "at", stateStruct.curPosAsStr()
		if addToContent and self.parent is not None and self.parent.body and hasattr(self.parent.body, "contentlist"):
			self.parent.body.contentlist.append(self)

	def addToBody(self, obj):
		if self.body is None:
			self.body = obj
		else:
			assert isinstance(self.body, CBody)
			self.body.contentlist.append(obj)

	def _copy(self, value, parent=None, name=None, leave_out_attribs=()):
		if isinstance(value, (int, long, float, str, unicode)) or value is None:
			return value
		elif isinstance(value, list):
			return [self._copy(v, parent=parent) for v in value]
		elif isinstance(value, tuple):
			return tuple([self._copy(v, parent=parent) for v in value])
		elif isinstance(value, dict):
			return {k: self._copy(v, parent=parent) for (k, v) in value.items()}
		elif isinstance(value, (_CBase, _CBaseWithOptBody, CType, CBody)):
			new = value.__class__.__new__(value.__class__)
			for k, v in vars(value).items():
				if k in leave_out_attribs:
					continue
				if k == "parent":
					new.parent = parent
				else:
					setattr(new, k, self._copy(v, parent=new, name=k))
			return new
		else:
			assert False, "dont know how to handle %r %r (%s)" % (name, value, value.__class__)

	def copy(self, leave_out_attribs=("body",)):
		return self._copy(self, parent=self.parent, leave_out_attribs=leave_out_attribs)

	def depth(self):
		if self.parent is None: return 1
		return self.parent.depth() + 1

	def getCType(self, stateStruct):
		raise Exception(str(self) + " cannot be converted to a C type")

	def findAttrib(self, stateStruct, attrib):
		if self.body is None:
			# it probably is the pre-declaration. but we might find the real-one
			if isinstance(self, CStruct):
				D = "structs"
			elif isinstance(self, CUnion):
				D = "unions"
			elif isinstance(self, CEnum):
				D = "enums"
			self = getattr(stateStruct, D).get(self.name, self)
		if self.body is None: return None
		for c in self.body.contentlist:
			if not isinstance(c, CVarDecl): continue
			if c.name == attrib: return c
		return None

	def asCCode(self, indent=""):
		raise NotImplementedError(str(self) + " asCCode not implemented")


class CTypedef(_CBaseWithOptBody):
	def finalize(self, stateStruct):
		if self._finalized:
			stateStruct.error("internal error: " + str(self) + " finalized twice")
			return

		self.type = make_type_from_typetokens(stateStruct, self, self._type_tokens)
		_CBaseWithOptBody.finalize(self, stateStruct)

		if self.type is None:
			stateStruct.error("finalize typedef " + str(self) + ": type is unknown")
			return
		if self.name is None:
			stateStruct.error("finalize typedef " + str(self) + ": name is unset")
			return

		self.parent.body.typedefs[self.name] = self

	def getCType(self, stateStruct):
		return getCType(self.type, stateStruct)

	def asCCode(self, indent=""):
		return indent + "typedef\n" + asCCode(self.type, indent, fullDecl=True) + " " + self.name


def resolveTypedef(t):
	while isinstance(t, CTypedef):
		t = t.type
	return t


class CFuncPointerBase(object): pass


class CFuncPointerDecl(_CBaseWithOptBody, CFuncPointerBase):
	def finalize(self, stateStruct, addToContent=None):
		if self._finalized:
			stateStruct.error("internal error: " + str(self) + " finalized twice")
			return

		if not self.type:
			self.type = make_type_from_typetokens(stateStruct, self, self._type_tokens)
		_CBaseWithOptBody.finalize(self, stateStruct, addToContent)

		if self.type is None:
			stateStruct.error("finalize " + str(self) + ": type is unknown")
		# Name can be unset. It depends where this is declared.

	def getCType(self, stateStruct, workaroundPtrReturn=True, wrap=True):
		if workaroundPtrReturn and isinstance(self.type, CPointerType):
			# https://bugs.python.org/issue5710
			restype = ctypes.c_void_p
		else:
			restype = getCType(self.type, stateStruct)
		if wrap: restype = wrapCTypeClassIfNeeded(restype)
		argtypes = map(lambda a: getCType(a, stateStruct), self.args)
		if wrap: argtypes = map(wrapCTypeClassIfNeeded, argtypes)
		return ctypes.CFUNCTYPE(restype, *argtypes)

	def asCCode(self, indent=""):
		return indent + asCCode(self.type) + "(*" + self.name + ") (" + ", ".join(map(asCCode, self.args)) + ")"


def _addToParent(obj, stateStruct, dictName=None, listName=None, allowPredec=True):
	assert dictName or listName
	assert hasattr(obj.parent, "body")
	d = getattr(obj.parent.body, dictName or listName)
	if dictName:
		if obj.name is None:
			# might be part of a typedef, so don't error
			return

		if obj.name in d:
			if allowPredec and d[obj.name].body is None:
				# If the body is empty, it was a pre-declaration and it is ok to overwrite it now.
				d[obj.name] = obj
			elif "extern" in d[obj.name].attribs:
				# Otherwise, if we explicitely use the "extern" attribute, it's also ok.
				d[obj.name] = obj
			else:
				# Otherwise however, it is an error.
				stateStruct.error(
					"finalize " + str(obj) + ": a previous equally named declaration exists: " + str(d[obj.name]))
		else:
			d[obj.name] = obj
	else:
		assert listName is not None
		d.append(obj)


def _finalizeBasicType(obj, stateStruct, dictName=None, listName=None, addToContent=None, allowPredec=True):
	if obj._finalized:
		stateStruct.error("internal error: " + str(obj) + " finalized twice")
		return

	if addToContent is None:
		addToContent = obj.name is not None

	if obj.type is None:
		obj.type = make_type_from_typetokens(stateStruct, obj, obj._type_tokens)
	_CBaseWithOptBody.finalize(obj, stateStruct, addToContent=addToContent)

	if addToContent and hasattr(obj.parent, "body") and not getattr(obj, "_already_added", False):
		_addToParent(obj=obj, stateStruct=stateStruct, dictName=dictName, listName=listName, allowPredec=allowPredec)


class CFunc(_CBaseWithOptBody):
	finalize = lambda *args, **kwargs: _finalizeBasicType(*args, dictName="funcs", **kwargs)

	def getCType(self, stateStruct):
		restype = getCType(self.type, stateStruct)
		argtypes = map(lambda a: getCType(a, stateStruct), self.args)
		return ctypes.CFUNCTYPE(restype, *argtypes)

	def asCCode(self, indent=""):
		s = indent + asCCode(self.type) + " " + self.name + "(" + ", ".join(map(asCCode, self.args)) + ")"
		if self.body is None: return s
		s += "\n"
		s += asCCode(self.body, indent)
		return s


class CVarDecl(_CBaseWithOptBody):
	finalize = lambda *args, **kwargs: _finalizeBasicType(*args, dictName="vars", allowPredec=False, **kwargs)

	def clearDeclForNextVar(self):
		if hasattr(self, "bitsize"): delattr(self, "bitsize")
		while self._type_tokens and self._type_tokens[-1] in ("*",):
			self._type_tokens.pop()

	def asCCode(self, indent=""):
		s = indent + asCCode(self.type) + " " + self.name
		if self.body is None: return s
		s += " = "
		s += asCCode(self.body)
		return s


def needWrapCTypeClass(t):
	if t is None: return False
	return t.__base__ is _ctypes._SimpleCData


def wrapCTypeClassIfNeeded(t):
	if needWrapCTypeClass(t):
		return wrapCTypeClass(t)
	else:
		return t


_wrapCTypeClassCache = {}


def wrapCTypeClass(t):
	if id(t) in _wrapCTypeClassCache: return _wrapCTypeClassCache[id(t)]

	class WrappedType(t): pass

	WrappedType.__name__ = "wrapCTypeClass_%s" % t.__name__
	_wrapCTypeClassCache[id(t)] = WrappedType
	return WrappedType


class CTypeConstructionException(Exception): pass


class RecursiveStructConstruction(CTypeConstructionException): pass


def _getCTypeStruct(baseClass, obj, stateStruct):
	def _construct(obj):
		fields = []
		for c in obj.body.contentlist:
			if not isinstance(c, CVarDecl): continue
			try:
				obj._construct_struct_attrib = c.type
				t = getCType(c.type, stateStruct)
			finally:
				obj._construct_struct_attrib = None
			if c.arrayargs:
				if len(c.arrayargs) != 1: raise Exception(str(c) + " has too many array args")
				n = c.arrayargs[0].value
				t = t * n
			elif stateStruct.IndirectSimpleCTypes:
				# See http://stackoverflow.com/questions/6800827/python-ctypes-structure-how-to-access-attributes-as-if-they-were-ctypes-and-not/6801253#6801253
				t = wrapCTypeClassIfNeeded(t)
			if hasattr(c, "bitsize"):
				fields += [(str(c.name), t, c.bitsize)]
			else:
				fields += [(str(c.name), t)]
		if obj._ctype_is_constructing:
			obj._ctype._fields_ = fields
			obj._ctype_is_constructing = False

	def construct(obj):
		try:
			stateStruct._construct_struct_type_stack += [obj]
			_construct(obj)
		finally:
			stateStruct._construct_struct_type_stack.pop()

	if getattr(obj, "_ctype_is_constructing", None):
		# If the parent referred to us as a pointer, it's fine,
		# we can return our incomplete type.
		if isPointerType(
				stateStruct._construct_struct_type_stack[-1]._construct_struct_attrib,
				alsoFuncPtr=True, alsoArray=False):
			return obj._ctype
		# Otherwise, try to construct it now.
		if obj._ctype_construct_need_now:
			raise RecursiveStructConstruction("Recursive construction of type %s" % obj)
		obj._ctype_construct_need_now = True
		construct(obj)
		return obj._ctype

	if hasattr(obj, "_ctype"): return obj._ctype
	if not hasattr(obj, "body"): raise CTypeConstructionException("%s must have the body attrib" % obj)
	if obj.body is None: raise CTypeConstructionException(
		"%s.body must not be None. maybe it was only forward-declarated?" % obj)

	class ctype(baseClass):
		pass

	ctype.__name__ = str(obj.name or "<anonymous-struct>")
	obj._ctype = ctype
	obj._ctype_is_constructing = True
	obj._ctype_construct_need_now = False
	construct(obj)
	return ctype


class CStruct(_CBaseWithOptBody):
	finalize = lambda *args, **kwargs: _finalizeBasicType(*args, dictName="structs", **kwargs)

	def getCType(self, stateStruct):
		return _getCTypeStruct(ctypes.Structure, self, stateStruct)

	def asCCode(self, indent=""):
		s = indent + "struct " + self.name
		if self.body is None: return s
		return s + "\n" + asCCode(self.body, indent)


class CUnion(_CBaseWithOptBody):
	finalize = lambda *args, **kwargs: _finalizeBasicType(*args, dictName="unions", **kwargs)

	def getCType(self, stateStruct):
		return _getCTypeStruct(ctypes.Union, self, stateStruct)

	def asCCode(self, indent=""):
		s = indent + "union " + self.name
		if self.body is None: return s
		return s + "\n" + asCCode(self.body, indent)


def minCIntTypeForNums(a, b=None, minBits=32, maxBits=64, useUnsignedTypes=True):
	if b is None: b = a
	bits = minBits
	while bits <= maxBits:
		if useUnsignedTypes and a >= 0 and b < (1 << bits):
			return "uint" + str(bits) + "_t"
		elif a >= -(1 << (bits - 1)) and b < (1 << (bits - 1)):
			return "int" + str(bits) + "_t"
		bits *= 2
	return None


class CEnum(_CBaseWithOptBody):
	finalize = lambda *args, **kwargs: _finalizeBasicType(*args, dictName="enums", **kwargs)

	def getNumRange(self):
		a, b = 0, 0
		for c in self.body.contentlist:
			assert isinstance(c, CEnumConst)
			if c.value < a: a = c.value
			if c.value > b: b = c.value
		return a, b

	def getMinCIntType(self):
		a, b = self.getNumRange()
		t = minCIntTypeForNums(a, b)
		return t

	def getEnumConst(self, value):
		for c in self.body.contentlist:
			if not isinstance(c, CEnumConst): continue
			if c.value == value: return c
		return None

	def getCType(self, stateStruct):
		t = self.getMinCIntType()
		if t is None:
			raise Exception(str(self) + " has a too high number range")
		t = stateStruct.StdIntTypes[t]
		return t

	# class EnumType(t):
	# 	_typeStruct = self
	# 	def __repr__(self):
	# 		v = self._typeStruct.getEnumConst(self.value)
	# 		if v is None: v = self.value
	# 		return "<EnumType " + str(v) + ">"
	# 	def __cmp__(self, other):
	# 		return cmp(self.value, other)
	# for c in self.body.contentlist:
	# 	if not c.name: continue
	# 	if hasattr(EnumType, c.name): continue
	# 	setattr(EnumType, c.name, c.value)
	# return EnumType
	def asCCode(self, indent=""):
		s = indent + "enum " + self.name
		if self.body is None: return s
		return s + "\n" + asCCode(self.body, indent)


class CEnumConst(_CBaseWithOptBody):
	def finalize(self, stateStruct, addToContent=None):
		if self._finalized:
			stateStruct.error("internal error: " + str(self) + " finalized twice")
			return

		if self.value is None:
			if self.parent.body.contentlist:
				last = self.parent.body.contentlist[-1]
				if isinstance(last.value, (str, unicode)):
					self.value = unichr(ord(last.value) + 1)
				else:
					self.value = last.value + 1
			else:
				self.value = 0

		_CBaseWithOptBody.finalize(self, stateStruct, addToContent)

		if self.name:
			# self.parent.parent is the parent of the enum
			self.parent.parent.body.enumconsts[self.name] = self

	def getConstValue(self, stateStruct):
		return self.value

	def asCCode(self, indent=""):
		return indent + self.name + " = " + str(self.value)


class CFuncArgDecl(_CBaseWithOptBody):
	AutoAddToContent = False

	def finalize(self, stateStruct, addToContent=False):
		if self._finalized:
			stateStruct.error("internal error: " + str(self) + " finalized twice")
			return

		if not self.type:
			self.type = make_type_from_typetokens(stateStruct, self, self._type_tokens)
		_CBaseWithOptBody.finalize(self, stateStruct, addToContent=False)

		if self.type != CBuiltinType(("void",)):
			self.parent.args += [self]

	def getCType(self, stateStruct):
		return getCType(self.type, stateStruct)

	def asCCode(self, indent=""):
		s = indent + asCCode(self.type)
		if self.name: s += " " + self.name
		return s

