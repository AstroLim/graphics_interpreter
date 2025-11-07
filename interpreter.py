"""
Interpreter for the Drawing Interpreter
Executes the AST and handles all runtime operations.
"""

from typing import Dict, List, Optional, Any, Callable
from parser import *
from graphics_engine import GraphicsEngine
import math


class InterpreterError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"RuntimeError at line {line}, column {column}: {message}")


class Function:
    def __init__(self, name: str, params: List[str], body: List[Statement], 
                 closure: Dict[str, Any]):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure.copy()
    
    def __repr__(self):
        return f"Function({self.name}, {len(self.params)} params)"


class Interpreter:
    def __init__(self, graphics: GraphicsEngine):
        self.graphics = graphics
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Function] = {}
        self.return_value = None
        self.return_flag = False
        
        # Built-in functions
        self.setup_builtins()
    
    def setup_builtins(self):
        """Register built-in functions"""
        builtins = {
            'sin': lambda x: math.sin(math.radians(x)),
            'cos': lambda x: math.cos(math.radians(x)),
            'tan': lambda x: math.tan(math.radians(x)),
            'asin': lambda x: math.degrees(math.asin(x)),
            'acos': lambda x: math.degrees(math.acos(x)),
            'atan': lambda x: math.degrees(math.atan(x)),
            'sqrt': lambda x: math.sqrt(x),
            'abs': lambda x: abs(x),
            'floor': lambda x: math.floor(x),
            'ceil': lambda x: math.ceil(x),
            'round': lambda x: round(x),
            'min': lambda a, b: min(a, b),
            'max': lambda a, b: max(a, b),
            'random': lambda: __import__('random').random(),
            'pi': lambda: math.pi,
            'e': lambda: math.e,
        }
        
        for name, func in builtins.items():
            self.functions[name] = Function(name, [], [], {})
            self.functions[name].builtin = func
    
    def interpret(self, program: Program):
        """Interpret a program"""
        try:
            for statement in program.statements:
                self.execute_statement(statement)
                if self.return_flag:
                    break
            self.graphics.redraw()
        except InterpreterError as e:
            raise e
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            raise InterpreterError(f"Unexpected error: {str(e)}\n{tb}", 0, 0)
    
    def execute_statement(self, stmt: Statement):
        """Execute a statement"""
        if isinstance(stmt, VariableDeclaration):
            self.execute_variable_declaration(stmt)
        elif isinstance(stmt, Assignment):
            self.execute_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self.execute_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.execute_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self.execute_for_statement(stmt)
        elif isinstance(stmt, FunctionDefinition):
            self.execute_function_definition(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.execute_return_statement(stmt)
        elif isinstance(stmt, FunctionCall):
            self.execute_function_call(stmt)
        else:
            raise InterpreterError(f"Unknown statement type: {type(stmt)}", 
                                 stmt.line if hasattr(stmt, 'line') else 0, 0)
    
    def execute_variable_declaration(self, stmt: VariableDeclaration):
        """Execute variable declaration"""
        var_name = stmt.identifier.name
        if stmt.value:
            value = self.evaluate_expression(stmt.value)
            self.variables[var_name] = value
        else:
            self.variables[var_name] = None
    
    def execute_assignment(self, stmt: Assignment):
        """Execute assignment"""
        var_name = stmt.identifier.name
        value = self.evaluate_expression(stmt.value)
        self.variables[var_name] = value
    
    def execute_if_statement(self, stmt: IfStatement):
        """Execute if statement"""
        condition = self.evaluate_expression(stmt.condition)
        if self.is_truthy(condition):
            for s in stmt.then_block:
                self.execute_statement(s)
                if self.return_flag:
                    return
        elif stmt.else_block:
            for s in stmt.else_block:
                self.execute_statement(s)
                if self.return_flag:
                    return
    
    def execute_while_statement(self, stmt: WhileStatement):
        """Execute while statement"""
        while self.is_truthy(self.evaluate_expression(stmt.condition)):
            for s in stmt.body:
                self.execute_statement(s)
                if self.return_flag:
                    return
    
    def execute_for_statement(self, stmt: ForStatement):
        """Execute for statement"""
        var_name = stmt.var.name
        start = self.evaluate_expression(stmt.start)
        end = self.evaluate_expression(stmt.end)
        step = self.evaluate_expression(stmt.step) if stmt.step else 1.0
        
        # Save original value if variable exists
        original_value = self.variables.get(var_name)
        
        current = start
        if step > 0:
            while current <= end:
                self.variables[var_name] = current
                for s in stmt.body:
                    self.execute_statement(s)
                    if self.return_flag:
                        if original_value is not None:
                            self.variables[var_name] = original_value
                        else:
                            del self.variables[var_name]
                        return
                current += step
        else:
            while current >= end:
                self.variables[var_name] = current
                for s in stmt.body:
                    self.execute_statement(s)
                    if self.return_flag:
                        if original_value is not None:
                            self.variables[var_name] = original_value
                        else:
                            del self.variables[var_name]
                        return
                current += step
        
        # Restore original value
        if original_value is not None:
            self.variables[var_name] = original_value
        elif var_name in self.variables:
            del self.variables[var_name]
    
    def execute_function_definition(self, stmt: FunctionDefinition):
        """Execute function definition"""
        func_name = stmt.name.name
        param_names = [p.name for p in stmt.params]
        self.functions[func_name] = Function(func_name, param_names, stmt.body, self.variables)
    
    def execute_return_statement(self, stmt: ReturnStatement):
        """Execute return statement"""
        if stmt.value:
            self.return_value = self.evaluate_expression(stmt.value)
        else:
            self.return_value = None
        self.return_flag = True
    
    def execute_function_call(self, call: FunctionCall):
        """Execute function call"""
        func_name = call.name.name
        
        # Check if it's a drawing command first (they take precedence)
        if func_name in self.drawing_commands:
            return self.execute_drawing_command(func_name, call.args)
        
        # Check if it's a built-in function
        if func_name in self.functions:
            func_obj = self.functions[func_name]
            if hasattr(func_obj, 'builtin') and callable(func_obj.builtin):
                builtin_func = func_obj.builtin
                args = [self.evaluate_expression(arg) for arg in call.args]
                try:
                    result = builtin_func(*args)
                    return result
                except TypeError as e:
                    raise InterpreterError(f"Error calling built-in function {func_name}: {str(e)}", 
                                         call.line, call.column)
                except Exception as e:
                    raise InterpreterError(f"Error in built-in function {func_name}: {str(e)}", 
                                         call.line, call.column)
        
        # Check if it's a user-defined function
        if func_name not in self.functions:
            raise InterpreterError(f"Undefined function: {func_name}", 
                                 call.line, call.column)
        
        func = self.functions[func_name]
        
        # Check if it's actually a Function object (not a built-in that was overwritten)
        if not isinstance(func, Function):
            raise InterpreterError(f"{func_name} is not a callable function (got {type(func).__name__})", 
                                 call.line, call.column)
        
        if len(call.args) != len(func.params):
            raise InterpreterError(f"Function {func_name} expects {len(func.params)} arguments, got {len(call.args)}", 
                                 call.line, call.column)
        
        # Save current state
        old_variables = self.variables.copy()
        old_return_flag = self.return_flag
        old_return_value = self.return_value
        
        # Evaluate arguments in current (outer) scope BEFORE changing variables
        arg_values = [self.evaluate_expression(arg_expr) for arg_expr in call.args]
        
        # Set up function scope
        self.variables = func.closure.copy()
        for param_name, arg_value in zip(func.params, arg_values):
            self.variables[param_name] = arg_value
        
        self.return_flag = False
        self.return_value = None
        
        # Execute function body
        for stmt in func.body:
            self.execute_statement(stmt)
            if self.return_flag:
                break
        
        # Get return value
        result = self.return_value
        
        # Restore state
        self.variables = old_variables
        self.return_flag = old_return_flag
        self.return_value = old_return_value
        
        return result
    
    def execute_drawing_command(self, command: str, args: List[Expression]):
        """Execute a drawing command"""
        arg_values = [self.evaluate_expression(arg) for arg in args]
        
        if command in ['forward', 'fd']:
            if len(arg_values) != 1:
                raise InterpreterError(f"{command} expects 1 argument", 0, 0)
            self.graphics.forward(arg_values[0])
            self.graphics.redraw()
        
        elif command in ['backward', 'bk']:
            if len(arg_values) != 1:
                raise InterpreterError(f"{command} expects 1 argument", 0, 0)
            self.graphics.backward(arg_values[0])
            self.graphics.redraw()
        
        elif command in ['left', 'lt']:
            if len(arg_values) != 1:
                raise InterpreterError(f"{command} expects 1 argument", 0, 0)
            self.graphics.turn_left(arg_values[0])
        
        elif command in ['right', 'rt']:
            if len(arg_values) != 1:
                raise InterpreterError(f"{command} expects 1 argument", 0, 0)
            self.graphics.turn_right(arg_values[0])
        
        elif command in ['penup', 'pu']:
            self.graphics.pen_up()
        
        elif command in ['pendown', 'pd']:
            self.graphics.pen_down()
        
        elif command == 'circle':
            if len(arg_values) == 1:
                self.graphics.draw_circle(arg_values[0])
            elif len(arg_values) == 3:
                self.graphics.draw_circle(arg_values[0], arg_values[1], arg_values[2])
            else:
                raise InterpreterError("circle expects 1 or 3 arguments", 0, 0)
            self.graphics.redraw()
        
        elif command in ['rectangle', 'rect']:
            if len(arg_values) == 2:
                self.graphics.draw_rectangle(arg_values[0], arg_values[1])
            elif len(arg_values) == 4:
                self.graphics.draw_rectangle(arg_values[0], arg_values[1], 
                                            arg_values[2], arg_values[3])
            else:
                raise InterpreterError("rectangle expects 2 or 4 arguments", 0, 0)
            self.graphics.redraw()
        
        elif command == 'line':
            if len(arg_values) != 4:
                raise InterpreterError("line expects 4 arguments (x1, y1, x2, y2)", 0, 0)
            self.graphics.draw_line(arg_values[0], arg_values[1], 
                                   arg_values[2], arg_values[3])
            self.graphics.redraw()
        
        elif command == 'polygon':
            if len(arg_values) < 6 or len(arg_values) % 2 != 0:
                raise InterpreterError("polygon expects an even number of arguments (pairs of x, y)", 0, 0)
            points = [(arg_values[i], arg_values[i+1]) for i in range(0, len(arg_values), 2)]
            self.graphics.draw_polygon(points)
            self.graphics.redraw()
        
        elif command == 'arc':
            if len(arg_values) == 2:
                self.graphics.draw_arc(arg_values[0], arg_values[1])
            elif len(arg_values) == 3:
                self.graphics.draw_arc(arg_values[0], arg_values[1], arg_values[2])
            elif len(arg_values) == 5:
                self.graphics.draw_arc(arg_values[0], arg_values[1], arg_values[2],
                                      arg_values[3], arg_values[4])
            else:
                raise InterpreterError("arc expects 2, 3, or 5 arguments", 0, 0)
            self.graphics.redraw()
        
        elif command == 'clear':
            self.graphics.clear()
        
        elif command == 'reset':
            self.graphics.reset()
            self.graphics.redraw()
        
        elif command == 'color':
            if len(arg_values) != 1:
                raise InterpreterError("color expects 1 argument", 0, 0)
            color = str(arg_values[0])
            self.graphics.set_color(color)
        
        elif command == 'fill':
            self.graphics.set_fill(True)
        
        elif command == 'nofill':
            self.graphics.set_fill(False)
        
        elif command == 'width':
            if len(arg_values) != 1:
                raise InterpreterError("width expects 1 argument", 0, 0)
            self.graphics.set_width(arg_values[0])
        
        elif command == 'goto':
            if len(arg_values) != 2:
                raise InterpreterError("goto expects 2 arguments (x, y)", 0, 0)
            self.graphics.goto(arg_values[0], arg_values[1])
            self.graphics.redraw()
        
        elif command in ['position', 'pos']:
            return self.graphics.get_position()
        
        elif command == 'show':
            self.graphics.show()
        
        elif command == 'hide':
            pass  # Not implemented in matplotlib
        
        return None
    
    drawing_commands = {
        'forward', 'fd', 'backward', 'bk', 'left', 'lt', 'right', 'rt',
        'penup', 'pu', 'pendown', 'pd', 'circle', 'rectangle', 'rect',
        'line', 'polygon', 'arc', 'clear', 'reset', 'color', 'fill',
        'nofill', 'width', 'goto', 'position', 'pos', 'show', 'hide'
    }
    
    def evaluate_expression(self, expr: Expression) -> Any:
        """Evaluate an expression"""
        if isinstance(expr, NumberLiteral):
            return expr.value
        
        if isinstance(expr, StringLiteral):
            return expr.value
        
        if isinstance(expr, BooleanLiteral):
            return expr.value
        
        if isinstance(expr, Identifier):
            if expr.name not in self.variables:
                raise InterpreterError(f"Undefined variable: {expr.name}", 
                                     expr.line, expr.column)
            return self.variables[expr.name]
        
        if isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr)
        
        if isinstance(expr, UnaryOp):
            return self.evaluate_unary_op(expr)
        
        if isinstance(expr, FunctionCall):
            return self.execute_function_call(expr)
        
        raise InterpreterError(f"Unknown expression type: {type(expr)}", 
                             expr.line if hasattr(expr, 'line') else 0, 0)
    
    def evaluate_binary_op(self, expr: BinaryOp) -> Any:
        """Evaluate binary operation"""
        left = self.evaluate_expression(expr.left)
        right = self.evaluate_expression(expr.right)
        
        op_type = expr.op.type
        
        if op_type == TokenType.PLUS:
            return left + right
        elif op_type == TokenType.MINUS:
            return left - right
        elif op_type == TokenType.MULTIPLY:
            return left * right
        elif op_type == TokenType.DIVIDE:
            if right == 0:
                raise InterpreterError("Division by zero", expr.line, expr.column)
            return left / right
        elif op_type == TokenType.MODULO:
            if right == 0:
                raise InterpreterError("Modulo by zero", expr.line, expr.column)
            return left % right
        elif op_type == TokenType.POWER:
            return left ** right
        elif op_type == TokenType.EQUALS:
            return left == right
        elif op_type == TokenType.NOT_EQUALS:
            return left != right
        elif op_type == TokenType.LESS_THAN:
            return left < right
        elif op_type == TokenType.GREATER_THAN:
            return left > right
        elif op_type == TokenType.LESS_EQUAL:
            return left <= right
        elif op_type == TokenType.GREATER_EQUAL:
            return left >= right
        elif op_type == TokenType.AND:
            return self.is_truthy(left) and self.is_truthy(right)
        elif op_type == TokenType.OR:
            return self.is_truthy(left) or self.is_truthy(right)
        else:
            raise InterpreterError(f"Unknown binary operator: {expr.op.value}", 
                                 expr.line, expr.column)
    
    def evaluate_unary_op(self, expr: UnaryOp) -> Any:
        """Evaluate unary operation"""
        value = self.evaluate_expression(expr.expr)
        
        if expr.op.type == TokenType.MINUS:
            return -value
        elif expr.op.type == TokenType.NOT:
            return not self.is_truthy(value)
        else:
            raise InterpreterError(f"Unknown unary operator: {expr.op.value}", 
                                 expr.line, expr.column)
    
    def is_truthy(self, value: Any) -> bool:
        """Check if a value is truthy"""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True

