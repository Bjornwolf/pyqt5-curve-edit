# -*- coding: utf-8 -*-


def L2Dist(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
            starting from the vertex with the lexicographically
            smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """

    # Sort the points lexicographically (tuples
    # are compared lexicographically).
    # Remove duplicates to detect the case we
    # have just one unique point.
    points = sorted(set(points))

    # Boring case: no points or a
    # single point, possibly repeated
    # multiple times.
    if len(points) <= 1:
        return points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Last point of each list is omitted because it is repeated
    # at the beginning of the other list
    return lower[:-1] + upper[:-1]


def deCasteljau(points, t):
    return deCasteljauRat(points, [1.0] * len(points), t)


def deCasteljauRat(points, weights, t):
    cpPoints = [points[i] for i in range(len(points))]
    t1 = 1.0 - t
    for k in range(1, len(cpPoints) + 1):
        for i in range(len(cpPoints) - k):
            u = t1 * weights[i]
            v = t * weights[i + 1]
            weights[i] = u + v
            u = u / weights[i]
            v = 1 - u
            cpPoints[i] = combine_pairs([u, v], [cpPoints[i], cpPoints[i + 1]])
    return cpPoints[0]


def combine_pairs(weights, points):
    result = (0.0, 0.0)
    for (i, (x, y)) in enumerate(points):
        result = (result[0] + weights[i] * x, result[1] + weights[i] * y)
    return result


def interpolateCurve(points):
    step = 1.0 / (len(points) - 1)
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    xsInterp = interpolate(step, xs, [0.001 * t for t in range(1001)])
    ysInterp = interpolate(step, ys, [0.001 * t for t in range(1001)])
    return [(xsInterp[i], ysInterp[i]) for i in range(1001)]


def interpolate(step, ys, points):
    N = len(ys)
    diffquot = ys
    print(ys)
    for n in range(2, N + 1):
        for k in range(N + 1 - n):
            print(N - k - 1)
            diffquot[N - 1 - k] = diffquot[N - 1 - k] - diffquot[N - k - 2]
            diffquot[N - 1 - k] /= ((n - 1) * step)

    result = []
    for pt in points:
        res = diffquot[-1]
        for i in range(2, N + 1):
            res = res * (pt - (N - i) * step) + diffquot[-i]
        result.append(res)
    return result
