"""
Parser for the Drawing Interpreter
Builds an Abstract Syntax Tree (AST) from tokens.
"""

from typing import List, Optional, Any
from lexer import Token, TokenType, LexerError


class ASTNode:
    """Base class for all AST nodes"""
    def __init__(self, token: Optional[Token] = None):
        self.token = token
        self.line = token.line if token else 0
        self.column = token.column if token else 0
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        super().__init__()
        self.statements = statements
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


class Statement(ASTNode):
    pass


class Expression(ASTNode):
    pass


class NumberLiteral(Expression):
    def __init__(self, token: Token, value: float):
        super().__init__(token)
        self.value = value
    
    def __repr__(self):
        return f"Number({self.value})"


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str):
        super().__init__(token)
        self.value = value
    
    def __repr__(self):
        return f"String({repr(self.value)})"


class BooleanLiteral(Expression):
    def __init__(self, token: Token, value: bool):
        super().__init__(token)
        self.value = value
    
    def __repr__(self):
        return f"Boolean({self.value})"


class Identifier(Expression):
    def __init__(self, token: Token, name: str):
        super().__init__(token)
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"


class BinaryOp(Expression):
    def __init__(self, left: Expression, op: Token, right: Expression):
        super().__init__(op)
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op.value}, {self.right})"


class UnaryOp(Expression):
    def __init__(self, op: Token, expr: Expression):
        super().__init__(op)
        self.op = op
        self.expr = expr
    
    def __repr__(self):
        return f"UnaryOp({self.op.value}, {self.expr})"


class Assignment(Statement):
    def __init__(self, identifier: Identifier, value: Expression):
        super().__init__(identifier.token)
        self.identifier = identifier
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.identifier.name} = {self.value})"


class VariableDeclaration(Statement):
    def __init__(self, identifier: Identifier, value: Optional[Expression] = None):
        super().__init__(identifier.token)
        self.identifier = identifier
        self.value = value
    
    def __repr__(self):
        if self.value:
            return f"VarDecl({self.identifier.name} = {self.value})"
        return f"VarDecl({self.identifier.name})"


class FunctionCall(Expression):
    def __init__(self, name: Identifier, args: List[Expression]):
        super().__init__(name.token)
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall({self.name.name}({len(self.args)} args))"


class IfStatement(Statement):
    def __init__(self, condition: Expression, then_block: List[Statement], 
                 else_block: Optional[List[Statement]] = None):
        super().__init__(condition.token if hasattr(condition, 'token') else None)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    
    def __repr__(self):
        return f"IfStatement(condition={self.condition}, then={len(self.then_block)}, else={len(self.else_block) if self.else_block else 0})"


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: List[Statement]):
        super().__init__(condition.token if hasattr(condition, 'token') else None)
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"WhileStatement(condition={self.condition}, body={len(self.body)})"


class ForStatement(Statement):
    def __init__(self, var: Identifier, start: Expression, end: Expression, 
                 step: Optional[Expression], body: List[Statement]):
        super().__init__(var.token)
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body
    
    def __repr__(self):
        return f"ForStatement({self.var.name}, {self.start} to {self.end}, step={self.step}, body={len(self.body)})"


class FunctionDefinition(Statement):
    def __init__(self, name: Identifier, params: List[Identifier], body: List[Statement]):
        super().__init__(name.token)
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"FunctionDef({self.name.name}({len(self.params)} params), body={len(self.body)})"


class ReturnStatement(Statement):
    def __init__(self, value: Optional[Expression] = None, token: Optional[Token] = None):
        super().__init__(token)
        self.value = value
    
    def __repr__(self):
        return f"Return({self.value})"


