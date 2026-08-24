

def mean(data):
    '''
    Return the mean value of numeric data.

    Parameters
    ----------
    data : list of numeric type
        The data to compute the mean from.

    Return
    ------
    average : float
        The mean of the data or "nan" if the set is empty.

    Example
    -------
    >>> from mina.statistics import mean
    >>> mean([1, 3, 5])
    3.0
    >>> mean([1, 3, 5, 7.5])
    4.125
    '''
    n = len(data)
    if n >= 1:
        return(sum(data) / float(n))
    else:
        return(float("nan"))


def median(data):
    '''
    Return the median (middle value) of numeric data.

    When the number of data points is odd, return the middle data point.
    When the number of data points is even, the median is interpolated by
    taking the average of the two middle values:

    Parameters
    ----------
    data : list of numeric type
        The data to get the median from.

    Return
    ------
    average : int or float
        The median value of the data or 'nan' if the set is empty.

    Example
    -------
    >>> from mina.statistics import median
    >>> median([1, 3, 5])
    3
    >>> median([1, 3, 5, 7])
    4.0

    Notes
    -----
    This implementation is adapted from the statistics module of the CPython
    standard library implementation. It can be viewed on GitHub at https://githu
    b.com/python/cpython/blob/30afc91f5e70cf4748ffac77a419ba69ebca6f6a/Lib/stati
    stics.py#L364. Rather than raise a specific error on an empty set, it simply
    returns a "nan" float.
    '''
    data = sorted(data)
    n = len(data)
    if n == 0:
        return(float("nan"))
    if n % 2 == 1:
        return data[n // 2]
    else:
        i = n // 2
        return (data[i - 1] + data[i]) / 2.0


def stdev(data):
    '''
    Calculate the population standard deviation.

    Parameters
    ----------
    data : list of numeric type
        The data to compute the population standard deviation from.

    Return
    ------
    deviation : float
        The population standard deviation of the data or "nan" if the set is
        empty.

    Example
    -------
    >>> from mina.statistics import stdev
    >>> stdev([1, 3, 5])
    1.63299316186
    >>> stdev([1, 3, 5, 7.5])
    2.40767003553
    '''
    n = len(data)
    if n >= 1:
        average = mean(data)
        sse = sum([(x - average) ** 2.0 for x in data])
        return((sse / n ) ** 0.5)
    else:
        return(float("nan"))
        
## Quantiles ###############################################################

# There is no one perfect way to compute quantiles.  Here we offer
# two methods that serve common needs.  Most other packages
# surveyed offered at least one or both of these two, making them
# "standard" in the sense of "widely-adopted and reproducible".
# They are also easy to explain, easy to compute manually, and have
# straight-forward interpretations that aren't surprising.

# The default method is known as "R6", "PERCENTILE.EXC", or "expected
# value of rank order statistics". The alternative method is known as
# "R7", "PERCENTILE.INC", or "mode of rank order statistics".

# For sample data where there is a positive probability for values
# beyond the range of the data, the R6 exclusive method is a
# reasonable choice.  Consider a random sample of nine values from a
# population with a uniform distribution from 0.0 to 1.0.  The
# distribution of the third ranked sample point is described by
# betavariate(alpha=3, beta=7) which has mode=0.250, median=0.286, and
# mean=0.300.  Only the latter (which corresponds with R6) gives the
# desired cut point with 30% of the population falling below that
# value, making it comparable to a result from an inv_cdf() function.
# The R6 exclusive method is also idempotent.

# For describing population data where the end points are known to
# be included in the data, the R7 inclusive method is a reasonable
# choice.  Instead of the mean, it uses the mode of the beta
# distribution for the interior points.  Per Hyndman & Fan, "One nice
# property is that the vertices of Q7(p) divide the range into n - 1
# intervals, and exactly 100p% of the intervals lie to the left of
# Q7(p) and 100(1 - p)% of the intervals lie to the right of Q7(p)."

# If needed, other methods could be added.  However, for now, the
# position is that fewer options make for easier choices and that
# external packages can be used for anything more advanced.

def quantiles(data, n=4, method='exclusive'):
    """Divide *data* into *n* continuous intervals with equal probability.

    Returns a list of (n - 1) cut points separating the intervals.

    Set *n* to 4 for quartiles (the default).  Set *n* to 10 for deciles.
    Set *n* to 100 for percentiles which gives the 99 cuts points that
    separate *data* in to 100 equal sized groups.

    The *data* can be any iterable containing sample.
    The cut points are linearly interpolated between data points.

    If *method* is set to *inclusive*, *data* is treated as population
    data.  The minimum value is treated as the 0th percentile and the
    maximum value is treated as the 100th percentile.

    """
    if n < 1:
        return(float("nan"))

    data = sorted(data)

    ld = len(data)
    if ld < 2:
        if ld == 1:
            return(float("nan"))

    if method == 'inclusive':
        m = ld - 1
        result = []
        for i in range(1, n):
            j, delta = divmod(i * m, n)
            interpolated = (data[j] * (n - delta) + data[j + 1] * delta) / n
            result.append(interpolated)
        return result

    if method == 'exclusive':
        m = ld + 1
        result = []
        for i in range(1, n):
            j = i * m // n                               # rescale i to m/n
            j = 1 if j < 1 else ld-1 if j > ld-1 else j  # clamp to 1 .. ld-1
            delta = i*m - j*n                            # exact integer math
            interpolated = (data[j - 1] * (n - delta) + data[j] * delta) / n
            result.append(interpolated)
        return result
    else:
    	return(float("nan"))
