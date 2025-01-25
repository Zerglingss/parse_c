from TokenType_placeholder import TokenType, TokenBase, DataType, Keywords
from TokenType_placeholder import BlockStart, StatementTerminate, DataMod, Operators, BinaryOperatorPrecedence
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
        if token.ofType == None:
            print(f'debug(): NONE TYPE TOKEN  {token.Id:>12}{token.value:>12}')
        else:
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
        if token.ofType == None:
            print('NONE TYPE')
        else:
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
    # Unused
    def match_soft(self, expected_type):
        """
        Match a token without consuming. Currently only for Decl and Assign in one statement. Raises exception, not meant for lookahead
        """
        token = self.current_token()
        if token and token.ofType == expected_type:
            return token
        else:
            self.match_error += 1

            raise SyntaxError(f"Unexpected token: {token.ofType} at position {self.position}, expected {expected_type}")

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

            raise SyntaxError(f"MATCH ERROR! Unexpected token: {token.ofType} at position {self.position}, expected {expected_type}")

    @debug_match
    def peek(self, expected_type, n=0):
        
        if n > 0: print('N: ', n)
        print(self.current_token)

        if expected_type == None:
            raise SyntaxError('Peek() encountered token of type None!')
            return False

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

    @debug
    # Takes in a pattern, matches, skips are possible, searches for term
    # Just going to make specific named ones for now
    def scan(self, *args):
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

    # Declaration is currently IDENTIFIER IDENTIFIER, soon IDENTIFIER __ IDENTIFIER
    @debug
    # Takes in a pattern, matches, skips are possible, searches for term
    # Just going to make specific named ones for now
    def scan_declare_init(self):

        temp_pos = self.position

        token = self.tokens[temp_pos]

        match_list = [TokenType.OPERATOR_ASSIGNMENT, TokenType.IDENTIFIER, TokenType.IDENTIFIER]
        # technically only '=" when we fix this, also check parse_declaration for fix

        while token.ofType != TokenType.DELIM_SEMICOLON:
            if token.ofType in match_list:
                temp = match_list.pop()
                print(f'{token.ofType}   {temp}')
                if token.ofType != temp:
                    return False
            temp_pos += 1
            token = self.tokens[temp_pos]
        if match_list:
            return False
        return True

    # Declaration is currently IDENTIFIER IDENTIFIER, soon IDENTIFIER __ IDENTIFIER
    @debug
    # Takes in a pattern, matches, skips are possible, searches for term
    # Just going to make specific named ones for now
    def scan_declaration(self):

        temp_pos = self.position

        token = self.tokens[temp_pos]

        match_fail = [TokenType.OPERATOR_ASSIGNMENT, TokenType.DELIM_SEMICOLON, TokenType.DELIM_LPAREN]
        match_list = [TokenType.IDENTIFIER, TokenType.IDENTIFIER]
        # technically only '=" when we fix this, also check parse_declaration for fix

        while token.ofType not in match_fail:
            if token.ofType in match_list:
                temp = match_list.pop()
                print(f'{token.ofType}   {temp}')
                if token.ofType != temp:
                    return False
            temp_pos += 1
            token = self.tokens[temp_pos]
        if match_list:
            return False
        return True

    @debug
    # Takes in a pattern, matches, skips are possible, searches for term
    # Just going to make specific named ones for now
    # def scan_arithmetic(self):

    #     temp_pos = self.position

    #     match_fail = [TokenType.DELIM_SEMICOLON]
    #     match_list = [TokenType.OPERATOR_ARITHMETIC, TokenType.IDENTIFIER]
    #     # technically only '=" when we fix this, also check parse_declaration for fix

    #     while self.tokens[temp_pos].ofType not in match_fail:
    #         # Hack so that * isn't counted as arithmetic and cause a false neg
    #         if self.tokens[temp_pos].ofType == TokenType.OPERATOR_UNARY:
    #             temp_pos += 1
    #             continue
    #         if self.tokens[temp_pos].ofType in match_list:
    #             temp = match_list.pop()
    #             print(f'{self.tokens[temp_pos].ofType}   {temp}')
    #             if self.tokens[temp_pos].ofType != temp:
    #                 return False
    #         temp_pos += 1
    #     if match_list:
    #         return False
    #     return True


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

    def lookahead(self, target_low, target_stop):
        temp_pos = self.position

        while temp_pos < len(self.tokens):
            token = self.tokens[temp_pos]

            if token.ofType == target_low: return True
            if token.ofType == target_stop: return False

            temp_pos += 1

        return False

    @debug
    def lookahead_go(self, target_low, target_stop):
        temp_pos = self.position

        level = 0

        while temp_pos < len(self.tokens):
            print('ughghg')
            token = self.tokens[temp_pos]

            if token.ofType == TokenType.DELIM_LPAREN: level += 1
            if token.ofType == TokenType.DELIM_RPAREN:
                if level <= 0:
                    # This is prob a problem
                    # raise
                    return False
                level += 1

            if token.ofType == target_low: return True
            if token.ofType == target_stop: return False
            if token.ofType == TokenType.DELIM_SEMICOLON: return False
            if token.ofType == TokenType.DELIM_COMMA: return False
            if token.ofType == TokenType.DELIM_RPAREN: return False

            temp_pos += 1

        raise SyntaxError('EOF reached during lookahead')
        return False

    # def lookahead_x(self, target_low, target_high):
    #     temp_pos = self.position

    #     while temp_pos < len(self.tokens):
    #         token = self.tokens[temp_pos]

    #         if token.ofType == target_low: return -1
    #         if token.ofType == target_high: return 1

    #         temp_pos += 1

    #     return None

    def parse_program(self):
        """
        Parse a program (example grammar rule).
        """
        # A program consists of a series of statements.
        statements = []
        token = self.current_token()
        while token:
            self.counter_main_loop += 1

            token = self.current_token()
            print(token)

            # _prev
            # statements.append(self.parse_statement())
            if self.peek(TokenType.KEYWORD_STRUCT):
                statements.append(self.parse_struct_declaration())
            if self.peek(TokenType.KEYWORD_TYPEDEF):
                statements.append(self.parse_typedef())

            # Handles var decls, var decl&init, func decl, func definition
            statements.append(self.parse_declaration())


            if self.error > 0:
                raise Exception(f'Unhandled Error {self.current_token=}, {token=}, {self.match_error}')
            if self.match_error > 0:
                raise Exception(f'Unhandled Match Error {self.current_token=}, {token=}, {self.match_error}')
            if self.unresolveable_error > 0:
                raise Exception(f'Unresolved Error {self.current_token=}, {token=}, {self.unresolveable_error}')

            # We went through and didn't get a token, break
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

    # New definition type-spec init-declarator
    @debug
    def parse_declaration(self):

        type_token = self.match(TokenType.IDENTIFIER)
        identifier_token = self.match(TokenType.IDENTIFIER)

        # declarator
        print('here')
        print(self.current_token())
        if self.peek(TokenType.DELIM_SEMICOLON):
            self.match(TokenType.DELIM_SEMICOLON)
            return {"type": "Declaration", "varType": type_token.value, "name": identifier_token.value}

        # init-declarator
        elif self.peek(TokenType.OPERATOR_ASSIGNMENT):
            self.match(TokenType.OPERATOR_ASSIGNMENT) # Operator '=' todo
            # Technically call assignment_expression, an expression can be a comma sep list of assignment_expressions
            initializer = self.parse_primary_expression();
            self.match(TokenType.DELIM_SEMICOLON)
            return {"type": "Declaration", "varType": type_token.value, "name": identifier_token.value, "initializer": initializer}

        # Function Declaration (and possibly definition
        elif self.peek(TokenType.DELIM_LPAREN):
            self.match(TokenType.DELIM_LPAREN)  # Match '('
            parameters = []
            print(self.current_token())
            if self.peek(TokenType.IDENTIFIER):
                parameters = self.parse_parameters()

            self.match(TokenType.DELIM_RPAREN)  # Match ')'

        if not self.peek(TokenType.DELIM_SEMICOLON):
            # A '=' op is possible here
            body = self.parse_compound_statement()
            return {
                "type": "Function Declaration",
                "returnType": type_token.value,
                "name": identifier_token.value,
                "parameters": parameters,
                "body": body
            }
        else:
            self.match(TokenType.DELIM_SEMICOLON)
            return {
                "type": "Function Declaration",
                "returnType": type_token.value,
                "name": identifier_token.value,
                "parameters": parameters,
            }

    @debug
    def parse_function_call(self):
        """
        Parse a function definition.
        Example: `int foo(int a, float b) { return a + b; }`
        """
        print('parse_function_call: ', self.current_token())

        function_name = self.match(TokenType.IDENTIFIER)  # Match the function name
        self.match(TokenType.DELIM_LPAREN)  # Match '('

        parameters = []
        if not self.peek(TokenType.DELIM_RPAREN):
            parameters = self.parse_arguments()

        self.match(TokenType.DELIM_RPAREN)  # Match ')'
        print('parse function call, after match')

        return {
            "type": "FunctionCall",
            "name": function_name.value,
            "parameters": parameters
        }

    @debug
    # Note this could be parse_declarator, when we break declarator from declaration
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
    def parse_arguments(self):
        """
        Parse function parameters.
        Example: `int a, float b`
        """
        parameters = []
        token = None

        # potentially this should call parse_declaration
        # ms site says this is a declarator, vs declaration, i'm unsure the distinction atm

        while token != self.current_token() and self.match_error == 0:
            parameters.append(self.parse_expression())
            token = self.current_token()
            if self.peek(TokenType.DELIM_COMMA):
                self.match(TokenType.DELIM_COMMA)
            else:
                break
        
        return parameters

    @debug
    def parse_parameters(self):
        """
        Parse function parameters.
        Example: `int a, float b`
        """
        parameters = []
        token = None

        # potentially this should call parse_declaration
        # ms site says this is a declarator, vs declaration, i'm unsure the distinction atm

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
        self.match(TokenType.KEYWORD_IF)
        self.match(TokenType.DELIM_LPAREN)  # Expect '('
        condition = self.parse_expression()
        self.match(TokenType.DELIM_RPAREN)  # Expect ')'
        then_block = self.parse_compound_statement()
        else_block = None
        if self.current_token() and self.current_token().ofType == TokenType.KEYWORD_ELSE:
            self.match(TokenType.KEYWORD_ELSE)
            else_block = self.parse_compound_statement()
        return {"type": "IfStatement", "condition": condition, "then": then_block, "else": else_block}

    def parse_while_statement(self):
        """
        Parse a while statement.
        """
        self.match(TokenType.KEYWORD_WHILE)
        self.match(TokenType.DELIM_LPAREN)
        condition = self.parse_expression()
        self.match(TokenType.DELIM_RPAREN)
        body = self.parse_compound_statement()
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

    def parse_type(self):
        """
        Parse a type, such as int, float, or struct MyStruct.
        """
        if self.current_token().value == 'int':
            self.match(TokenType.IDENTIFIER)
            return {"base_type": "int"}
        elif self.current_token().value == 'float':
            self.match(TokenType.IDENTIFIER)
            return {"base_type": "float"}
        elif self.match(TokenType.KEYWORD_STRUCT):
            struct_name = self.match(TokenType.IDENTIFIER)
            if not struct_name:
                raise SyntaxError("Expected struct name after 'struct'.")
            return {"base_type": "struct", "name": struct_name.value}
        elif self.match(TokenType.OPERATOR_UNARY):  # Pointer types
            base_type = self.parse_type()
            base_type["pointer"] = True
            return base_type
        else:
            raise SyntaxError("Unexpected token while parsing type.")


    def parse_typedef(self):
        """
        Parse a typedef declaration.
        """
        self.match(TokenType.KEYWORD_TYPEDEF)  # Consume the 'typedef' keyword
        aliased_type = self.parse_type()       # Parse the type being aliased
        alias_name = self.match(TokenType.IDENTIFIER)  # Parse the alias name
        self.match(TokenType.DELIM_SEMICOLON)  # Consume the trailing ';'
        
        if not alias_name:
            raise SyntaxError("Expected identifier for typedef alias.")

        return {
            "type": "TypedefDeclaration",
            "aliased_type": aliased_type,
            "alias_name": alias_name.value,
        }


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
        return {"type": "StructDeclaration", "name": identifier.value, "fields": fields}

    @debug
    def parse_compound_statement(self):
        # This is called at the begining of a block statement

        statements = []

        # Following the chain, the key calls here are declarators, and assignment expressions,

        Next = self.match(TokenType.DELIM_LBRACE)
        while Next and not self.peek(TokenType.DELIM_RBRACE):
            
            if self.scan_declare_init():
                statements.append(self.parse_declaration())
            else:
                statements.append(self.parse_statement())

            if Next == self.current_token():
                Next = False
                self.error += 1

        self.match(TokenType.DELIM_RBRACE)
        return {"BlockStatements": statements}

    @debug
    # We know the primary expression, return it or an evaluation
    def parse_primary_expression(self):
        if self.peek(TokenType.DELIM_LPAREN):  # Opening parenthesis
            self.match(TokenType.DELIM_LPAREN)
            expression = self.parse_expression()   # Parse the subexpression
            self.match(TokenType.DELIM_RPAREN)  # Ensure a closing parenthesis exists
            return expression


        prefix = None; postfix = None

        while self.peek(TokenType.OPERATOR_UNARY):
            prefix = self.match(TokenType.OPERATOR_UNARY)

        if self.current_token().value in Operators.Special_Operators.keys():
            prefix = self.match(TokenType.OPERATOR_BINARY)

        if self.peek(TokenType.DELIM_LPAREN, 1):
            # Functioncall
            return self.parse_function_call()
        elif self.peek(TokenType.LITERAL_SPECIAL):
            token = self.match(TokenType.LITERAL_SPECIAL)
        else:
            token = self.match(TokenType.IDENTIFIER)

        if self.peek(TokenType.OPERATOR_UNARY):
            postfix = self.match(TokenType.OPERATOR_UNARY)

        # self.match(TokenType.DELIM_RBRACE)
        # self.match(TokenType.DELIM_SEMICOLON)
        if prefix:
            if prefix and postfix:
                return {"type": "Literal" if token.ofType == TokenType.LITERAL_SPECIAL else "Identifier", "prefix": prefix.value, "postfix": postfix.value, "value": token.value}
            else:
                return {"type": "Literal" if token.ofType == TokenType.LITERAL_SPECIAL else "Identifier", "prefix": prefix.value, "value": token.value}
        if postfix:
            return {"type": "Literal" if token.ofType == TokenType.LITERAL_SPECIAL else "Identifier", "postfix": postfix.value, "value": token.value}
        else:
            return {"type": "Literal" if token.ofType == TokenType.LITERAL_SPECIAL else "Identifier", "value": token.value}

    @debug
    def parse_assignment(self):

        # Add this in later to check we have an identifier, not a var type
        # if self.peek(TokenBase.KEYWORD)

        lhs_token = self.parse_primary_expression();
        assignment_operator = self.match(TokenType.OPERATOR_ASSIGNMENT)
        expression = self.parse_expression()
        self.match(TokenType.DELIM_SEMICOLON)

        return {"type": "Assignment", "left": lhs_token, "operator": assignment_operator.value, "right": expression}

    @debug
    def parse_statement(self):
        """
        Parse an expression statement.
        """

        # An lbrace will enter us into another compound statement (we came from there likely)

        if self.peek(TokenBase.KEYWORD):

            # This is parse selection statement
            if self.peek(TokenType.KEYWORD_IF):
                return self.parse_if_statement()
            # parse iteration statement
            elif self.peek(TokenType.KEYWORD_WHILE):
                return self.parse_while_statement()
            # This one might be special, all others we will be called again within this block
            elif self.peek(TokenType.KEYWORD_RETURN):
                return self.parse_return_statement()
            else:
                return self.parse_declaration()
                raise SyntaxError('unhandled statement type, or a declaration was sent to parse_statement()')
        else:
            if self.scan_declare_init() or self.scan_declaration():
                return self.parse_declaration()
            elif self.lookahead(TokenType.OPERATOR_ASSIGNMENT, TokenType.DELIM_SEMICOLON):
                return self.parse_assignment()
            # parse_primary_expression for function calls
            elif self.lookahead(TokenType.DELIM_LPAREN, TokenType.DELIM_SEMICOLON):
                expression =  self.parse_primary_expression()
                self.match(TokenType.DELIM_SEMICOLON)
                return {"type": "ExpressionStatement", "expression": expression}

            raise

    # def parse_expression(self):

    #     if self.scan_arithmetic():
    #         return self.parse_binary_expression()
    #     else:
    #         return self.parse_primary_expression()


    # @debug
    # def parse_binary_expression(self):

    #     l_operand = self.parse_primary_expression()
    #     operator = self.match(TokenType.OPERATOR_ARITHMETIC)
    #     r_operand = self.parse_expression()

    #     return {"type": "BinaryOperation", "left": l_operand, "operator": operator.value, "right": r_operand}

    @debug
    def parse_expression(self):
        return self.parse_binary_expression(0)  # Starting with lowest precedence

    @debug
    def parse_binary_expression(self, min_precedence):
        # Parse the left-hand operand
        l_operand = self.parse_primary_expression()

        while self.peek(TokenType.OPERATOR_BINARY) and self.current_token().opPrecedence >= min_precedence:
            # Get the current operator and its precedence
            if self.peek(TokenBase.OPERATOR):
                operator_precedence = self.current_token().opPrecedence
            operator = self.match(TokenType.OPERATOR_BINARY)
            
            # Handle right-hand operand with higher precedence
            r_operand = self.parse_binary_expression(operator_precedence + 1)

            # Combine into a binary operation
            l_operand = {
                "type": "BinaryOperation",
                "left": l_operand,
                "operator": operator.value,
                "right": r_operand
            }

        return l_operand


