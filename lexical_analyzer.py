"""
Лексический анализатор для языка Pascal
Вариант 13: Объявление и определение записи (record) в Pascal
"""


class Token:
    """Класс для хранения информации о лексеме"""
    def __init__(self, code, token_type, lexeme, line, start_pos, end_pos):
        self.code = code          # Условный код
        self.token_type = token_type  # Тип лексемы
        self.lexeme = lexeme      # Лексема
        self.line = line          # Номер строки
        self.start_pos = start_pos    # Начальная позиция в строке
        self.end_pos = end_pos        # Конечная позиция в строке
        self.is_error = False     # Флаг ошибки


class LexicalAnalyzer:
    """Лексический анализатор (сканер) для Pascal-подобного синтаксиса"""
    
    # Словарь кодов лексем
    TOKEN_CODES = {
        'KEYWORD_TYPE': 1,         # Ключевое слово type
        'KEYWORD_RECORD': 2,       # Ключевое слово record
        'KEYWORD_END': 3,          # Ключевое слово end
        'IDENTIFIER': 4,           # Идентификатор
        'COLON': 5,                # Двоеточие :
        'SEMICOLON': 6,            # Точка с запятой ;
        'COMMA': 7,                # Запятая ,
        'KEYWORD_REAL': 8,         # Тип данных real
        'KEYWORD_INTEGER': 9,      # Тип данных integer
        'ASSIGN': 10,              # Оператор присваивания :=
        'WHITESPACE': 11,          # Разделитель (пробел)
        'NEWLINE': 12,             # Разделитель (новая строка)
        'ERROR': 99                # Ошибка
    }
    
    # Ключевые слова Pascal
    KEYWORDS = {
        'type', 'record', 'end', 'real', 'integer', 
        'var', 'begin', 'procedure', 'function', 'if', 
        'then', 'else', 'while', 'do', 'for', 'to', 
        'downto', 'array', 'of', 'string', 'boolean'
    }
    
    def __init__(self):
        self.tokens = []
        self.errors = []
    
    def is_letter(self, char):
        """Проверка: буква или подчеркивание"""
        return char.isalpha() or char == '_'
    
    def is_digit(self, char):
        """Проверка: цифра"""
        return char.isdigit()
    
    def is_alphanumeric(self, char):
        """Проверка: буква, цифра или подчеркивание"""
        return self.is_letter(char) or self.is_digit(char)
    
    def analyze(self, text):
        """
        Анализ входного текста и выделение лексем.
        
        Аргументы:
            text: строка с исходным кодом
            
        Возвращает:
            кортеж (tokens, errors)
        """
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
                if char in ' \t':
                    whitespace_start = col
                    while col < len(line) and line[col] in ' \t':
                        col += 1
                    lexeme = line[whitespace_start:col]
                    self.tokens.append(Token(
                        self.TOKEN_CODES['WHITESPACE'],
                        'разделитель (пробел)',
                        lexeme,
                        line_num,
                        whitespace_start + 1,
                        col
                    ))
                    continue

                # Проверка на русские символы (кириллицу)
                if 'а' <= char <= 'я' or 'А' <= char <= 'Я' or char == 'ё' or char == 'Ё':
                    self._add_error(line_num, col + 1, char)
                    col += 1
                    continue

                # Оператор =
                if char == '=':
                    self.tokens.append(Token(
                        self.TOKEN_CODES['ASSIGN'],
                        'Оператор присваивания',
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
                    
                    # Определение типа лексемы
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
                
                # Двоеточие (может быть частью :=)
                if char == ':':
                    if col + 1 < len(line) and line[col + 1] == '=':
                        # Оператор присваивания :=
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
                        # Обычное двоеточие
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
                
                # Недопустимый символ
                self._add_error(line_num, col + 1, char)
                col += 1
            
            # Добавляем маркер конца строки
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
        """Добавление информации об ошибке"""
        error_token = Token(
            self.TOKEN_CODES['ERROR'],
            'ОШИБКА',
            char,
            line,
            pos,
            pos
        )
        error_token.is_error = True
        self.tokens.append(error_token)
        self.errors.append({
            'line': line,
            'position': pos,
            'char': char,
            'message': f'Недопустимый символ: "{char}"'
        })