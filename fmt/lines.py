#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under the terms 
# of the GNU Affero General Public License.
#

#
# EXPERIMENTAL - Exploritory; Under construction.
#
# This module is experimental, exploratory, and under construction,
# and probably will remain so for quite some time. 
# 

from ..fmt import FormatBase


class Lines(FormatBase):
	"""
	Format line width and output.
	#
	# This module is experimental, exploratory, and under construction,
	# and probably will remain so for a long time.
	#
	# I strongly recommend NOT using it in any real application, as it
	# may change in extreme ways.
	#
	# It may disappear completely.
	#
	"""
	
	DefLength = 69
	
	DefFormats = {
		None : {
			'lines' : "{}"
		},
		"title" : {
			'lines'  : "# {}",
			'format' : "#\n{}\n#"
		},
		"about" : {
			'lines' : "# {}"
		},
		"item" : {
			"first"  : "{}",
			"lines"  : "   {}",
			"format" : " * {}"
		}
	}
	
	
	
	def __init__(self, **k):
		"""
		Pass `maxlen` and `formats` dict as keyword arguments that 
		specify the maximum width of text lines and a replacement for
		the Lines.DefFormats format dict.
		
		The `formats` dict defaults to (a copy of) self.DefFormats,
		which defines a dict containing "title", "about", and "item" 
		keys for the formatting of title text, about (descriptions)
		lines, and list "item" lines in the style of HTML lists.
		
		Add a "first" format to any format value (as "item" does) to
		use different processing for the first line.
		"""
		
		maxlen = k.get('maxlen')   # max line length (def: DefLength)
		formats = k.get("formats") # format dict     (def: DefFormats)
		fdefault = k.get("format") # default format  (def: None)
		
		# if no `formats` are given, copy the defaults
		formats = formats or {}
		if not formats:
			for key in self.DefFormats:
				formats[key] = self.DefFormats[key]
		
		# init superclass and store private vars
		FormatBase.__init__(self, maxlen, formats, **k)
		self.__formats = formats
		self.__maxlen  = maxlen or self.DefLength
		self.__format  = fdefault
		
		# runtime
		self.__flength = {}
	
	
	@property
	def maxlen(self):
		return self.__maxlen
	
	@property
	def formats(self):
		return self.__formats
	
	
	
	def format(self, text, **k):
		"""
		Pass `text` to be formatted. Pass alternate format as keyword
		`fmt` - default is the format passed to the constructor (or None
		if no format was given to the constructor. 
		
		Lines of text are generated (by the 'line' key) and then embedded
		in the format specified by the 'format' key of the format dict
		supplied to the constructor (else the self.DefFormat dict).
		"""
		
		# get format (as given by kwargs, or the default)
		fmt = k.get('format', k.get('ff', ''))
		
		# get array of lines in `text`, none longer than `self.maxlen`
		lines = self.lines(text)
		
		# Result - format each line and store results here
		rlines = []
		
		#
		# Get format strings and process lines.
		#  * Each `lines` line is first processed by the 'lines' key.
		#  * A 'format' key is optional, to be applied to the finished
		#    product of 'lines'.
		#
		
		#
		# 0) If there's a "first" item in self.formats, use that on the
		#    first line in lines.
		#
		if 'first' in self.formats.get(fmt, {}):
			first = lines[0]
			line = self.formatApply(fmt, 'first', " ".join(first))
			rlines.append(line)
			lines = lines[1:]
		
		# 1) Format each line with self.format['lines']
		for line in lines:
			if not line:
				linetext = ''
			else:
				linetext = ' '.join(line)
				
			# now line is a string - apply the format
			line = self.formatApply(fmt, 'lines', linetext)
			rlines.append(line)
		
		# 2) join the lines to a text string
		text = "\n".join(rlines)
		
		#
		# 3) Finally apply the enclosing 'format' to the text.
		#
		return self.formatApply(fmt, 'format', text)
		
		return text
	
	
	
	def formatApply(self, fmt, key, text, **k):
		"""Use the given format and key to format `text`"""
		fdict = self.__formats.get(fmt, {})
		fkey = fdict.get(key, "{}")
		return fkey.format(text)
	
	
	def formatLength(self, format_key):
		"""Return the widest line in `format_key` with no text."""
		try:
			return self.__flength[format_key]
		except KeyError:
			fblank = self.formatApply(format_key, "")
			flines = fblank.splitlines()
			fmax = 0
			for line in flines:
				flen = len(line)
				if flen > fmax:
					fmax = flen
			self.__flength[format_key] = flen
			return fmax
	
	
	def lines(self, text):
		"""
		Return a list of lines paginated lines within the maximum length.
		"""
		# split all words into a list and grab the first word
		words = text.strip().split()
		word1 = words[0]
		
		# current line and its word-count
		cline = [word1]     # current line
		chars = len(word1)  # current line char count
		
		# final result - all lines
		lines = []
		wordc = 1    
		
		# loop through remaining words
		for word in words[1:]:
			
			# get line-length after new word (plus the previous space)
			chars += len(word)+1
			
			# if line length won't exceed maxlen, append the next word
			if chars <= self.maxlen:
				cline.append(word)
				wordc += 1
			
			# if it would exceed maxlen...
			else:
				lines.append(cline)
				cline = [word]
				chars = len(word)
		
		# add the rest of the last sentence
		if cline and cline[0]:
			lines.append([])
			lines[-1].extend(cline)
		
		# return list of text lines
		return lines
	

