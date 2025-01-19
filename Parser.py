from TokenType import TokenType, TokenBase, DataType, Keywords
from TokenType import BlockStart, StatementTerminate, DataMod
from enum import Enum
from pprint import pprint


def _debug(func):
    """
    A decorator to print debug information about a function call.
    """
    def wrapper(*args, **kwargs):
        print(f"Debug:  {func.__name__}")
        print(f"Arguments: {args[1:]}")  # Skip 'self' in methods
        # print(f"Keyword Arguments: {kwargs}")

        result = func(*args, **kwargs)

        print(f"Returned: {result}")
        # print(f"--- End Debug ---\n")
        return result
    return wrapper


def debug(func):
    """
    A decorator to print debug information about a function call.
    """
    def wrapper(*args, **kwargs):
        print(f"\nDebug:  {func.__name__.upper()}")
        token = args[0].current_token()
        print(f"Recieved: {token.Id:>12} {token.ofType:>12} {token.value:>12}")

        result = func(*args, **kwargs)

        print(f"{func.__name__}  Returned: {result}\n\n")
        # print(f"--- End Debug ---\n")
        return result
    return wrapper


def debug_match(func):
    """
    A decorator to print debug information about a function call.
    """
    def wrapper(*args, **kwargs):
        print(f"\nDebug: {func.__name__.upper()}")
        token = args[0].current_token()
        print(f"Recieved: {token.Id:>12} {token.ofType:>12} {token.value:>12}")
        print(f"Expecting: {args[1]:>31}")
        if len(args) > 2: print(f"N: {args[2]:>31}")
        # print(f"Keyword Arguments: {kwargs}")

        result = func(*args, **kwargs)

        print(f"Match!: {result}\n")
        # print(f"--- End Debug ---\n")
        return result
    return wrapper


def log_scope(func):
    def wrapper(*args, **kwargs):
        print(f"--- Debugging {func.__name__} ---")
        print(f"Arguments: {args}, {kwargs}")

        result = func(*args, **kwargs)

        print("--- Local Variables ---")
        for name, value in locals().items():
            if name not in {'func', 'args', 'kwargs', 'result'}:  # Avoid clutter
                print(f"{name}: {value}")
        print(f"Result: {result}")
        print("--- End Debugging ---\n")

        return result
    return wrapper


