from utils import (deCasteljau, deCasteljauRat, convex_hull)
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF


class Curve:
    def __init__(self, points=[], ctype='bezier'):
        self.points = points
        self.points_no = len(points)
        self.ctype = ctype
        self.is_changed = True
        self.is_hull = False
        self.is_guide = False
        self.plot = None
        self.hull = None
        self.guide = None

    def add_point(self, x, y, z=0):
        self.points.append((x, y))
        self.points_no += 1
        self.is_changed = True

    def move_point_to(self, i, x=None, y=None):
        (old_x, old_y) = self.points[i]
        self.points[i] = (x if x is not None else old_x,
                          y if y is not None else old_y)
        self.is_changed = True

    def move_point_by(self, i, dx, dy):
        (x, y) = self.points[i]
        self.points[i] = (x + dx, y + dy)
        self.is_changed = True

    def make_plot(self):
        if self.is_changed:
            if self.is_hull:
                self.make_hull()
            if self.is_guide:
                self.make_guide()
            plot_size = 100. + 10. * self.points_no
            if self.ctype == 'bezier' and self.points_no > 0:
                points = [deCasteljau(self.points, t / plot_size)
                          for t in range(int(plot_size + 1))]
            elif self.ctype == 'rbezier' and self.points_no > 0:
                points = [deCasteljauRat(self.points, self.weights,
                                         t / plot_size)
                          for t in range(int(plot_size + 1))]
            else:
                points = []
            self.plot = QPolygonF()
            for (x, y) in points:
                self.plot.append(QPointF(x + 5, y + 5))
        self.is_changed = False

    def make_hull(self):
        conv = convex_hull(self.points)
        self.hull = QPolygonF()
        for (x, y) in conv:
            self.hull.append(QPointF(x + 5, y + 5))

    def make_guide(self):
        self.guide = QPolygonF()
        for (x, y) in self.points:
            self.guide.append(QPointF(x + 5, y + 5))

    def toggle_hull(self, is_hull):
        self.is_hull = is_hull
        self.is_changed = True

    def toggle_guide(self, is_guide):
        self.is_guide = is_guide
        self.is_changed = True
