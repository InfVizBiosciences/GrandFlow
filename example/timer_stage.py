#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from grandflow.util.timer import StageTimer

timer = StageTimer()
timer.start('timer1')

time.sleep(5)

print('timer1 stop : %s ' % timer.stop('timer1'))

timer.start('timer2')

time.sleep(3)

print('timer1 stop : %s ' % timer.stop('timer1'))
print('timer1 stop : %s ' % timer.stop('timer1'))
print('timer1 stop : %s ' % timer.stop('timer1'))
print('timer1 stop : %s ' % timer.stop('timer1'))
print('timer2 stop : %s ' % timer.stop('timer2'))

# timer.total() 有一个
print('Total time of timer1 and timer2: %s' % timer.total())
