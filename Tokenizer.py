# Tokenizer.py
# Jan 3, 2025
# Jan 11, 2025 Updated, some cleanup and data veryification
# This file is still in the very early stages of development
# Break a simple c.source code file into tokens
from dataclasses import dataclass, field
from typing import Dict, Optional
import re


from TokenType_placeholder import TokenType, Delimiters, Keywords, Operators
from TokenType_placeholder import TokenBase, DataType
from Parser_placeholder import Parser

from pprint import pprint


# C Source code file
TEST_FILE = 'j:/c_Parser/c_files/decl_test.c'

# Used for token IDs
def get_next_key():
    key = 0
    while True:
        yield key
        key += 1

@dataclass
class Token:
    Id: Dict = field(default_factory=dict)   # Unique identifier for the token
    base: Dict = field(default_factory=dict) # Token base e.g.
    ofType: Dict = field(default_factory=dict) # Specific type (e.g., Keywords)
    value: Dict = field(default_factory=dict) # Value of the token (e.g., 'int')
    line: int = 0
    y1: int = 0
    y2: int = 0

    # The DataType the token refers to, if it has one, else None

    def __str__(self):
        if self.ofType:
            return f'{self.Id:3} {self.base:26} {self.ofType:18} {self.value:18}'
        else:
            return f'{self.Id:3} {self.base:26}{"ofType: None":18}{self.value:18}'


def main():

    # Load our test c source
    code = load_code(TEST_FILE)

    # Build Very Large Regex
    pattern = build_regex()

    # Perform regex on entire file
    match = re.findall(pattern, code, re.DOTALL)

    # Based on our regex, these groups will be filled in with their appropriate members
    match_index_to_base = {
    0: TokenBase.COMMENT_ML, 1: TokenBase.COMMENT_SL, 2: TokenBase.PREPROCESSOR,
    5: TokenBase.LITERAL, 6: TokenBase.WORD,
    7: TokenBase.OPERATOR, 8: TokenBase.DELIM}

    # Build a list of all tokens
    tokens = []
    key_gen = get_next_key()
    # For each token
    for e in match:
        # For each match group, not very efficient
        for k, v in match_index_to_base.items():
            token = {}
            # Each token should have only 1 match besides the whitespace group
            if e[k]:
                assert(token == {}) # Error multiple matches
                # Create a new token to append to our tokens list
                token = Token()
                token.Id = next(key_gen)
                # base is the type of token, LITERAL, DELIM, etc.
                token.base = v
                # match e, token group k
                token.value = e[k]
            if token:
                tokens.append(token)

    # debug print
    for e in tokens:
        print(e)

    # Modifies and prints token data
    # Modification is in place, thus no return.
    modify_tokens_add_ofType_data(tokens)


    parser = Parser(tokens)
    ast = parser.parse_program()
    pprint(ast)



def modify_tokens_add_ofType_data(tokens):

    print('DELIMS:')
    tokens_sublist = [x for x in tokens if x.base == TokenBase.DELIM]
    for token in tokens_sublist:
        if Delimiters.to_name(token.value):
            token.ofType = Delimiters.to_name(token.value)
            print(token)

    print('KEYWORDS:')
    tokens_sublist = [x for x in tokens if x.base == TokenBase.WORD]
    for token in tokens_sublist:
        if token.value in Keywords._mapping:
            token.base = TokenBase.KEYWORD
            token.ofType = Keywords.to_name(token.value)
            if token.ofType == TokenType.KEYWORD_INT:
                token.ofType = TokenType.IDENTIFIER
            elif token.ofType == TokenType.KEYWORD_FLOAT:
                token.ofType = TokenType.IDENTIFIER
            elif token.ofType == TokenType.KEYWORD_CHAR:
                token.ofType = TokenType.IDENTIFIER
            elif token.ofType == TokenType.KEYWORD_VOID:
                token.ofType = TokenType.IDENTIFIER
            print(token)

    print('IDENTIFIERS:')
    tokens_sublist = [x for x in tokens_sublist if x.base == TokenBase.WORD]
    for token in tokens_sublist:
        token.base = TokenBase.IDENTIFIER
        token.ofType = TokenType.IDENTIFIER
        print(token)

    # print('DataTypes (Subset):')
    # tokens_sublist = [x for x in tokens if x.base == TokenBase.KEYWORD]
    # for token in tokens_sublist:
    #     # print(f'testing...', token)
    #     if token.base == TokenBase.KEYWORD:
    #         # print(f'is keyword...', token)
    #         if token.ofType == Keywords.to_name('int'):
    #             token.is_Datatype = DataType.KEYWORD_INT
    #         elif token.ofType == Keywords.to_name('float'):
    #             token.is_Datatype = DataType.KEYWORD_FLOAT
    #         elif token.ofType == Keywords.to_name('char'):
    #             token.is_Datatype = DataType.KEYWORD_CHAR
    #         elif token.ofType == Keywords.to_name('void'):
    #             token.is_Datatype = DataType.KEYWORD_VOID
    #         print(token)


    print('LITERALS:')
    tokens_sublist = [x for x in tokens if x.base == TokenBase.LITERAL]
    for token in tokens_sublist:
        token.ofType = TokenType.LITERAL_SPECIAL
        print(token)

    print('OPERATORS:')
    tokens_sublist = [x for x in tokens if x.base == TokenBase.OPERATOR]
    for token in tokens_sublist:
        if token.value in Operators.Operators:
            token.ofType = Operators.to_type(token.value)
            print(token)
        else:
            token.ofType = None

    print('UNRECOGNIZED OPERATORS:')
    for token in tokens_sublist:
        if token.ofType == None:
            print(token)
    else:
        print('NONE!')


# Import the c.source code, join all lines
def load_code(c_file):
    with open(c_file, 'r') as file:
        lines = file.readlines()

    return ''.join([line for line in lines])


# Build a regex that captures all tokens
def build_regex():

    ml_comment = r"/\*(?:[^\*]|\*[^\/])*\*/" # multiline comment
    comment = r"//[^\n]*"
    directives = r"\s*\#\s*(?:\w+)\b(?:[ \t]+(?:[^\n]*))?"
    numeric_literal = r"(?:0b)?[\d][.\d]?[\d]*"
    string_literal = r"\"(?:[^\"\\]|\\.)*\""
    char_literal = r"\'(?:[^\'\\]|\\.)*\'"
    bool_literal = r"true|false"
    identifier = r"[a-zA-Z_]+[a-zA-Z_\d]*"
    operators = r"[\+\-\*\/\%\=\!\<\>\&\|\^\~\?\:]+"
    delimiters = r"[\{\}\(\)\[\]\,\.\;]"
    return r"("+ml_comment+r")|("+comment+r")|("+directives+r")(\n)|(\n)|("+numeric_literal+r"|"+string_literal+r"|"+char_literal+r"|"+bool_literal+r")|("+identifier+r")|("+operators+r")|("+delimiters+r")"




if __name__ == '__main__':
    main()
