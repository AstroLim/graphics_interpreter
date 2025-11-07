"""
Graphics Engine for the Drawing Interpreter
Handles all drawing operations using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, Polygon, Arc, FancyBboxPatch
import numpy as np
from typing import List, Tuple, Optional
import math


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def angle_to(self, other: 'Point') -> float:
        return math.degrees(math.atan2(other.y - self.y, other.x - self.x))


class GraphicsEngine:
    def __init__(self, width: int = 800, height: int = 600, title: str = "Drawing Interpreter"):
        self.width = width
        self.height = height
        self.title = title
        
        # Pen state
        self.pen_position = Point(0, 0)
        self.pen_angle = 90  # Degrees, 0 = right, 90 = up
        self._pen_is_down = True
        self.pen_color = 'black'
        self.pen_width = 1.0
        self.fill_color = None
        self.filling = False
        
        # Drawing elements
        self.lines: List[Tuple[Point, Point, str, float]] = []  # (start, end, color, width)
        self.circles: List[Tuple[Point, float, str, float, Optional[str]]] = []  # (center, radius, color, width, fill)
        self.rectangles: List[Tuple[Point, float, float, str, float, Optional[str]]] = []  # (corner, width, height, color, width, fill)
        self.polygons: List[Tuple[List[Point], str, float, Optional[str]]] = []  # (points, color, width, fill)
        self.arcs: List[Tuple[Point, float, float, float, str, float]] = []  # (center, width, height, angle, color, width)
        
        # Current polygon being drawn
        self.current_polygon_points: List[Point] = []
        
        # Figure and axes
        self.fig = None
        self.ax = None
        self.setup_canvas()
    
    def setup_canvas(self):
        """Initialize the matplotlib figure and axes"""
        self.fig, self.ax = plt.subplots(figsize=(self.width/100, self.height/100))
        self.ax.set_xlim(-self.width/2, self.width/2)
        self.ax.set_ylim(-self.height/2, self.height/2)
        self.ax.set_aspect('equal')
        self.ax.set_title(self.title)
        self.ax.grid(True, alpha=0.3)
        self.ax.axhline(y=0, color='k', linewidth=0.5)
        self.ax.axvline(x=0, color='k', linewidth=0.5)
        plt.ion()  # Interactive mode
    
    def clear(self):
        """Clear all drawings"""
        self.lines.clear()
        self.circles.clear()
        self.rectangles.clear()
        self.polygons.clear()
        self.arcs.clear()
        self.current_polygon_points.clear()
        self.redraw()
    
    def reset(self):
        """Reset pen position and angle"""
        self.pen_position = Point(0, 0)
        self.pen_angle = 90
        self._pen_is_down = True
        self.pen_color = 'black'
        self.pen_width = 1.0
        self.fill_color = None
        self.filling = False
    
    def set_color(self, color: str):
        """Set pen color"""
        self.pen_color = color
        if self.filling:
            self.fill_color = color
    
    def set_width(self, width: float):
        """Set pen width"""
        self.pen_width = max(0.1, width)
    
    def set_fill(self, fill: bool):
        """Enable or disable filling"""
        self.filling = fill
        if fill and not self.fill_color:
            self.fill_color = self.pen_color
        elif not fill:
            self.fill_color = None
    
    def pen_up(self):
        """Lift the pen"""
        self._pen_is_down = False
    
    def pen_down(self):
        """Lower the pen"""
        self._pen_is_down = True
    
    def goto(self, x: float, y: float):
        """Move pen to absolute position"""
        if self._pen_is_down:
            self.lines.append((Point(self.pen_position.x, self.pen_position.y), 
                             Point(x, y), 
                             self.pen_color, 
                             self.pen_width))
        self.pen_position = Point(x, y)
    
    def forward(self, distance: float):
        """Move pen forward in current direction"""
        angle_rad = math.radians(self.pen_angle)
        new_x = self.pen_position.x + distance * math.cos(angle_rad)
        new_y = self.pen_position.y + distance * math.sin(angle_rad)
        self.goto(new_x, new_y)
    
    def backward(self, distance: float):
        """Move pen backward (opposite of current direction)"""
        self.forward(-distance)
    
    def turn_left(self, angle: float):
        """Turn pen left (counter-clockwise)"""
        self.pen_angle += angle
    
    def turn_right(self, angle: float):
        """Turn pen right (clockwise)"""
        self.pen_angle -= angle
    
    def set_angle(self, angle: float):
        """Set pen angle in degrees (0 = right, 90 = up)"""
        self.pen_angle = angle
    
    def get_position(self) -> Tuple[float, float]:
        """Get current pen position"""
        return (self.pen_position.x, self.pen_position.y)
    
    def get_angle(self) -> float:
        """Get current pen angle"""
        return self.pen_angle
    
    def draw_circle(self, radius: float, center_x: Optional[float] = None, 
                   center_y: Optional[float] = None):
        """Draw a circle"""
        if center_x is None:
            center_x = self.pen_position.x
        if center_y is None:
            center_y = self.pen_position.y
        
        center = Point(center_x, center_y)
        fill_color = self.fill_color if self.filling else None
        self.circles.append((center, radius, self.pen_color, self.pen_width, fill_color))
        
        if not self._pen_is_down:
            self.pen_position = center
    
    def draw_rectangle(self, width: float, height: float, 
                      corner_x: Optional[float] = None, 
                      corner_y: Optional[float] = None):
        """Draw a rectangle"""
        if corner_x is None:
            corner_x = self.pen_position.x
        if corner_y is None:
            corner_y = self.pen_position.y
        
        corner = Point(corner_x, corner_y)
        fill_color = self.fill_color if self.filling else None
        self.rectangles.append((corner, width, height, self.pen_color, self.pen_width, fill_color))
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float):
        """Draw a line between two points"""
        self.lines.append((Point(x1, y1), Point(x2, y2), self.pen_color, self.pen_width))
    
    def draw_polygon(self, points: List[Tuple[float, float]]):
        """Draw a polygon from a list of (x, y) points"""
        point_objects = [Point(x, y) for x, y in points]
        fill_color = self.fill_color if self.filling else None
        self.polygons.append((point_objects, self.pen_color, self.pen_width, fill_color))
    
    def draw_arc(self, width: float, height: float, angle: float = 0,
                center_x: Optional[float] = None, 
                center_y: Optional[float] = None):
        """Draw an arc (ellipse segment)"""
        if center_x is None:
            center_x = self.pen_position.x
        if center_y is None:
            center_y = self.pen_position.y
        
        center = Point(center_x, center_y)
        self.arcs.append((center, width, height, angle, self.pen_color, self.pen_width))
    
    def redraw(self):
        """Redraw all elements on the canvas"""
        if self.ax is None:
            return
        
        self.ax.clear()
        self.ax.set_xlim(-self.width/2, self.width/2)
        self.ax.set_ylim(-self.height/2, self.height/2)
        self.ax.set_aspect('equal')
        self.ax.set_title(self.title)
        self.ax.grid(True, alpha=0.3)
        self.ax.axhline(y=0, color='k', linewidth=0.5)
        self.ax.axvline(x=0, color='k', linewidth=0.5)
        
        # Draw lines
        for start, end, color, width in self.lines:
            self.ax.plot([start.x, end.x], [start.y, end.y], 
                        color=color, linewidth=width)
        
        # Draw circles
        for center, radius, color, width, fill in self.circles:
            circle = Circle((center.x, center.y), radius, 
                          edgecolor=color, linewidth=width, 
                          facecolor=fill if fill else 'none')
            self.ax.add_patch(circle)
        
        # Draw rectangles
        for corner, w, h, color, width, fill in self.rectangles:
            rect = Rectangle((corner.x, corner.y), w, h,
                           edgecolor=color, linewidth=width,
                           facecolor=fill if fill else 'none')
            self.ax.add_patch(rect)
        
        # Draw polygons
        for points, color, width, fill in self.polygons:
            if len(points) >= 3:
                polygon = Polygon([(p.x, p.y) for p in points],
                                edgecolor=color, linewidth=width,
                                facecolor=fill if fill else 'none')
                self.ax.add_patch(polygon)
        
        # Draw arcs
        for center, w, h, angle, color, width in self.arcs:
            arc = Arc((center.x, center.y), w, h, angle=angle,
                     theta1=0, theta2=180,  # Semi-circle by default
                     edgecolor=color, linewidth=width)
            self.ax.add_patch(arc)
        
        # Draw current pen position
        self.ax.plot(self.pen_position.x, self.pen_position.y, 
                    'ro', markersize=5, alpha=0.7)
        
        plt.draw()
        plt.pause(0.01)
    
    def show(self):
        """Display the canvas"""
        if self.fig:
            plt.show(block=False)
    
    def save(self, filename: str):
        """Save the drawing to a file"""
        if self.fig:
            self.fig.savefig(filename, dpi=100, bbox_inches='tight')
            print(f"Drawing saved to {filename}")

