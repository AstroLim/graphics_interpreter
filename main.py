"""
Main entry point for the Drawing Interpreter
Provides both REPL and script execution modes.
"""

import sys
import os
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from interpreter import Interpreter, InterpreterError
from graphics_engine import GraphicsEngine


class DrawingInterpreter:
    def __init__(self):
        self.graphics = GraphicsEngine(width=800, height=600, title="Drawing Interpreter")
        self.interpreter = Interpreter(self.graphics)
        self.graphics.show()
    
    def execute_code(self, code: str, show_output: bool = True) -> tuple[bool, str]:
        """
        Execute code and return (success, message)
        """
        try:
            # Tokenize
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # Parse
            parser = Parser(tokens)
            program = parser.parse()
            
            # Execute
            self.interpreter.interpret(program)
            
            if show_output:
                self.graphics.redraw()
            
            return True, "Execution successful"
        
        except LexerError as e:
            return False, f"Lexer Error: {e.message} (line {e.line}, column {e.column})"
        
        except ParserError as e:
            return False, f"Parser Error: {e.message} (line {e.line}, column {e.column})"
        
        except InterpreterError as e:
            return False, f"Runtime Error: {e.message} (line {e.line}, column {e.column})"
        
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return False, f"Unexpected Error: {str(e)}\n{tb}"
    
    def run_repl(self):
        """Run the Read-Eval-Print Loop"""
        print("=" * 60)
        print("Drawing Interpreter - Interactive Mode")
        print("=" * 60)
        print("Type 'help' for commands, 'exit' or 'quit' to exit")
        print("Multi-line input: end line with '\\' to continue")
        print("=" * 60)
        print()
        
        buffer = []
        
        while True:
            try:
                if buffer:
                    prompt = "... "
                else:
                    prompt = "draw> "
                
                line = input(prompt).strip()
                
                if not line:
                    continue
                
                # Handle special commands
                if line.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if line.lower() == 'help':
                    self.print_help()
                    continue
                
                if line.lower() == 'clear':
                    self.graphics.clear()
                    buffer = []
                    continue
                
                if line.lower() == 'reset':
                    self.graphics.reset()
                    buffer = []
                    continue
                
                # Check for line continuation
                if line.endswith('\\'):
                    buffer.append(line[:-1])
                    continue
                
                # Add line to buffer
                buffer.append(line)
                code = '\n'.join(buffer)
                buffer = []
                
                # Execute code
                success, message = self.execute_code(code)
                
                if not success:
                    print(f"Error: {message}")
                # Success messages are implicit (drawing appears)
            
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
                buffer = []
            
            except EOFError:
                print("\nGoodbye!")
                break
    
    def run_script(self, filename: str):
        """Run a script from a file"""
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print(f"Executing script: {filename}")
            success, message = self.execute_code(code, show_output=True)
            
            if success:
                print("Script executed successfully.")
                # Keep window open
                input("Press Enter to close...")
                return True
            else:
                print(f"Error: {message}")
                return False
        
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return False
    
    def print_help(self):
        """Print help information"""
        help_text = """
Drawing Interpreter Commands:

DRAWING COMMANDS:
  forward(distance) or fd(distance)    - Move forward
  backward(distance) or bk(distance)   - Move backward
  left(angle) or lt(angle)             - Turn left (counter-clockwise)
  right(angle) or rt(angle)            - Turn right (clockwise)
  penup() or pu()                      - Lift pen
  pendown() or pd()                    - Lower pen
  goto(x, y)                           - Move to absolute position
  circle(radius)                       - Draw circle at current position
  circle(radius, x, y)                 - Draw circle at (x, y)
  rectangle(width, height)             - Draw rectangle
  rectangle(width, height, x, y)       - Draw rectangle at (x, y)
  line(x1, y1, x2, y2)                 - Draw line between two points
  polygon(x1, y1, x2, y2, ...)        - Draw polygon
  arc(width, height, [angle])          - Draw arc
  color("colorname")                   - Set pen color
  fill()                               - Enable filling
  nofill()                             - Disable filling
  width(n)                             - Set pen width
  clear()                              - Clear canvas
  reset()                              - Reset pen position and settings
  position() or pos()                  - Get current position (returns tuple)

CONTROL FLOW:
  if condition { statements }          - Conditional execution
  if condition { statements } else { statements }
  while condition { statements }       - Loop while condition is true
  for var = start to end { statements }
  for var = start to end step n { statements }

VARIABLES:
  var name = value                     - Declare variable
  let name = value                     - Declare and assign variable
  name = value                         - Assign to variable

FUNCTIONS:
  function name(param1, param2) { statements }
  return value                         - Return from function

OPERATORS:
  +, -, *, /, %, ^                     - Arithmetic
  ==, !=, <, >, <=, >=                 - Comparison
  and, or, not                         - Logical

BUILT-IN FUNCTIONS:
  sin(x), cos(x), tan(x)               - Trigonometry (degrees)
  sqrt(x), abs(x)                      - Math functions
  min(a, b), max(a, b)                 - Min/Max
  random()                             - Random number [0, 1)
  pi(), e()                            - Constants

EXAMPLES:
  forward(100)
  right(90)
  forward(100)
  color("red")
  circle(50)
  fill()
  rectangle(100, 50)

  var x = 0
  while x < 360 {
    forward(2)
    right(1)
    x = x + 1
  }

  function square(size) {
    for i = 1 to 4 {
      forward(size)
      right(90)
    }
  }
  square(100)
        """
        print(help_text)


def main():
    """Main entry point"""
    interpreter = DrawingInterpreter()
    
    if len(sys.argv) > 1:
        # Script mode
        filename = sys.argv[1]
        interpreter.run_script(filename)
    else:
        # REPL mode
        interpreter.run_repl()


if __name__ == "__main__":
    main()

