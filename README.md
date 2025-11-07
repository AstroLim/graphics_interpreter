# Drawing Interpreter

A fully-featured, production-ready drawing interpreter system implemented in Python. This interpreter accepts user-defined commands, performs lexical analysis (tokenization), parses commands according to defined grammar rules, and executes them to create graphics. It includes comprehensive error handling, immediate output generation, and support for variables, functions, control flow, and complex drawing operations.

## Features

### Core Interpreter Components
- **Lexer (Tokenization)**: Complete lexical analysis with support for keywords, identifiers, numbers, strings, operators, and delimiters
- **Parser (AST Generation)**: Full parser that builds an Abstract Syntax Tree from tokens
- **Interpreter (Execution Engine)**: Executes AST nodes with proper scoping and error handling
- **Graphics Engine**: Matplotlib-based rendering engine for drawing operations

### Language Features
- **Variables**: Declare and assign variables with `var` or `let`
- **Control Flow**: `if/else`, `while` loops, `for` loops with step support
- **Functions**: User-defined functions with parameters and return values
- **Expressions**: Full expression evaluation with arithmetic, comparison, and logical operators
- **Built-in Functions**: Math functions (sin, cos, sqrt, etc.), constants (pi, e), and utilities

### Drawing Commands
- **Movement**: `forward()`, `backward()`, `left()`, `right()`, `goto()`
- **Pen Control**: `penup()`, `pendown()`, `color()`, `width()`, `fill()`, `nofill()`
- **Shapes**: `circle()`, `rectangle()`, `line()`, `polygon()`, `arc()`
- **Canvas**: `clear()`, `reset()`, `show()`

### Error Handling
- **Lexer Errors**: Detailed error messages with line and column numbers for invalid tokens
- **Parser Errors**: Clear syntax error messages with context
- **Runtime Errors**: Comprehensive runtime error handling (undefined variables, type errors, division by zero, etc.)
- **Graceful Degradation**: Interpreter never crashes; all errors are caught and reported

## Installation

### Requirements
- Python 3.7 or higher
- matplotlib
- numpy

### Setup
```bash
# Install dependencies
pip install matplotlib numpy
```

## Usage

### Interactive Mode (REPL)
Run the interpreter without arguments to start the interactive REPL:

```bash
python main.py
```

Example session:
```
draw> forward(100)
draw> right(90)
draw> forward(100)
draw> color("red")
draw> circle(50)
```

### Script Mode
Execute a script file:

```bash
python main.py examples/spiral.drw
```

### Multi-line Input
In REPL mode, end a line with `\` to continue on the next line:

```
draw> function square(size) { \
...     for i = 1 to 4 { \
...         forward(size) \
...         right(90) \
...     } \
... }
```

## Language Syntax

### Variables
```python
var x = 10
let y = 20
x = x + 5
```

### Control Flow
```python
# If statement
if x > 10 {
    color("red")
} else {
    color("blue")
}

# While loop
var i = 0
while i < 10 {
    forward(10)
    right(36)
    i = i + 1
}

# For loop
for i = 1 to 10 {
    forward(10)
    right(36)
}

# For loop with step
for i = 0 to 100 step 5 {
    circle(i / 10)
}
```

### Functions
```python
function square(size) {
    for i = 1 to 4 {
        forward(size)
        right(90)
    }
}

function add(a, b) {
    return a + b
}

square(100)
var result = add(5, 3)
```

### Drawing Commands
```python
# Basic movement
forward(100)
backward(50)
left(90)
right(45)
goto(0, 0)

# Pen control
penup()
pendown()
color("red")
width(3)
fill()
nofill()

# Shapes
circle(50)
circle(50, 100, 100)  # radius, x, y
rectangle(100, 50)
rectangle(100, 50, -50, -50)  # width, height, x, y
line(0, 0, 100, 100)
polygon(0, 0, 50, 0, 50, 50, 0, 50)  # x1, y1, x2, y2, ...
arc(100, 50, 45)  # width, height, angle

# Canvas
clear()
reset()
```

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`, `^` (power)
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical**: `and`, `or`, `not`

### Built-in Functions
- **Trigonometry**: `sin(x)`, `cos(x)`, `tan(x)`, `asin(x)`, `acos(x)`, `atan(x)` (angles in degrees)
- **Math**: `sqrt(x)`, `abs(x)`, `floor(x)`, `ceil(x)`, `round(x)`
- **Utilities**: `min(a, b)`, `max(a, b)`, `random()`
- **Constants**: `pi()`, `e()`

## Example Scripts

The `examples/` directory contains several example scripts:

- **spiral.drw**: Draws a spiral pattern
- **square_pattern.drw**: Creates a pattern of squares
- **circle_flower.drw**: Draws a flower using circles
- **star.drw**: Creates a 5-pointed star
- **geometric_shapes.drw**: Demonstrates various shapes
- **recursive_tree.drw**: Draws a recursive tree structure
- **mandelbrot_approximation.drw**: Creates a Mandelbrot-like pattern

## Architecture

### Module Structure
- **lexer.py**: Tokenization and lexical analysis
- **parser.py**: Parsing and AST generation
- **interpreter.py**: Execution engine and runtime
- **graphics_engine.py**: Graphics rendering using matplotlib
- **main.py**: REPL and CLI interface

### Error Handling Flow
1. **Lexer**: Catches invalid characters, unterminated strings, malformed numbers
2. **Parser**: Catches syntax errors, missing tokens, invalid expressions
3. **Interpreter**: Catches runtime errors (undefined variables, type errors, division by zero)

All errors include line and column numbers for easy debugging.

## Advanced Features

### Function Scope
Functions have their own variable scope and can access variables from their closure:

```python
var x = 10

function test() {
    var y = 20
    return x + y  # x from outer scope, y from function scope
}
```

### Recursion
The interpreter supports recursive function calls:

```python
function factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
```

### Complex Expressions
Full expression evaluation with operator precedence:

```python
var result = (a + b) * c - d / e ^ 2
var condition = x > 10 and y < 20 or z == 0
```

## Limitations

- No string concatenation with `+` operator (planned for future)
- No arrays/lists (planned for future)
- No file I/O operations (planned for future)
- Graphics window must remain open for drawings to persist

## Contributing

This is a complete, production-ready interpreter system. Future enhancements could include:
- String operations
- Array/list data structures
- File I/O
- Additional drawing primitives
- Animation support
- Export to image formats

## License

This project is provided as-is for educational and demonstration purposes.

## Author

Created as a comprehensive interpreter system demonstrating:
- Lexical analysis (tokenization)
- Parsing and AST generation
- Interpreter design and execution
- Error handling and recovery
- Graphics programming integration

