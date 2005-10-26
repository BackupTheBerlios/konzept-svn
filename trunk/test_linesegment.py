#!/usr/bin/python
# -*- coding: UTF-8 -*-

from numarray import *
from linesegment import *

# crossing lines
l1 = LineSegment(array([3,1]), array([3,5]))
l2 = LineSegment(array([1,1]), array([5,3]))
print l1.intersectionWithLineSegment(l2)

# non-crossing with regular cm
l1 = LineSegment(array([1,1]), array([2,6]))
l2 = LineSegment(array([2,1]), array([3,7]))
print l1.intersectionWithLineSegment(l2)

# non-crossing with singular cm
l1 = LineSegment(array([0,0]), array([4,4]))
l2 = LineSegment(array([2,0]), array([6,4]))
print l1.intersectionWithLineSegment(l2)
