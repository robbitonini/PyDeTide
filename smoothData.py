#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  SMOOTH.PY
  
  Python module developed on the basis of the MATLAB function SMOOTH, aiming to 
  smooth a time series. 
  
  The module implements both LOWESS and LOESS smooth data methods, together
  with their "robust" versions.

  Usage:
  
    > import smooth as sm
  
    > s = sm.smooth(t, ts, span, method)

  t:       incremental time steps
  ts:      sea leva data 
  span:    number of points or percentage of points used to calculate s
           

  methods: 'lowess'   - Lowess (linear fit)
           'loess'    - Loess (quadratic fit)
           'rlowess'  - Robust Lowess (linear fit)
           'rloess'   - Robust Loess (quadratic fit)
  

"""

import sys
import numpy as np


def lowess(x, y, span, method, robust, ite):
  """
  LOWESS  Smooth data using Lowess or Loess method.

  The difference between LOWESS and LOESS is that LOWESS uses a
  linear model to do the local fitting whereas LOESS uses a
  quadratic model to do the local fitting. Some other software
  may not have LOWESS, instead, they use LOESS with order 1 or 2 to
  represent these two smoothing methods.

  Reference: 
  [79] W.S.Cleveland, "Robust Locally Weighted Regression and Smoothing
       Scatterplots", _J. of the American Statistical Ass._, Vol 74, No. 368 
       (Dec.,1979), pp. 829-836.
       http://www.math.tau.ac.il/~yekutiel/MA%20seminar/Cleveland%201979.pdf
    
  """
  n = len(y)
  span = np.floor(span)
  span = min(span,n)
  c = np.copy(y)
  
  if (span == 1):
    return
  
  useLoess = False
  
  if (method == "loess"):
    useLoess = True

  diffx = np.diff(x)

  ynan = np.isnan(y)-0
  anyNans = int(np.any(ynan[:]))
  eps = np.spacing(1)
  seps = np.sqrt(eps)
  theDiffs = np.hstack((1, diffx, 1))

  if (robust):
    lbound = np.zeros((n,1))
    rbound = np.zeros((n,1))

  # Compute the non-robust smooth for non-uniform x
  for i in range(n):
    # if x(i) and x(i-1) are equal we just use the old value.
    if (theDiffs[i] == 0):
      c[i] = c[i-1]
      if (robust):
        lbound[i] = lbound[i-1]
        rbound[i] = rbound[i-1]
      continue

    # Find nearest neighbours
    idx = iKNearestNeighbours(span, i, x, 1-ynan)

    if (robust):
      # Need to store neighborhoods for robust loop
      lbound[i] = np.min(idx)
      rbound[i] = np.max(idx)
    
    if (len(idx) == 0):
      c[i] = np.NaN
      continue

    x1 = x[idx]-x[i] # center around current point to improve conditioning
    d1 = np.abs(x1)
    y1 = y[idx]

    weight = iTricubeWeights(d1)
    if (np.all(weight < seps)):
      weight[:] = 1    # if all weights are 0, just skip weighting

    ones = np.ones((len(x1),1))
    x1 = np.reshape(x1,(len(x1),1))
    v = np.hstack((ones, x1))
    weight = np.reshape(weight,(len(weight),1))

    if (useLoess):
      v = np.concatenate((v,x1*x1), axis=1) # There is no significant growth here
      
    ones = np.ones((1,np.shape(v)[1]), dtype=np.int)
    weight = np.hstack((weight,weight,weight))
    v = weight*v
    y1 = weight[:,0]*y1
    if (np.shape(v)[0] == np.shape(v)[1]):
      # Square v may give infs in the \ solution, so force least squares
      zeros = np.zeros((1,np.shape(v)[0]))
      v = np.vstack((v, zeros))
      y1 = np.hstack((y1,0))
      b = np.linalg.lstsq(v,y1)
    else:
      b = np.linalg.lstsq(v,y1)
    
    c[i] = b[0][0]
    
  
  # now that we have a non-robust fit, we can compute the residual and do
  # the robust fit if required
  maxabsyXeps = np.max(np.abs(y))*eps
  if (robust):
    for k in range(ite):
      r = y-c
      # Compute robust weights
      rweight = iBisquareWeights(r, maxabsyXeps)

      # Find new value for each point.
      for i in range(n):

        if (i>0 and x[i]==x[i-1]):
          c[i] = c[i-1]
          continue
        
        if np.isnan(c[i]): 
          continue 
        
        idx = range(lbound[i],rbound[i]+1)

         
        if (anyNans):
          ciao = np.nonzero(ynan[idx]==1)[0]
          idx[:] = [ item for i,item in enumerate(idx) if i not in ciao ]
        
        # check robust weights for removed points
        if np.any(rweight[idx] <= 0):
          tmprw = (rweight > 0)
          idx = iKNearestNeighbours(span, i, x, tmprw)

        x1 = x[idx] - x[i]
        d1 = np.abs(x1)
        y1 = y[idx]
        
        weight = iTricubeWeights(d1)
        if (np.all(weight < seps)):
          weight[:] = 1    # if all weights are 0, just skip weighting
    
        ones = np.ones((len(x1),1))
        x1 = np.reshape(x1,(len(x1),1))
        v = np.hstack((ones, x1))
        #print np.shape(v),np.shape(ones),np.shape(x1)

        if (useLoess):
          v = np.concatenate((v,x1*x1), axis=1) # There is no significant growth here
        
        
        # Modify the weights based on x values by multiplying them by
        # robust weights.
        weight = weight*rweight[idx]
        weight = np.reshape(weight, (len(weight),1))
        weight = np.hstack((weight,weight,weight))
        v = weight*v
        y1 = weight[:,0]*y1
        #print np.shape(v), np.shape(y1)
        if (np.shape(v)[0] == np.shape(v)[1]):
          # Square v may give infs in the \ solution, so force least squares
          zeros = np.zeros((1,np.shape(v)[0]))
          v = np.vstack((v, zeros))
          y1 = np.hstack((y1,0))
          b = np.linalg.lstsq(v,y1)
        else:
          b = np.linalg.lstsq(v,y1)
        
        c[i] = b[0][0]

  return c


def iBisquareWeights(r, myeps):
  """
  Bi-square (robust) weight function
  Convert residuals to weights using the bi-square weight function.
  NOTE that this function returns the square root of the weights
  """
  # Only use non-NaN residuals to compute median
  idx = np.isnan(r)
  idx1 = np.nonzero(idx==False)
  idx2 = np.nonzero(idx==True)
  # And bound the median away from zero
  s = np.max( np.array([1e8 * myeps, np.median(np.abs(r[idx1]))]) )
  # Covert the residuals to weights
  delta = iBisquare( r/(6*s) )
  # Everything with NaN residual should have zero weight
  delta[idx2] = 0
  return delta


def iBisquare(x):
  """
  This is this bi-square function defined at the top of the left hand
  column of page 831 in [C79]
  NOTE that this function returns the square root of the weights
  """
  b = np.zeros( np.shape(x) )
  idx = np.abs(x) < 1
  idx1 = np.nonzero(idx==True)
  b[idx1] = np.abs( 1 - x[idx1]**2 )
  return b


def iKNearestNeighbours(k, i, x, ini):
  """
  Find the k points from x(in) closest to x(i)
  """
    
  if (np.shape(np.nonzero(ini))[1] <= k):
    # If we have k points or fewer, then return them all
    idx = np.nonzero(ini)
  else:
    
    fanculo = np.nonzero(ini)
    # Find the distance to the k closest point
    d = np.abs(x-x[i])
    ds = np.sort(d[fanculo])
    dk = ds[k]
    # Find all points that are as close as or closer than the k closest point
    tmp = np.nonzero(d <= dk)

    close = np.zeros((len(x)))
    close[tmp[0]] = tmp[0]+1
    
    tmp1 = close * ini
    # The required indices are those points that are both close and "in"
    idx = np.nonzero(tmp1)[0]

  return idx


def iTricubeWeights(d):
  """
  Tri-cubic weight function
  Convert distances into weights using tri-cubic weight function.
  NOTE that this function returns the square-root of the weights.
 
  Protect against divide-by-zero. This can happen if more points than the span
  are coincident.
  """
  maxD = np.max(d)
  if (maxD > 0):
    d = d/np.max(d)

  w = (1-d**3)**(1.5)
  return w


def smooth(*kargs):
  """  
  SMOOTH  Smooth data.
  
  Note:
    'moving' and 'sgolay' methods have not been implemented

  """

  x = np.array(kargs[0])
  y = np.array(kargs[1])
  span = kargs[2]
  method = kargs[3]

  t = len(y)
  if (t == 0):
    c = y
    print("error:  {0}".format(t))
  elif (len(x) != t):
    print("error: x and y must be same length");
  
  # realize span
  if (span <= 0):
    print("error: span must be positive {0}".format(span))
  
  if (span < 1):
    span = np.ceil(span*t) # percent convention
  
  if (not span):
    span = 5   


  idx = range(0,t)

    
  sortx = np.any(np.diff(np.isnan(x)) < 0)   # if NaNs not all at end
  if (sortx or np.any(np.diff(x) < 0)):      # sort x
    x, idx = np.sort(x)
    y = y[idx]

  c = np.ones(len(y))*np.NaN
  ok = 1-np.isnan(x)

  if (method == 'moving'):
    c[ok] = moving(x[ok], y[ok], span)
    
  elif (method in ('lowess', 'loess', 'rlowess', 'rloess') ):
    robust = 0
    ite = 5
    if (method[0] == 'r'):
      robust = 1
      method = method[1:]
      
    c = lowess(x, y, span, method, robust, ite)

  elif (method == 'sgolay'):
    c[ok] = sgolay(x[ok], y[ok], span, degree)

  else:
    print("unrecognized method")
  
  c[idx] = c
  
  return c
  
