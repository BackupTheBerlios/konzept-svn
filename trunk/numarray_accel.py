#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" functions to accelerate the numeric calculations
    that should overload the numarray functions
"""

from numarray import *
import numarray.linear_algebra

def determinant(a):
	if shape(a) == (2,2):
		return a[0,0]*a[1,1] - a[0,1]*a[1,0]
	elif shape(a) == (3,3):
		return a[0,0]*(a[1,1]*a[2,2]-a[2,1]*a[1,2]) + \
		       a[1,0]*(a[2,1]*a[0,2]-a[0,1]*a[2,2]) + \
			   a[2,0]*(a[0,1]*a[1,2]+a[1,1]*a[0,2])
	return linear_algebra.determinant(a)

def inverse(a, d0 = None):
	if shape(a) == (2,2):
		_a = array(shape=shape(a), type=Float64)
		ai = array(shape=shape(a), type=Float64)
		_a[:] = a[:]
		if d0 == None: d0 = determinant(_a)
		ai[0,0] = _a[1,1]
		ai[0,1] = -_a[0,1]
		ai[1,0] = -_a[1,0]
		ai[1,1] = _a[0,0]
		return ai/d0

	elif shape(a) == (3,3):
		_a = array(shape=shape(a), type=Float64)
		ai = array(shape=shape(a), type=Float64)
		_a[:] = a[:]
		if d0 == None: d0 = determinant(_a)

		ai[0,0] = _a[1,1] * _a[2,2] - _a[2,1] * _a[1,2]
		ai[0,1] = _a[2,1] * _a[0,2] - _a[0,1] * _a[2,2]
		ai[0,2] = _a[0,1] * _a[1,2] - _a[1,1] * _a[0,2]

		ai[1,0] = _a[2,0] * _a[1,2] - _a[1,0] * _a[2,2]
		ai[1,1] = _a[0,0] * _a[2,2] - _a[2,0] * _a[0,2]
		ai[1,2] = _a[1,0] * _a[0,2] - _a[0,0] * _a[1,2]

		ai[2,0] = _a[1,0] * _a[2,1] - _a[2,0] * _a[1,1]
		ai[2,1] = _a[2,0] * _a[0,1] - _a[0,0] * _a[2,1]
		ai[2,2] = _a[0,0] * _a[1,1] - _a[1,0] * _a[0,1]

		return ai/d0

	return linear_algebra.inverse(a)
