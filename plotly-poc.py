#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flowinspector import flow

import matplotlib.pyplot as plt
from plotly.offline import plot
from plotly.tools import mpl_to_plotly


flw = flow('/home/alvar/testset3/testset3/test.pcap');

plt.rcParams['figure.figsize'] = (10, 7)

plt = flw.show(show=False)
plt.tight_layout()

fig = plt.gcf()
plotly_fig = mpl_to_plotly(fig)

plot(plotly_fig)
