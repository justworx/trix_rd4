
#
# PropertyValueAliases.txt
#  - PropertyValueAliases-8.0.0.txt
#  - Date: 2015-03-11, 22:29:33 GMT [MD]
#



#
# bc - Bidi_Class
#

BIDI = dict(
	AL  = "Arabic_Letter",
	AN  = "Arabic_Number",
	B   = "Paragraph_Separator",
	BN  = "Boundary_Neutral",
	CS  = "Common_Separator",
	EN  = "European_Number",
	ES  = "European_Separator",
	ET  = "European_Terminator",
	FSI = "First_Strong_Isolate",
	L   = "Left_To_Right",
	LRE = "Left_To_Right_Embedding",
	LRI = "Left_To_Right_Isolate",
	LRO = "Left_To_Right_Override",
	NSM = "Nonspacing_Mark",
	ON  = "Other_Neutral",
	PDF = "Pop_Directional_Format",
	PDI = "Pop_Directional_Isolate",
	R   = "Right_To_Left",
	RLE = "Right_To_Left_Embedding",
	RLI = "Right_To_Left_Isolate",
	RLO = "Right_To_Left_Override",
	S   = "Segment_Separator",
	WS  = "White_Space"
)



#
# gc - General_Category
#

CATEGORY = dict(
	C  = "Other",                # Cc | Cf | Cn | Co | Cs
	Cc = "Control",              #; cntrl #
	Cf = "Format",
	Cn = "Unassigned",
	Co = "Private_Use",
	Cs = "Surrogate", 
	L  = "Letter",               # Ll | Lm | Lo | Lt | Lu
	LC = "Cased_Letter",         # Ll | Lt | Lu
	Ll = "Lowercase_Letter",
	Lm = "Modifier_Letter",
	Lo = "Other_Letter",
	Lt = "Titlecase_Letter",
	Lu = "Uppercase_Letter",
	M  = "Mark",                 #; Combining_Mark  # Mc | Me | Mn
	Mc = "Spacing_Mark",
	Me = "Enclosing_Mark",
	Mn = "Nonspacing_Mark",
	N  = "Number",               # Nd | Nl | No #Nd = "Decimal_Number",       #; digit
	Nd = "Decimal_Number",       # digit
	Nl = "Letter_Number",
	No = "Other_Number",
	P  = "Punctuation",          # Pc | Pd | Pe | Pf | Pi | Po | Ps
	Pc = "Connector_Punctuation",
	Pd = "Dash_Punctuation",
	Pe = "Close_Punctuation",
	Pf = "Final_Punctuation",
	Pi = "Initial_Punctuation",
	Po = "Other_Punctuation",
	Ps = "Open_Punctuation",
	S  = "Symbol",                # Sc | Sk | Sm | So
	Sc = "Currency_Symbol",
	Sk = "Modifier_Symbol",
	Sm = "Math_Symbol",
	So = "Other_Symbol",
	Z  = "Separator",             # Zl | Zp | Zs
	Zl = "Line_Separator",
	Zp = "Paragraph_Separator",
	Zs = "Space_Separator"
)



# 
# lb - Line_Break
#

LINEBREAK = dict(
	AI = "Ambiguous",
	AL = "Alphabetic",
	B2 = "Break_Both",
	BA = "Break_After",
	BB = "Break_Before",
	BK = "Mandatory_Break",
	CB = "Contingent_Break",
	CJ = "Conditional_Japanese_Starter",
	CL = "Close_Punctuation",
	CM = "Combining_Mark",
	CP = "Close_Parenthesis",
	CR = "Carriage_Return",
	EX = "Exclamation",
	GL = "Glue",
	H2 = "H2",
	H3 = "H3",
	HL = "Hebrew_Letter",
	HY = "Hyphen",
	ID = "Ideographic",
	IN = "Inseparable",
	IS = "Infix_Numeric",
	JL = "JL",
	JT = "JT",
	JV = "JV",
	LF = "Line_Feed",
	NL = "Next_Line",
	NS = "Nonstarter",
	NU = "Numeric",
	OP = "Open_Punctuation",
	PO = "Postfix_Numeric",
	PR = "Prefix_Numeric",
	QU = "Quotation",
	RI = "Regional_Indicator",
	SA = "Complex_Context",
	SG = "Surrogate",
	SP = "Space",
	SY = "Break_Symbols",
	WJ = "Word_Joiner",
	XX = "Unknown",
	ZW = "ZWSpace"
)




class propalias(object):
	
	@classmethod
	def bidi(cls, x):
		return cls.find(x, BIDI)
	
	@classmethod
	def category(cls, x):
		return cls.find(x, CATEGORY)
	
	@classmethod
	def linebreak(cls, x):
		return cls.find(x, LINEBREAK)
	
	@classmethod
	def find(cls, x, VAR):
		
		if x:
			# if X is a key, return its value
			if (len(x)==2) and (x in VAR):
				return {x:VAR[x]}
			
			# otherwise, it's a search term for the value
			X = x.upper() # KEY
			for k in VAR:
				w = x.lower()       # word(s)
				v = VAR[k].lower()  # value
				z = v.split("_")    # split value
				if (w in v) or (w in v.split("_")):
					return {x:VAR.get(X)}
		
		# if both fail, return the search term and 
		return {x:''}
	
	#
	# abreviated (for use in params)
	#
	br = linebreak
	cat = category




