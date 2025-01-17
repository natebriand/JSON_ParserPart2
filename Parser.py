import os

# Class to represent types of tokens
class TokenType:
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    FALSE = 'FALSE'
    TRUE = 'TRUE'
    NULL = 'NULL'
    LEFTCURLY = 'LEFTCURLY'
    RIGHTCURLY = 'RIGHTCURLY'
    LEFTSQUARE = 'LEFTSQUARE'
    RIGHTSQUARE = 'RIGHTSQUARE'
    COMMA = 'COMMA'
    COLON = 'COLON'
    EOF = 'EOF'

# Class to represent a token itself, with a type and value
class Token:
    def __init__(self, type_, value=None, line_number=None):
        self.type = type_
        self.value = value
        self.line_number = line_number  # used for error handling

# Class that represents the nodes in the parse tree, each token we will define a node
class Node:
    def __init__(self, label=None):
        self.label = label
        self.children = []  # its children will be JSON keys and values

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, depth=0, output_file = None):
        indent = " " * depth
        label = self.label if self.label else "(none)"
        output_file.write(f"{indent}{label}\n")
        for child in self.children:
            child.print_tree(depth + 4, output_file)

# A Class used to extract all the tokens from a txt file of token streams, and parse
# them according to the respectful grammar
class ExtractTokensLexer:
    def __init__(self, fileName):
        self.tokens = []  # storing the tokens we get
        self.get_tokens(fileName)  # calls the function to get the tokens
        self.current_token_index = 0  # index to track the current token within the parser

    # goes line by line calling the token_from_line method to get each token
    def get_tokens(self, file_name):
        with open(file_name, 'r') as input_file:
            for line_number, line in enumerate(input_file, start=1):
                line = line.strip()
                token = self.token_from_line(line, line_number)
                if token is not None:
                    self.tokens.append(token)

    def token_from_line(self, line, line_number):
        # removing <, >, and spaces to manipulate easier
        line = line.strip()
        line = line.lstrip("<")
        line = line.rstrip(">")
        line = line.replace(" ", "")
        # get token type and token value
        split = line.split(",", 1)  # limit split to one, so it doesn't split the comma if it's a value
        token_type = split[0]
        token_value = split[1]
        if token_type in vars(TokenType).values():  # make sure it's a respected type
            return Token(token_type, token_value, line_number)   # return a new token based on the type and value
        else:
            return None
    # gets the next token from the list
    def get_next_token(self):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        else:
            # Returns EOF token if no more tokens are left
            return Token(TokenType.EOF)


