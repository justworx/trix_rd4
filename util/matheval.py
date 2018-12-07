#
# Copyright 2018 justworx
# This file is part of the trix project, distributed under
# the terms of the GNU Affero General Public License.
#

from .. import *
import ast, math, operator


#
# EVAL
#
def matheval(expr, vvars={}, fn={}):
	"""
	Evaluate a math expression given as string `expr`.
	
	Optional args `vvars` and `fn` may be given as dicts - the former
	containing variables as key-value pairs, the later being executable
	objects as key-value pairs.
	"""
	 
	r = __eval(ast.parse(expr, mode='eval'), vvars, fn)
	return r
	try:
		if r == int(r):
			return int(r)
	except Exception:
		pass
	return r



# unwanted functions from math module
MATH_FN_BAD = ['fsum']



# relevant builtin functions
MATH_FN_GOOD = {
	'abs' : abs
}


# variables from math module
MATH_NAMES = {
	'e' : math.e,
	'pi' : math.pi
}


# unary operators
MATH_UOPS = {
	ast.USub: operator.neg,
	ast.UAdd: operator.pos
}


# binary operators
BOPS = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Pow: operator.pow,
	ast.Mod: operator.mod
}

try:
	BOPS[ast.Div] = operator.div #py2
except AttributeError:
	BOPS[ast.Div] = operator.truediv #py3



#
# EVAL NODE
#
def __eval(node, vars, fn):
	
	if isinstance(node, ast.Expression):
		return __eval(node.body, vars, fn)
	
	# NUMBER
	elif isinstance(node, ast.Num):
		return float(node.n)
	
	# BINARY OP:
	elif isinstance(node, ast.BinOp):
		op_type = type(node.op)
		if op_type in BOPS:
			return BOPS[op_type](
				__eval(node.left, vars, fn),
				__eval(node.right, vars, fn)
			)
		else:
			raise ValueError("matheval-invalid-binary-op", xdata(
					op=type(node.op).__name__
				))
	
	# UNARY OP:
	elif isinstance(node, ast.UnaryOp):
		op_type = type(node.op)
		if op_type in MATH_UOPS:
			return MATH_UOPS[op_type](__eval(node.operand, vars, fn))
		else:
			raise ValueError("matheval-invalid-unary-op", xdata(
					op=type(node.op).__name__
				))
	
	#
	# VARIABLES:
	# - Names of vars argument variables, or the e and pi from math 
	#   module.
	#
	elif isinstance(node, ast.Name):
		if node.id in vars:
			return vars[node.id]
		elif node.id in MATH_NAMES:
			return MATH_NAMES[node.id]
		else:
			raise ValueError("matheval-invalid-variable", xdata(
					var=str(node.id)
				))
	
	#
	# STRING:
	# - This is intended to support arguments to functions that will 
	#   eventually return a number. It has the affect of allowing string
	#   operations, but I don't know of any reason to prevent that, so 
	#   I'll leave it here.
	#
	elif isinstance(node, ast.Str):
		return node.s
	
	#
	# FUNCTIONS:
	# - Handle the functions described in the math module and relevant
	#   builtin functions.
	#
	elif isinstance(node, ast.Call):
		if not isinstance(node.func, ast.Name):
			raise ValueError("matheval-unknown-function", xdata(
					name=str(ast.Name), require=str(node.func)
				))
		
		if node.func.id == MATH_FN_GOOD:
			func = MATH_FN_GOOD[node.func.id]
		elif node.func.id in fn:
			func = fn[node.func.id]
		elif not node.func.id in MATH_FN_BAD:
			func = getattr(math, node.func.id, None)
		if func is None:
			raise ValueError("matheval-invalid-function", xdata(
					name=node.func.id, value=None
				))
		
		if node.args is not None:
			args = [__eval(v, vars, fn) for v in node.args]
		else:
			args = []
		return func(*args)
	
	else:
		raise ValueError("matheval-invalid-node-type", xdata(
			nodetype=type(node).__name__
		))




