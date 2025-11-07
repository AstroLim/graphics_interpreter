"""
Lexer (Tokenizer) for the Drawing Interpreter
Handles lexical analysis and tokenization of input commands.
"""

import re
from enum import Enum
from typing import List, Optional, Tuple


class TokenType(Enum):
    # Keywords
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    TO = "TO"
    STEP = "STEP"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    VAR = "VAR"
    LET = "LET"
    
    # Drawing commands
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    PENUP = "PENUP"
    PENDOWN = "PENDOWN"
    CIRCLE = "CIRCLE"
    RECTANGLE = "RECTANGLE"
    LINE = "LINE"
    POLYGON = "POLYGON"
    ARC = "ARC"
    CLEAR = "CLEAR"
    RESET = "RESET"
    COLOR = "COLOR"
    FILL = "FILL"
    NOFILL = "NOFILL"
    WIDTH = "WIDTH"
    GOTO = "GOTO"
    POSITION = "POSITION"
    SHOW = "SHOW"
    HIDE = "HIDE"
    
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    BOOLEAN = "BOOLEAN"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    POWER = "POWER"
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Assignment
    ASSIGN = "ASSIGN"
    
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"


class Token:
    def __init__(self, type: TokenType, value: any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and 
                self.value == other.value and
                self.line == other.line)


class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"LexerError at line {line}, column {column}: {message}")


class Lexer:
    KEYWORDS = {
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'to': TokenType.TO,
        'step': TokenType.STEP,
        'function': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'var': TokenType.VAR,
        'let': TokenType.LET,
        'forward': TokenType.FORWARD,
        'fd': TokenType.FORWARD,
        'backward': TokenType.BACKWARD,
        'bk': TokenType.BACKWARD,
        'left': TokenType.LEFT,
        'lt': TokenType.LEFT,
        'right': TokenType.RIGHT,
        'rt': TokenType.RIGHT,
        'penup': TokenType.PENUP,
        'pu': TokenType.PENUP,
        'pendown': TokenType.PENDOWN,
        'pd': TokenType.PENDOWN,
        'circle': TokenType.CIRCLE,
        'rectangle': TokenType.RECTANGLE,
        'rect': TokenType.RECTANGLE,
        'line': TokenType.LINE,
        'polygon': TokenType.POLYGON,
        'arc': TokenType.ARC,
        'clear': TokenType.CLEAR,
        'reset': TokenType.RESET,
        'color': TokenType.COLOR,
        'fill': TokenType.FILL,
        'nofill': TokenType.NOFILL,
        'width': TokenType.WIDTH,
        'goto': TokenType.GOTO,
        'position': TokenType.POSITION,
        'pos': TokenType.POSITION,
        'show': TokenType.SHOW,
        'hide': TokenType.HIDE,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
    }
    
    OPERATORS = {
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '*': TokenType.MULTIPLY,
        '/': TokenType.DIVIDE,
        '%': TokenType.MODULO,
        '^': TokenType.POWER,
        '==': TokenType.EQUALS,
        '!=': TokenType.NOT_EQUALS,
        '<=': TokenType.LESS_EQUAL,
        '>=': TokenType.GREATER_EQUAL,
        '<': TokenType.LESS_THAN,
        '>': TokenType.GREATER_THAN,
        '=': TokenType.ASSIGN,
    }
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.text):
            return None
        return self.text[pos]
    
    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> float:
        start_pos = self.pos
        start_col = self.column
        
        # Read integer part
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        # Read fractional part
        if self.current_char() == '.':
            self.advance()
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        # Read scientific notation
        if self.current_char() and self.current_char().lower() == 'e':
            self.advance()
            if self.current_char() in '+-':
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        num_str = self.text[start_pos:self.pos]
        try:
            return float(num_str)
        except ValueError:
            raise LexerError(f"Invalid number format: {num_str}", self.line, start_col)
    
    def read_string(self) -> str:
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        start_col = self.column
        
        value = []
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char() == 'n':
                    value.append('\n')
                elif self.current_char() == 't':
                    value.append('\t')
                elif self.current_char() == '\\':
                    value.append('\\')
                elif self.current_char() == quote_char:
                    value.append(quote_char)
                else:
                    value.append(self.current_char())
                self.advance()
            else:
                value.append(self.current_char())
                self.advance()
        
        if not self.current_char():
            raise LexerError("Unterminated string", self.line, start_col)
        
        self.advance()  # Skip closing quote
        return ''.join(value)
    
    def read_identifier(self) -> str:
        start_pos = self.pos
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            self.advance()
        return self.text[start_pos:self.pos]
    
    def tokenize(self) -> List[Token]:
        self.tokens = []
        self.pos = 0
        self.line = 1
        self.column = 1
        
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Handle comments
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Handle newlines
            if self.current_char() == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.advance()
                continue
            
            # Handle numbers
            if self.current_char().isdigit() or (self.current_char() == '.' and 
                                                  self.peek_char() and 
                                                  self.peek_char().isdigit()):
                start_col = self.column
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line, start_col))
                continue
            
            # Handle strings
            if self.current_char() in '"\'':
                start_col = self.column
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, self.line, start_col))
                continue
            
            # Handle operators (check multi-character first)
            if self.current_char() + (self.peek_char() or '') in self.OPERATORS:
                op = self.current_char() + self.peek_char()
                start_col = self.column
                self.advance()
                self.advance()
                self.tokens.append(Token(self.OPERATORS[op], op, self.line, start_col))
                continue
            
            if self.current_char() in self.OPERATORS:
                start_col = self.column
                op = self.current_char()
                self.advance()
                self.tokens.append(Token(self.OPERATORS[op], op, self.line, start_col))
                continue
            
            # Handle identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                start_col = self.column
                identifier = self.read_identifier()
                
                # Check if it's a keyword
                if identifier.lower() in self.KEYWORDS:
                    token_type = self.KEYWORDS[identifier.lower()]
                    # Special handling for boolean values
                    if token_type == TokenType.BOOLEAN:
                        value = identifier.lower() == 'true'
                        self.tokens.append(Token(token_type, value, self.line, start_col))
                    else:
                        self.tokens.append(Token(token_type, identifier.lower(), self.line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, self.line, start_col))
                continue
            
            # Handle delimiters
            delimiter_map = {
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                ':': TokenType.COLON,
            }
            
            if self.current_char() in delimiter_map:
                start_col = self.column
                char = self.current_char()
                self.tokens.append(Token(delimiter_map[char], char, self.line, start_col))
                self.advance()
                continue
            
            # Unknown character
            raise LexerError(f"Unexpected character: {repr(self.current_char())}", 
                           self.line, self.column)
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