# class that will parse tokens into a parse tree
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer  # we created a new lexer called ExtractTokensLexer
        self.current_token = None
        self.errors = []

    def get_next_token(self):
        # gets the next token from our txt input of tokens
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        """Consumes a token if it matches the expected type."""
        if self.current_token.type == token_type:
            self.get_next_token()
        else:
            # this means there was a syntactic error as the wrong next token was encountered,
            # this is the start of our panic mode recovery
            self.errors.append(f"Syntax error at line {self.current_token.line_number} "
                               f"Expected token {token_type}, got {self.current_token.type}")
            self.current_token = Token(TokenType.EOF)

    def parse(self):
        """Starts the parsing process by fetching the first token and
        calling the first grammar rule."""
        self.get_next_token()
        return self.object()


    """START OF PARSING GRAMMAR RULES"""

    def object(self):
        """Parses the object grammar rule: object  → '{' items '}'"""
        if self.current_token.type == TokenType.EOF:
            return None
        node = Node(label="object:")  # node for the opening of an object
        self.eat(TokenType.LEFTCURLY)
        if self.current_token.type != TokenType.RIGHTCURLY:  # if not an end curly brace, must be items in the object
            items = self.contents()
            if items:
                node.add_child(items)  # call the items function, parsing whats inside the object
        self.eat(TokenType.RIGHTCURLY)
        return node

    def contents(self):
        """Parses the contents grammar rule: contents → pair (',' pair)*
           Note that the left soft brackets are not part of the grammar, and are not terminals.
           They're only for the purpose of representation"""
        if self.current_token.type == TokenType.EOF:
            return None
        node = Node(label="Contents: ")  # creating the node that is the contents of the object
        pair_node = self.pair()  # getting the node that is the pair inside the object (key: value)
        node.add_child(pair_node)
        while self.current_token.type == TokenType.COMMA:  # if more commas come after each pair, we keep adding pairs
            self.eat(TokenType.COMMA)                      # this is how we represent kleen-*
            pair_node = self.pair()
            if pair_node:
                node.add_child(pair_node)
        return node

    def pair(self):
        """Parses the pair grammar rule: pair → id ':' value"""
        """The pair node will have a child which is the key's value"""
        if self.current_token.type == TokenType.EOF:
            return None
        label = self.current_token.value
        node = Node(label=f"key: {label}")
        self.eat(TokenType.STRING)
        self.eat(TokenType.COLON)
        value_node = self.value()
        if value_node:
            node.add_child(value_node)  # Every key has a value to go along with it
        return node

    def value(self):
        """Parses the value grammar rule: value → STRING | NUMBER | 'true' | 'false' | 'null' | object | array"""
        if self.current_token.type == TokenType.EOF:
            return None
        if self.current_token.type == TokenType.STRING:
            label = self.current_token.value
            self.eat(TokenType.STRING)
            return Node(label=f"String: {label}")
        elif self.current_token.type == TokenType.NUMBER:
            label = self.current_token.value
            self.eat(TokenType.NUMBER)
            return Node(label=f"Number: {label}")
        elif self.current_token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE)
            return Node(label="Boolean: true")
        elif self.current_token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE)
            return Node(label="Boolean: false")
        elif self.current_token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            return Node(label="Null: null")
        elif self.current_token.type == TokenType.LEFTSQUARE:
            return self.list()
        elif self.current_token.type == TokenType.LEFTCURLY:
            return self.object()
        else:
            self.current_token = Token(TokenType.EOF)
            return None


    def list(self):
        """Parses the list grammar rule: list → '[' elements ']'"""
        if self.current_token.type == TokenType.EOF:
            return None
        node = Node(label="List: ")  # node for the opening of a list
        self.eat(TokenType.LEFTSQUARE)
        if self.current_token.type != TokenType.RIGHTSQUARE:  # if not an end square bracket, must be items in the list
            item = self.items()
            if item:
                node.add_child(item)
        self.eat(TokenType.RIGHTSQUARE)
        return node

    def items(self):
        """Parses the item grammar rule: item → value (',' value)*"""
        if self.current_token.type == TokenType.EOF:
            return None
        node = Node(label="Elements: ")
        item_node = self.value()
        if item_node:
            node.add_child(item_node)  # we know there's at least one item in the array, this adds it
        while self.current_token.type == TokenType.COMMA:  # loop keeps checking for list items and adding them as
            self.eat(TokenType.COMMA)                      # a child of the element node
            item_node = self.value()
            if item_node:
                node.add_child(item_node)
        return node

    """END OF PARSING GRAMMAR RULES"""


# function that runs test files through the parser
def run_test_files(input_folder='input_folder', output_folder='output_folder'):
    if not os.path.exists(input_folder):  # check if folder exists
        print("Input folder not found")
        return
    if not os.path.exists(output_folder):  # check if folder exists
        print("Output folder not found")
        return

    for i in range(1, 11):
        # get names of files, input01.txt, input02.txt, etc
        input_file_name = os.path.join(input_folder, f"input{i:02d}.txt")
        output_file_name = os.path.join(output_folder, f"output{i:02d}.txt")

        lexer = ExtractTokensLexer(input_file_name)  # create lexer to get the tokens
        parser = Parser(lexer)  # parse the tokens

        with open(output_file_name, 'w') as file:
            tree = parser.parse()
            if tree:
                tree.print_tree(output_file=file)  # print parse tree to the file
            if parser.errors:
                file.write("\n")
                file.write(f"{parser.errors[0]}\n")  # if errors, print them to the file

if __name__ == "__main__":
    run_test_files()