class Parser:
    def __init__(self, tokens):
        """
        Initialize the parser with a list of tokens.
        """
        self.tokens = tokens
        self.position = 0

        self.scope = []
        self.error = 0
        self.peek_error = 0
        self.match_error = 0
        self.unresolveable_error = 0
        self.looking_for_stack = {}

        self.counter_main_loop = 0

    def current_token(self):
        """
        Get the current token.
        """
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def next_token(self):
        """
        Advance to the next token and return it.
        """
        self.position += 1
        return self.current_token()

    @debug_match
    def match(self, expected_type):
        """
        Consume a token if it matches the expected type; raise an error otherwise.
        """
        token = self.current_token()
        if token and token.ofType == expected_type:
            self.next_token()
            return token
        else:
            self.match_error += 1

            raise SyntaxError(f"Unexpected token: {token.ofType} at position {self.position}, expected {expected_type}")

    @debug_match
    def peek(self, expected_type, n=0):
        if n > 0: print('N: ', n)
        print(self.current_token)

        n = self.position + n

        token = self.tokens[n]
        if type(expected_type) == TokenBase:
            if token and token.base == expected_type:
                return True
            else:
                self.peek_error += 1
                return False
        if token and token.ofType == expected_type:
            return True
        else:
            self.peek_error += 1
            return False

    # Returns a list of the next n tokens
    @debug
    def scan(self, n):
        temp_pos = self.position
        if len(self.tokens) < temp_pos + n:
            raise SyntaxError(f"Scan called with {n}! number of tokens {len(self.tokens)}, position: {self.position}")

        result = []
        while n >= 0:
            token = self.tokens[temp_pos]
            result.append(token)
            n -= 1

        if token and token.ofType == expected_type:
            return result
        else:
            return None

    def group_match(self, group_func):
        """
        Match the current token against a group of token types.

        Parameters:
            group (list): A list of token types to match.

        Returns:
            dict: The matched token, or raises an exception if no match.
        """
        if self.current_token():
            if group_func(self.current_token()):
                self.next_token()
                return token
        raise SyntaxError(f"Unexpected token: {self.current_token()}, expected one of {group_func}")

    def parse_program(self):
        """
        Parse a program (example grammar rule).
        """
        # A program consists of a series of statements.
        statements = []
        token = self.current_token()
        while token:
            print('parse_program, main loop')
            self.counter_main_loop += 1

            token = self.current_token()
            print(token)

            print('calling parse_statement')
            statements.append(self.parse_statement())

            if self.error > 0:
                raise Exception(f'Unhandled Error {self.current_token=}, {token=}, {self.match_error}')
            if self.match_error > 0:
                raise Exception(f'Unhandled Match Error {self.current_token=}, {token=}, {self.match_error}')
            if self.unresolveable_error > 0:
                raise Exception(f'Unresolved Error {self.current_token=}, {token=}, {self.unresolveable_error}')

            if token == self.current_token():
                token = False
            elif self.position >= len(self.tokens):
                token = False

        print(statements, '\n\n')

        print('Completed!')
        print('main loop events: ', self.counter_main_loop)
        print('len tokens: ', len(self.tokens))
        print('final position: ', self.position)

        return {"type": "Program", "body": statements}

    def lookahead(self, target_low, target_high, skip_whitespace=True):
        temp_pos = self.position

        while temp_pos < len(self.tokens):
            token = self.tokens[temp_pos]

            if token.ofType == target_low: return -1
            if token.ofType == target_high: return 1

            temp_pos += 1

        return None

    def parse_statement(self):
        print('parse_statement')
        print(self.current_token())

        token = self.current_token()

        if token.ofType == TokenType.IDENTIFIER:

            lookahead = self.lookahead(TokenType.DELIM_SEMICOLON, TokenType.DELIM_LBRACE)

            if lookahead < 0:
                print('returning parse_function_declaration')
                return self.parse_function_declaration()
            elif lookahead > 0:
                print('returning parse_function_definition')
                return self.parse_function_definition()
            raise SyntaxError(f"Unexpected token: {token.ofType} at position {self.position}")
        else:
            breakpoint()
            raise SyntaxError(f"Unexpected token: {token.ofType} at position {self.position}")

    def parse_function_definition(self):
        """
        Parse a function definition.
        Example: `int foo(int a, float b) { return a + b; }`
        """
        print('parse_funckion_definition')
        print(self.current_token())

        return_type = self.match(TokenType.IDENTIFIER)  # Match the return type
        function_name = self.match(TokenType.IDENTIFIER)  # Match the function name

        print('returntype set, functionname set, ', self.current_token())
        self.match(TokenType.DELIM_LPAREN)  # Match '('
        parameters = []
        if self.peek(TokenType.IDENTIFIER):
            parameters = self.parse_parameters()

        self.match(TokenType.DELIM_RPAREN)  # Match ')'
        print('parse function definition, after match')
        body = self.parse_block_statement()  # Parse the function body

        return {
            "type": "FunctionDefinition",
            "returnType": return_type.value,
            "name": function_name.value,
            "parameters": parameters,
            "body": body
        }

    def parse_function_call(self):
        """
        Parse a function definition.
        Example: `int foo(int a, float b) { return a + b; }`
        """
        print('parse_function_call: ', self.current_token())

        function_name = self.match(TokenType.IDENTIFIER)  # Match the function name
        self.match(TokenType.DELIM_LPAREN)  # Match '('

        parameters = []
        if self.peek(TokenType.IDENTIFIER):
            parameters = self.parse_parameters()

        self.match(TokenType.DELIM_RPAREN)  # Match ')'
        print('parse function call, after match')

        return {
            "type": "FunctionCall",
            "name": function_name.value,
            "parameters": parameters
        }

    def parse_function_declaration(self):
        """
        Parse a function declaration.
        Example: `int foo(int a, float b);`
        """
        return_type = self.match(TokenType.IDENTIFIER)  # Match the return type

        function_name = self.match(TokenType.IDENTIFIER)  # Match the function name

        self.match(TokenType.DELIM_LPAREN)  # Match '('
        parameters = []
        if self.peek(TokenType.IDENTIFIER):
            parameters = self.parse_parameters()
        self.match(TokenType.DELIM_RPAREN)  # Match ')'
        self.match(TokenType.DELIM_SEMICOLON)  # Match ';'

        return {
            "type": "FunctionDeclaration",
            "returnType": return_type.value,
            "name": function_name.value,
            "parameters": parameters
        }

    def parse_parameter(self):
        """
        Parse function parameters.
        Example: `int a, float b`
        """
        param_type = self.match(TokenType.IDENTIFIER)  # Match parameter type
        param_name = self.match(TokenType.IDENTIFIER)  # Match parameter name
        return { "type": "Parameter",
                "paramType": param_type.value,
                "name": param_name.value}

    @debug
    def parse_parameters(self):
        """
        Parse function parameters.
        Example: `int a, float b`
        """
        parameters = []
        token = None
        while token != self.current_token() and self.match_error == 0:
            parameters.append(self.parse_parameter())
            token = self.current_token()
            if self.peek(TokenType.DELIM_COMMA):
                self.match(TokenType.DELIM_COMMA)
        return parameters

    def parse_if_statement(self):
        """
        Parse an if statement.
        """
        self.match(TokenType.KEYWORD_IF.value)
        self.match(TokenType.DELIM_LPAREN.value)  # Expect '('
        condition = self.parse_expression()
        self.match(TokenType.DELIM_RPAREN.value)  # Expect ')'
        then_block = self.parse_block_statement()
        else_block = None
        if self.current_token() and self.current_token().ofType == TokenType.KEYWORD_ELSE.value:
            self.match(TokenType.KEYWORD_ELSE.value)
            else_block = self.parse_block_statement()
        return {"type": "IfStatement", "condition": condition, "then": then_block, "else": else_block}

    def parse_while_statement(self):
        """
        Parse a while statement.
        """
        self.match(TokenType.KEYWORD_WHILE.value)
        self.match(TokenType.DELIM_LPAREN.value)
        condition = self.parse_expression()
        self.match(TokenType.DELIM_RPAREN.value)
        body = self.parse_block_statement()
        return {"type": "WhileStatement", "condition": condition, "body": body}
    @debug
    def parse_return_statement(self):
        """
        Parse a return statement.
        """
        self.match(TokenType.KEYWORD_RETURN)
        expression = self.parse_expression()
        self.match(TokenType.DELIM_SEMICOLON)
        return {"type": "ReturnStatement", "expression": expression}

    def parse_struct_declaration(self):
        """
        Parse a struct declaration.
        """
        self.match(TokenType.KEYWORD_STRUCT)
        identifier = self.match(TokenType.IDENTIFIER)
        self.match(TokenType.DELIM_LBRACE)
        fields = []
        while self.current_token() and self.current_token().ofType != TokenType.DELIM_RBRACE:
            fields.append(self.parse_declaration())
        self.match(TokenType.DELIM_RBRACE)
        self.match(TokenType.DELIM_SEMICOLON)
        return {"type": "StructDeclaration", "name": identifier, "fields": fields}

    def parse_block_statement(self):
        """
        Parse a block statement (enclosed in curly braces).
        """
        print('parse_block_statement: ',  self.current_token())

        statements = []

        Next = self.match(TokenType.DELIM_LBRACE)
        while Next and not self.peek(TokenType.DELIM_RBRACE):
            statements.append(self.parse_expression_statement())

            if Next == self.current_token():
                Next = False
                self.error += 1

        self.match(TokenType.DELIM_RBRACE)
        return {"type": "BlockStatement", "body": statements}

    @debug
    def parse_expression_statement(self):
        """
        Parse an expression statement.
        """
        # no more statements
        # token = self.current_token()
        print('parse_expression_statement: ', self.current_token())
        if self.peek(TokenBase.KEYWORD):

            if self.peek(TokenType.KEYWORD_IF):
                return self.parse_if_statement()
            elif self.peek(TokenType.KEYWORD_WHILE):
                return self.parse_while_statement()
            # This one might be special, all others we will be called again within this block
            elif self.peek(TokenType.KEYWORD_RETURN):
                return self.parse_return_statement()
            else:
                print('parse_expression_statement!!!!!!!!!!: ', self.current_token())
                return self.parse_expression_statement()
                
        print('parse_expression_statement: ', self.current_token())
        expression = self.parse_expression()
        
        self.match(TokenType.DELIM_SEMICOLON)
        return {"type": "ExpressionStatement", "expression": expression}

    @debug
    def parse_expression_prefix(self):
        """
        Parse an expression (placeholder for now).
        """
        token = self.current_token()

        if self.peek(TokenType.LPAREN):
            return self.parse_function_call()
        expressions = []

        token = self.parse_declaration()

        while token and not self.peek(TokenType.DELIM_SEMICOLON):
            if self.peek(TokenType, TokenBase.OPERATOR):
                expressions.append(self.parse_expression())

            if token == self.current_token():
                Next = False
                self.error += 1
        return {"type": "Expression", "Expressions": {expressions}}

    @debug
    def parse_expression(self):
        

        if self.peek(TokenType.DELIM_SEMICOLON, 1):
            
            temp_tokenType = self.current_token()
            l_operand = self.parse_operand()
            return {"type": "Literal" if temp_tokenType == TokenType.LITERAL_SPECIAL else "Identifier", "value": l_operand}
        # if self.peek(TokenType.DELIM_SEMICOLON, 1):
        #     temp_tokenType = self.current_token()
        #     l_operand = self.parse_operand()
        #     return {"type": "Literal" if temp_tokenType == TokenType.LITERAL_SPECIAL else "Identifier", "value": token.value}

        else:
            l_operand = self.parse_operand()
            operator = self.match(TokenType.OPERATOR_ARITHMETIC)
            r_operand = self.match(TokenType.IDENTIFIER)

        return {"type": "BinaryOperation", "left": l_operand, "operator": operator, "right": r_operand}

    def parse_operand(self):
        token = None
        if self.peek(TokenType.IDENTIFIER):
            token = self.match(TokenType.IDENTIFIER)
        else:
            token = self.match(TokenType.LITERAL_SPECIAL)
        return {"type": "Literal" if token.ofType == TokenType.LITERAL_SPECIAL else "Identifier", "value": token.value}

    def parse_declaration(self):
        """
        Parse a variable declaration (e.g., int x;).
        """
        # Check if this is actually a declaration
        if self.peek(TokenType.IDENTIFIER, 1):
            type_token = self.match(TokenType.IDENTIFIER)  # Extend for other types
            identifier = self.match(TokenType.IDENTIFIER)

            return {"type": "Declaration", "varType": type_token, "name": identifier}
        # This is not a declaration, return the identifier
        else:
            identifier = self.match(TokenType.IDENTIFIER)

            return {"type": "Assignment", "varType": type_token, "name": identifier}



