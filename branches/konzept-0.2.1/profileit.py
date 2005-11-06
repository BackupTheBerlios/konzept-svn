#! /usr/bin/python

from paint4 import *
import profile
import pstats

profile.run('entryPoint()','paint4.prof')
p = pstats.Stats('paint4.prof')
p.strip_dirs()
p.sort_stats('cumulative')
# p.sort_stats('name')
p.print_stats()