class ParserError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"ParserError at line {line}, column {column}: {message}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Optional[Token]:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 1) -> Optional[Token]:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]
    
    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1
    
    def expect(self, token_type: TokenType, error_msg: str = None) -> Token:
        token = self.current_token()
        if not token or token.type != token_type:
            if error_msg:
                raise ParserError(error_msg, 
                                token.line if token else 0, 
                                token.column if token else 0)
            raise ParserError(f"Expected {token_type.name}, got {token.type.name if token else 'EOF'}", 
                            token.line if token else 0, 
                            token.column if token else 0)
        self.advance()
        return token
    
    def skip_newlines(self):
        while self.current_token() and self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        statements = []
        self.skip_newlines()
        
        while self.current_token() and self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[Statement]:
        token = self.current_token()
        if not token:
            return None
        
        if token.type == TokenType.VAR or token.type == TokenType.LET:
            return self.parse_variable_declaration()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.FUNCTION:
            return self.parse_function_definition()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.IDENTIFIER:
            # Could be assignment or function call
            if self.peek_token() and self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
            else:
                # Function call as statement
                expr = self.parse_expression()
                if isinstance(expr, FunctionCall):
                    return expr
                raise ParserError(f"Unexpected expression: {expr}", token.line, token.column)
        else:
            # Check if it's a drawing command keyword followed by parentheses
            drawing_command_types = {
                TokenType.FORWARD, TokenType.BACKWARD, TokenType.LEFT, TokenType.RIGHT,
                TokenType.PENUP, TokenType.PENDOWN, TokenType.CIRCLE, TokenType.RECTANGLE,
                TokenType.LINE, TokenType.POLYGON, TokenType.ARC, TokenType.CLEAR,
                TokenType.RESET, TokenType.COLOR, TokenType.FILL, TokenType.NOFILL,
                TokenType.WIDTH, TokenType.GOTO, TokenType.POSITION, TokenType.SHOW, TokenType.HIDE
            }
            
            if token.type in drawing_command_types:
                # Try parsing as expression (function call)
                expr = self.parse_expression()
                if isinstance(expr, FunctionCall):
                    return expr
                # If no parentheses, it might be a command without args (like penup, pendown, etc.)
                # But those should have parentheses in our syntax
                raise ParserError(f"Drawing command {token.value} must be called with parentheses", 
                                token.line, token.column)
            
            # Try parsing as expression statement
            expr = self.parse_expression()
            if isinstance(expr, FunctionCall):
                return expr
            raise ParserError(f"Unexpected token: {token.type.name}", token.line, token.column)
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        self.advance()  # Skip VAR or LET
        identifier = self.parse_identifier()
        value = None
        if self.current_token() and self.current_token().type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
        return VariableDeclaration(identifier, value)
    
    def parse_assignment(self) -> Assignment:
        identifier = self.parse_identifier()
        self.expect(TokenType.ASSIGN, "Expected '=' after identifier")
        value = self.parse_expression()
        return Assignment(identifier, value)
    
    def parse_if_statement(self) -> IfStatement:
        self.advance()  # Skip IF
        condition = self.parse_expression()
        
        self.expect(TokenType.LBRACE, "Expected '{' after if condition")
        then_block = self.parse_block()
        self.expect(TokenType.RBRACE, "Expected '}' after if block")
        
        else_block = None
        if self.current_token() and self.current_token().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.LBRACE, "Expected '{' after else")
            else_block = self.parse_block()
            self.expect(TokenType.RBRACE, "Expected '}' after else block")
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        self.advance()  # Skip WHILE
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE, "Expected '{' after while condition")
        body = self.parse_block()
        self.expect(TokenType.RBRACE, "Expected '}' after while block")
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        self.advance()  # Skip FOR
        var = self.parse_identifier()
        self.expect(TokenType.ASSIGN, "Expected '=' after for variable")
        start = self.parse_expression()
        self.expect(TokenType.TO, "Expected 'to' after start value")
        end = self.parse_expression()
        
        step = None
        if self.current_token() and self.current_token().type == TokenType.STEP:
            self.advance()
            step = self.parse_expression()
        
        self.expect(TokenType.LBRACE, "Expected '{' after for statement")
        body = self.parse_block()
        self.expect(TokenType.RBRACE, "Expected '}' after for block")
        return ForStatement(var, start, end, step, body)
    
    def parse_function_definition(self) -> FunctionDefinition:
        self.advance()  # Skip FUNCTION
        name = self.parse_identifier()
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        
        params = []
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            params.append(self.parse_identifier())
            while self.current_token() and self.current_token().type == TokenType.COMMA:
                self.advance()
                params.append(self.parse_identifier())
        
        self.expect(TokenType.RPAREN, "Expected ')' after function parameters")
        self.expect(TokenType.LBRACE, "Expected '{' after function parameters")
        body = self.parse_block()
        self.expect(TokenType.RBRACE, "Expected '}' after function body")
        return FunctionDefinition(name, params, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        token = self.current_token()
        self.advance()  # Skip RETURN
        value = None
        if self.current_token() and self.current_token().type != TokenType.NEWLINE:
            value = self.parse_expression()
        return ReturnStatement(value, token)
    
    def parse_block(self) -> List[Statement]:
        statements = []
        self.skip_newlines()
        
        while (self.current_token() and 
               self.current_token().type != TokenType.RBRACE and
               self.current_token().type != TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return statements
    
    def parse_expression(self) -> Expression:
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        left = self.parse_logical_and()
        
        while self.current_token() and self.current_token().type == TokenType.OR:
            op = self.current_token()
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        left = self.parse_equality()
        
        while self.current_token() and self.current_token().type == TokenType.AND:
            op = self.current_token()
            self.advance()
            right = self.parse_equality()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_equality(self) -> Expression:
        left = self.parse_comparison()
        
        while (self.current_token() and 
               self.current_token().type in (TokenType.EQUALS, TokenType.NOT_EQUALS)):
            op = self.current_token()
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> Expression:
        left = self.parse_additive()
        
        while (self.current_token() and 
               self.current_token().type in (TokenType.LESS_THAN, TokenType.GREATER_THAN,
                                            TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL)):
            op = self.current_token()
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> Expression:
        left = self.parse_multiplicative()
        
        while (self.current_token() and 
               self.current_token().type in (TokenType.PLUS, TokenType.MINUS)):
            op = self.current_token()
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        left = self.parse_unary()
        
        while (self.current_token() and 
               self.current_token().type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO)):
            op = self.current_token()
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> Expression:
        if (self.current_token() and 
            self.current_token().type in (TokenType.MINUS, TokenType.NOT)):
            op = self.current_token()
            self.advance()
            expr = self.parse_unary()
            return UnaryOp(op, expr)
        
        return self.parse_power()
    
    def parse_power(self) -> Expression:
        left = self.parse_primary()
        
        while self.current_token() and self.current_token().type == TokenType.POWER:
            op = self.current_token()
            self.advance()
            right = self.parse_primary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_primary(self) -> Expression:
        token = self.current_token()
        
        if not token:
            raise ParserError("Unexpected end of input", 0, 0)
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberLiteral(token, token.value)
        
        if token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token, token.value)
        
        if token.type == TokenType.BOOLEAN:
            self.advance()
            return BooleanLiteral(token, token.value)
        
        # Check if it's a drawing command keyword that should be treated as a function call
        drawing_command_types = {
            TokenType.FORWARD, TokenType.BACKWARD, TokenType.LEFT, TokenType.RIGHT,
            TokenType.PENUP, TokenType.PENDOWN, TokenType.CIRCLE, TokenType.RECTANGLE,
            TokenType.LINE, TokenType.POLYGON, TokenType.ARC, TokenType.CLEAR,
            TokenType.RESET, TokenType.COLOR, TokenType.FILL, TokenType.NOFILL,
            TokenType.WIDTH, TokenType.GOTO, TokenType.POSITION, TokenType.SHOW, TokenType.HIDE
        }
        
        if token.type in drawing_command_types and self.peek_token() and self.peek_token().type == TokenType.LPAREN:
            # Treat drawing command as function call
            identifier = Identifier(token, token.value)
            self.advance()  # Consume the keyword token
            return self.parse_function_call(identifier)
        
        if token.type == TokenType.IDENTIFIER:
            identifier = self.parse_identifier()
            # Check if it's a function call
            if self.current_token() and self.current_token().type == TokenType.LPAREN:
                return self.parse_function_call(identifier)
            return identifier
        
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise ParserError(f"Unexpected token in expression: {token.type.name}", 
                        token.line, token.column)
    
    def parse_identifier(self) -> Identifier:
        token = self.current_token()
        if not token or token.type != TokenType.IDENTIFIER:
            raise ParserError(f"Expected identifier, got {token.type.name if token else 'EOF'}", 
                            token.line if token else 0, 
                            token.column if token else 0)
        self.advance()
        return Identifier(token, token.value)
    
    def parse_function_call(self, name: Identifier) -> FunctionCall:
        self.advance()  # Skip '('
        args = []
        
        if self.current_token() and self.current_token().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.current_token() and self.current_token().type == TokenType.COMMA:
                self.advance()
                args.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN, "Expected ')' after function arguments")
        return FunctionCall(name, args)

