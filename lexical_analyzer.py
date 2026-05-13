"""
Лексический анализатор для языка Pascal
Вариант 13: Объявление и определение записи (record) в Pascal
"""


class Token:
    """Класс для хранения информации о лексеме"""
    def __init__(self, code, token_type, lexeme, line, start_pos, end_pos):
        self.code = code
        self.token_type = token_type
        self.lexeme = lexeme
        self.line = line
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_error = False


class LexicalAnalyzer:
    """Лексический анализатор (сканер) для Pascal-подобного синтаксиса"""
    
    TOKEN_CODES = {
        'KEYWORD_TYPE': 1,
        'KEYWORD_RECORD': 2,
        'KEYWORD_END': 3,
        'IDENTIFIER': 4,
        'COLON': 5,
        'SEMICOLON': 6,
        'COMMA': 7,
        'KEYWORD_REAL': 8,
        'KEYWORD_INTEGER': 9,
        'KEYWORD_STRING': 10,
        'ASSIGN': 11,
        'WHITESPACE': 12,
        'NEWLINE': 13,
        'ERROR': 99
    }
    
    KEYWORDS = {
        'type', 'record', 'end', 'real', 'integer', 'string'
    }
    
    def __init__(self):
        self.tokens = []
        self.errors = []
    
    def is_letter(self, char):
        return ('a' <= char <= 'z') or ('A' <= char <= 'Z') or char == '_'
    
    def is_digit(self, char):
        return '0' <= char <= '9'
    
    def is_alphanumeric(self, char):
        return self.is_letter(char) or self.is_digit(char)
    
    def analyze(self, text):
        self.tokens = []
        self.errors = []
        
        if not text:
            return self.tokens, self.errors
        
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            col = 0
            while col < len(line):
                char = line[col]
                
                # Пропуск пробелов
                if char == ' ' or char == '\t':
                    whitespace_start = col
                    while col < len(line) and (line[col] == ' ' or line[col] == '\t'):
                        col += 1
                    self.tokens.append(Token(
                        self.TOKEN_CODES['WHITESPACE'],
                        'разделитель (пробел)',
                        ' ',
                        line_num,
                        whitespace_start + 1,
                        col
                    ))
                    continue
                
                # Оператор =
                if char == '=':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['ASSIGN'],
                        'оператор присваивания',
                        '=',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Идентификаторы и ключевые слова
                if self.is_letter(char):
                    start = col
                    while col < len(line) and self.is_alphanumeric(line[col]):
                        col += 1
                    lexeme = line[start:col]
                    
                    if lexeme == 'type':
                        token_code = self.TOKEN_CODES['KEYWORD_TYPE']
                        token_type = 'ключевое слово (type)'
                    elif lexeme == 'record':
                        token_code = self.TOKEN_CODES['KEYWORD_RECORD']
                        token_type = 'ключевое слово (record)'
                    elif lexeme == 'end':
                        token_code = self.TOKEN_CODES['KEYWORD_END']
                        token_type = 'ключевое слово (end)'
                    elif lexeme == 'real':
                        token_code = self.TOKEN_CODES['KEYWORD_REAL']
                        token_type = 'тип данных (real)'
                    elif lexeme == 'integer':
                        token_code = self.TOKEN_CODES['KEYWORD_INTEGER']
                        token_type = 'тип данных (integer)'
                    elif lexeme == 'string':
                        token_code = self.TOKEN_CODES['KEYWORD_STRING']
                        token_type = 'тип данных (string)'
                    else:
                        token_code = self.TOKEN_CODES['IDENTIFIER']
                        token_type = 'идентификатор'
                    
                    self.tokens.append(Token(
                        token_code,
                        token_type,
                        lexeme,
                        line_num,
                        start + 1,
                        col
                    ))
                    continue
                
                # Двоеточие
                if char == ':':
                    if col + 1 < len(line) and line[col + 1] == '=':
                        self.tokens.append(Token(
                            self.TOKEN_CODES['ASSIGN'],
                            'оператор присваивания',
                            ':=',
                            line_num,
                            col + 1,
                            col + 2
                        ))
                        col += 2
                    else:
                        self.tokens.append(Token(
                            self.TOKEN_CODES['COLON'],
                            'разделитель (двоеточие)',
                            ':',
                            line_num,
                            col + 1,
                            col + 1
                        ))
                        col += 1
                    continue
                
                # Точка с запятой
                if char == ';':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['SEMICOLON'],
                        'разделитель (точка с запятой)',
                        ';',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Запятая
                if char == ',':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['COMMA'],
                        'разделитель (запятая)',
                        ',',
                        line_num,
                        col + 1,
                        col + 1
                    ))
                    col += 1
                    continue
                
                # Русские символы и другие недопустимые - просто пропускаем с ошибкой
                self._add_error(line_num, col + 1, char)
                col += 1
            
            # Маркер конца строки
            if line_num < len(lines):
                self.tokens.append(Token(
                    self.TOKEN_CODES['NEWLINE'],
                    'разделитель (новая строка)',
                    '\\n',
                    line_num,
                    len(line) + 1,
                    len(line) + 1
                ))
        
        return self.tokens, self.errors
    
    def _add_error(self, line, pos, char):
        # Добавляем ошибку в список, НО НЕ создаем токен!
        self.errors.append({
            'line': line,
            'position': pos,
            'char': char,
            'message': f'Недопустимый символ: "{char}"'
        })