# Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
```

## Running the Interpreter

### Interactive Mode (REPL)
```bash
python main.py
```

Then type commands:
```
draw> forward(100)
draw> right(90)
draw> forward(100)
draw> color("red")
draw> circle(50)
```

### Script Mode
```bash
python main.py examples/spiral.drw
```

## Basic Examples

### Draw a Square
```
function square(size) {
    for i = 1 to 4 {
        forward(size)
        right(90)
    }
}

square(100)
```

### Draw a Spiral
```
var angle = 0
var distance = 1

while angle < 720 {
    forward(distance)
    right(2)
    angle = angle + 2
    distance = distance + 0.1
}
```

### Draw a Circle Pattern
```
for i = 1 to 8 {
    penup()
    var x = 100 * cos(i * 45)
    var y = 100 * sin(i * 45)
    goto(x, y)
    pendown()
    circle(20)
}
```

## Common Commands

- `forward(distance)` - Move forward
- `backward(distance)` - Move backward  
- `left(angle)` - Turn left (degrees)
- `right(angle)` - Turn right (degrees)
- `goto(x, y)` - Move to position
- `penup()` - Lift pen
- `pendown()` - Lower pen
- `color("colorname")` - Set color
- `circle(radius)` - Draw circle
- `rectangle(width, height)` - Draw rectangle
- `clear()` - Clear canvas
- `reset()` - Reset position

## Getting Help

In REPL mode, type `help` for a full list of commands and syntax.

