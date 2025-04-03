from matplotlib.patches import Patch

class DataPoint:

    def __init__(
        self,
        name: str,
        count: int,
        points: float,
        color: str,
        hatch: str,
        edge_color: str
    ):
        self.name = name
        self.count = count
        self.points = points
        self.color = color
        self.hatch = hatch
        self.edge_color = edge_color

    def __repr__(self):
        return str({"name": self.name, "count": self.count, "points": self.points})
    
    def get_values(self):
        return [self.count, self.points]

    def get_Patch(self):
        return Patch(
            facecolor=self.color,
            edgecolor=self.edge_color,
            label=self.name,
        ),