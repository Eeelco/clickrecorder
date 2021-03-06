# Code adapted from https://github.com/reptillicus/Bezier
import numpy as np
from scipy.special import comb

def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i



def bezier_curve(points, nTimes=1000):
    """
       Given a set of control points, return the
       bezier curve defined by the control points.
       points should be a list of lists, or list of tuples
       such as [ [1,1], 
                 [2,3], 
                 [4,5], ..[Xn, Yn] ]
        nTimes is the number of time steps, defaults to 1000
        See http://processingjs.nihongoresources.com/bezierinfo/
    """

    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return zip([round(x) for x in xvals[::-1][1:]], [round(y) for y in yvals[::-1][1:]])


def random_bezier(start_node, end_node, max_deviation,npoints):
    dist = (end_node - start_node)
    distnorm = np.linalg.norm(dist)

    perpendicular_vec = np.random.choice([-1,1]) * np.asarray([dist[1], -dist[0]])/distnorm

    mid_node = start_node + np.random.uniform(0.1,0.9) * dist + np.random.uniform(0, max_deviation * distnorm) * perpendicular_vec

    bez =  bezier_curve([start_node, mid_node, end_node],nTimes=npoints)
    # Remove duplicates
    dedup = []
    [dedup.append(x) for x in bez if x not in dedup]
    return dedup, len(dedup)
