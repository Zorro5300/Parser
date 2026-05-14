import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Token:
    """Класс лексемы"""
    code: int
    token_type: str
    lexeme: str
    line: int
    start_pos: int
    end_pos: int
    is_error: bool = False


class LexicalAnalyzer:
    """Лексический анализатор для Pascal record"""
    
    # Коды лексем
    KEYWORD_TYPE = 1
    KEYWORD_RECORD = 2
    KEYWORD_END = 3
    KEYWORD_REAL = 4
    KEYWORD_INTEGER = 5
    KEYWORD_BOOLEAN = 6
    KEYWORD_CHAR = 7
    IDENTIFIER = 10
    ASSIGN_OP = 11  # =
    COLON = 12      # :
    SEMICOLON = 13  # ;
    COMMA = 14      # ,
    NEWLINE = 20
    WHITESPACE = 21
    UNKNOWN = 99
    ERROR = 100
    
    # Типы лексем
    TYPE_NAMES = {
        KEYWORD_TYPE: "ключевое слово 'type'",
        KEYWORD_RECORD: "ключевое слово 'record'",
        KEYWORD_END: "ключевое слово 'end'",
        KEYWORD_REAL: "ключевое слово 'real'",
        KEYWORD_INTEGER: "ключевое слово 'integer'",
        KEYWORD_BOOLEAN: "ключевое слово 'boolean'",
        KEYWORD_CHAR: "ключевое слово 'char'",
        IDENTIFIER: "идентификатор",
        ASSIGN_OP: "оператор присваивания '='",
        COLON: "двоеточие ':'",
        SEMICOLON: "точка с запятой ';'",
        COMMA: "запятая ','",
        NEWLINE: "разделитель (новая строка)",
        WHITESPACE: "разделитель (пробел)",
        UNKNOWN: "неизвестный символ",
        ERROR: "ошибка"
    }
    
    # Ключевые слова
    KEYWORDS = {
        'type': KEYWORD_TYPE,
        'record': KEYWORD_RECORD,
        'end': KEYWORD_END,
        'real': KEYWORD_REAL,
        'integer': KEYWORD_INTEGER,
        'boolean': KEYWORD_BOOLEAN,
        'char': KEYWORD_CHAR
    }
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.errors: List[dict] = []
        self.line = 1
        self.pos = 1
        self.text = ""
        self.length = 0
    
    def analyze(self, text: str) -> Tuple[List[Token], List[dict]]:
        """Основной метод анализа"""
        self.tokens = []
        self.errors = []
        self.text = text
        self.length = len(text)
        self.line = 1
        self.pos = 1
        
        i = 0
        while i < self.length:
            self.pos = i + 1
            ch = text[i]
            
            # Пропускаем пробелы
            if ch == ' ':
                self.tokens.append(Token(
                    self.WHITESPACE, self.TYPE_NAMES[self.WHITESPACE], ' ', self.line, i + 1, i + 1
                ))
                i += 1
                continue
            
            # Новая строка
            if ch == '\n':
                self.tokens.append(Token(
                    self.NEWLINE, self.TYPE_NAMES[self.NEWLINE], '\\n', self.line, i + 1, i + 1
                ))
                self.line += 1
                i += 1
                continue
            
            # Односимвольные операторы и разделители
            if ch == '=':
                self.tokens.append(Token(
                    self.ASSIGN_OP, self.TYPE_NAMES[self.ASSIGN_OP], '=', self.line, i + 1, i + 1
                ))
                i += 1
                continue
            
            if ch == ':':
                self.tokens.append(Token(
                    self.COLON, self.TYPE_NAMES[self.COLON], ':', self.line, i + 1, i + 1
                ))
                i += 1
                continue
            
            if ch == ';':
                self.tokens.append(Token(
                    self.SEMICOLON, self.TYPE_NAMES[self.SEMICOLON], ';', self.line, i + 1, i + 1
                ))
                i += 1
                continue
            
            if ch == ',':
                self.tokens.append(Token(
                    self.COMMA, self.TYPE_NAMES[self.COMMA], ',', self.line, i + 1, i + 1
                ))
                i += 1
                continue
            
            # Идентификаторы и ключевые слова
            if self._is_letter(ch):
                start = i
                while i < self.length and (self._is_letter(text[i]) or self._is_digit(text[i]) or text[i] == '_'):
                    i += 1
                lexeme = text[start:i]
                
                # Проверка на ключевое слово
                if lexeme.lower() in self.KEYWORDS:
                    code = self.KEYWORDS[lexeme.lower()]
                    self.tokens.append(Token(
                        code, self.TYPE_NAMES[code], lexeme, self.line, start + 1, i
                    ))
                else:
                    self.tokens.append(Token(
                        self.IDENTIFIER, self.TYPE_NAMES[self.IDENTIFIER], lexeme, self.line, start + 1, i
                    ))
                continue
            
            # Числа (допустимы в идентификаторах, но отдельно не используются в грамматике)
            if self._is_digit(ch):
                start = i
                while i < self.length and self._is_digit(text[i]):
                    i += 1
                lexeme = text[start:i]
                # Цифры могут быть частью идентификатора, но если они одни - это ошибка?
                # По грамматике цифры только в составе идентификатора
                self.errors.append({
                    'message': f"Некорректный символ: цифра '{lexeme}' не может быть отдельной лексемой",
                    'line': self.line,
                    'position': start + 1,
                    'char': lexeme
                })
                self.tokens.append(Token(
                    self.ERROR, "ОШИБКА", lexeme, self.line, start + 1, i, is_error=True
                ))
                continue
            
            # Обработка ошибок: любой другой символ (включая $)
            if not (ch == ' ' or ch == '\n' or self._is_letter(ch) or self._is_digit(ch) or 
                    ch in '=:;, '):
                error_char = ch
                start = i
                i += 1
                # Собираем последовательность недопустимых символов как одну ошибку
                while i < self.length and not (self._is_letter(text[i]) or self._is_digit(text[i]) or 
                                                text[i] in '=:;, \n' or self._is_letter(text[i])):
                    error_char += text[i]
                    i += 1
                
                self.errors.append({
                    'message': f"Недопустимый символ: '{error_char}'",
                    'line': self.line,
                    'position': start + 1,
                    'char': error_char
                })
                self.tokens.append(Token(
                    self.ERROR, "ОШИБКА", error_char, self.line, start + 1, i, is_error=True
                ))
                continue
        
        return self.tokens, self.errors
    
    def _is_letter(self, ch: str) -> bool:
        """Проверка, является ли символ буквой"""
        return ('a' <= ch <= 'z') or ('A' <= ch <= 'Z')
    
    def _is_digit(self, ch: str) -> bool:
        """Проверка, является ли символ цифрой"""
        return '0' <= ch <= '9'


# Для тестирования
if __name__ == "__main__":
    analyzer = LexicalAnalyzer()
    
    test_text = """type complex = record
    re, im: real;
end;"""
    
    tokens, errors = analyzer.analyze(test_text)
    
    print("=== ТОКЕНЫ ===")
    for token in tokens:
        if token.token_type not in ['разделитель (пробел)', 'разделитель (новая строка)']:
            print(f"{token.code:3} | {token.token_type:25} | '{token.lexeme}' | строка {token.line}, поз. {token.start_pos}-{token.end_pos}")
    
    print("\n=== ОШИБКИ ===")
    for err in errors:
        print(f"  {err['message']} (строка {err['line']}, позиция {err['position']})")