############################################################################
#
# smooth.py
#
# Copyright 2005-6 Donour Sizemore (donour@cs.uchicago.edu)
#
# This file is part of pyXede.
#
# pyXede is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyXede is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyXede; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
############################################################################
#
# These are routines for smoothing X,Y coordindate data such as a dyno plot.
#
############################################################################



def NNA(data, iterations = 1, window = 15):
    """Smooth X,Y coordinate data using a nearest neighbors average. Simply
    put, points are moved up or down by averaging the values of the points in
    a window around them. Default number of iterations is 4 and windowsize is
    4. Data should be a list of [x,y] lists or tuples.
    
    """
    print window
    points = []
    for i in data:
        points.append([i[0], i[1]])
    
    for i in range(0, iterations):
        for j in range(window, len(points) - window):
            for k in range(1, window):
                points[j][1] = points[j][1] + points[j-k][1]
                points[j][1] = points[j][1] + points[j+k][1]
            points[j][1] = points[j][1] / (2.0 * (window-1)  + 1.0)
    return points
                

def box(data, iterations = 10):
    """Smooth X,Y coordinate data using the Sizemore 'Box' method :).
    Default number of iterations is 10, but more (or less) can be specified.
    Data should be a list of (x,y) tuples.
    """

    points = []
    for i in data:
        points.append([i[0], i[1]])
    
    for i in range(0, iterations):
        for j in range(0, len(points)-4):
            a = points[j]
            b = points[j+1]
            c = points[j+2]
            d = points[j+3]

            points[j][0] = (a[0] + d[0]) / 2.0
            points[j][1] = (a[1] + b[1] + c[1] + d[1]) / 4.0

    for i in range(0, iterations):
        for j in range(3, len(points)):
            a = points[j]
            b = points[j-1]
            c = points[j-2]
            d = points[j-3]

            points[j][0] = (a[0] + d[0]) / 2.0
            points[j][1] = (a[1] + b[1] + c[1] + d[1]) / 4.0

    return points

def RunningAverage(data, window = 10):
    """Smooth X,Y coordinate data by keeping a simple running average of the
       last window number of points. This i roughly equivalent to doing NNA,
       but looking only to the left.
    """
    points = []
    for i in data:
        points.append([i[0], i[1]])

    for i in range(0, len(points)+1 - window):
        # average the points in points[i:i+window][1]
        w = points[(i):(i+window)]
        values = map(lambda x: x[1], w)
        value = sum(values) / window
        points[i-1+window][1] = value

    return points

def SavGol(data, window = 64, moments = 0):
    """Smooth X,Y coodinate data using Savitzky-Golay algorithm
    """
    import savgol
    values = map(lambda x: x[1], data)
    values = savgol.smooth(values, window, moments)
    points = []
    for i in range(0, len(data)):
        points.append( (data[i][0], values[i]) )
    return points

if __name__ == "__main__":
    import random, math
    points = []
    real   = []
    for i in range(1,1000):
        p = (math.sin(i/float(50)) * 200+i) 
        real.append( (i, p) )
        points.append( (i, p + (random.random()-0.5)*400 ) )

    import gnuplot, time
    one   = NNA(points)
    gnuplot.plot([points, real, one],
                 terminal = "x11",
                 labels = ["Raw Data", "Real Curve", "Fit Curve"],
                 output = "1.png");time.sleep(3)
    two   = box(points)
    gnuplot.plot([points, real, two],
                 terminal = "x11",
                 labels = ["Raw Data", "Real Curve", "Fit Curve"],
                 output = "2.png");time.sleep(3)
    three = RunningAverage(points)
    gnuplot.plot([points,real, three],
                 terminal = "x11",
                 labels = ["Raw Data", "Real Curve", "Fit Curve"],
                 output = "3.png");time.sleep(3)
    four = SavGol(points)
    gnuplot.plot([points,real, four],
                 terminal = "x11",
                 labels = ["Raw Data", "Real Curve", "Fit Curve"],
                 output = "4.png");time.sleep(3)

