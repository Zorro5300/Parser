from lexical_analyzer import LexicalAnalyzer, Token


class SyntaxError:
    """Класс для хранения информации о синтаксической ошибке"""
    def __init__(self, fragment, line, position, description):
        self.fragment = fragment
        self.line = line
        self.position = position
        self.description = description


class SyntaxAnalyzer:
    """Синтаксический анализатор для объявления record в Pascal"""
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.errors = []
        self.lexical_analyzer = LexicalAnalyzer()
    
    def _get_token(self):
        """Получить текущий значащий токен (без пробелов и новых строк)"""
        while self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            if t.token_type in ['разделитель (пробел)', 'разделитель (новая строка)']:
                self.pos += 1
            elif t.is_error:
                self.pos += 1
            else:
                return t
        return None
    
    def _peek_token(self):
        """Посмотреть следующий значащий токен без перемещения"""
        saved_pos = self.pos
        token = self._get_token()
        self.pos = saved_pos
        return token
    
    def _next(self):
        """Перейти к следующему токену"""
        self.pos += 1
    
    def _get_last_position(self):
        """Позиция последнего значащего токена"""
        pos = self.pos - 1
        while pos >= 0:
            t = self.tokens[pos]
            if t.token_type not in ['разделитель (пробел)', 'разделитель (новая строка)'] and not t.is_error:
                return t.line, t.end_pos + 1
            pos -= 1
        return 1, 1
    
    def _add_error(self, fragment, line, pos, desc):
        """Добавить синтаксическую ошибку"""
        self.errors.append(SyntaxError(fragment, line, pos, desc))
    
    def analyze(self, text):
        """Главный метод анализа"""
        self.errors = []
        
        if not text or not text.strip():
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return False, self.errors
        
        all_tokens, lex_errors = self.lexical_analyzer.analyze(text)
        self.tokens = all_tokens
        self.pos = 0
        
        self.parse_Z()
        
        success = len(self.errors) == 0
        return success, self.errors
    
    def parse_Z(self):
        # проверка на лексику
        for t in self.tokens:
            if t.is_error:
                self._add_error(t.lexeme, t.line, t.start_pos, f"Лексическая ошибка: недопустимы символ '{t.lexeme}'")
                #return
        """
        Z → "type" ID "=" "record" FIELD_LIST "end" ";"
        """
        token = self._get_token()
        
        if token is None:
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return
        
        # 1. Проверка "type"
        if token.lexeme != 'type':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'type', получено '{token.lexeme}'"
            )
        else:
            self._next()

        # 2. Идентификатор (имя типа)
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался идентификатор (имя типа)")
        elif token.token_type != 'идентификатор':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался идентификатор, получено '{token.lexeme}'"
            )
        else:
            self._next()
        
        # 3. Оператор '='
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался оператор '='")
        elif token.lexeme != '=':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался оператор '=', получено '{token.lexeme}'"
            )
        else:
            self._next()
        
        # 4. Ключевое слово 'record'
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось ключевое слово 'record'")        
        elif token.lexeme != 'record':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'record', получено '{token.lexeme}'"
            )
            self._next()
        else:
            self._next()
        # 7    
            self.parse_FIELD_LIST()
            
            token = self._get_token()
            if token and token.lexeme == ';':
                self._next()
        
        # 7 Ключевое слово end
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось ключевое слово 'end' для завершения записи")
        elif token.lexeme != 'end':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ключевое слово 'end', получено '{token.lexeme}'"
            )
        else:
            self._next()
        
        # 8. Точка с запятой ';' после end
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась ';' после 'end'")
        elif token.lexeme != ';':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалась ';', получено '{token.lexeme}'"
            )
        else:
            self._next()
        
        # Проверка на лишние токены
        token = self._get_token()
        if token is not None:
            if token.lexeme != 'end' and token.token_type != 'разделитель (новая строка)':
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Неожиданный токен '{token.lexeme}' после конца объявления"
                    )

    def _skip_to_end(self):
        """Пропустить все токены до end"""
        while True:
            token = self._get_token()
            if token is None:
                break
            if token.lexeme == 'end':
                self._next()
                break
    
    def parse_FIELD_LIST(self):
        """
        FIELD_LIST → ( FIELD_DEF ";" )* FIELD_DEF
        """
        fields_parsed = False

        # Парсим
        while True:
            token = self._peek_token()
            
            if token is None:
                break
            
            if token.lexeme == 'end':
                    break
            if not self.parse_FIELD_DEF():
                self._next()
                continue

            fields_parsed = True

            # После поля обязательно ;
            token = self._get_token()
            if token is None:
                self._add_error("", 1, 1, "Ожидалась ';' после определения поля")
                break

            if token.lexeme != ';':
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидалась ';' после определения поля, получено '{token.lexeme}'"
                )
                continue
            self._next()

            #Если не было ни одного поля то ошибка
            if not fields_parsed:
                token = self._get_token()
                if token and token.lexeme != 'end':
                    self._add_error("", 1, 1, "Ожидалось определение поля")
    
    def parse_FIELD_DEF(self):
        """
        FIELD_DEF → ID_LIST ":" TYPE_NAME
        ID_LIST → ID ( "," ID )*
        TYPE_NAME → "real" | "integer"
        """
        # Разбор списка идентификаторов
        saved_pos = self.pos
        identifiers = []
        
        # Первый идентификатор
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался идентификатор в определении поля")
            return False
        
        if token.token_type == 'идентификатор':
            identifiers.append(token.lexeme)
            self._next()
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался идентификатор, получено '{token.lexeme}'"
            )
            return False
        
        # Дополнительные идентификаторы (через запятую)
        while True:
            token = self._get_token()
            if token is None:
                break
            
            if token.lexeme == ',':
                self._next()
                token = self._get_token()
                if token and token.token_type == 'идентификатор':
                    identifiers.append(token.lexeme)
                    self._next()
                else:
                    self._add_error(
                        token.lexeme if token else "", 
                        token.line if token else 1, 
                        token.start_pos if token else 1,
                        "Ожидался идентификатор после ','"
                    )
                    return False
            else:
                break
        
        # Проверка двоеточия
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, f"Ожидалось ':' после списка полей [{', '.join(identifiers)}]")
            return False
        
        if token.lexeme != ':':
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидалось ':', получено '{token.lexeme}'"
            )
            return False
        
        self._next()
        
        # Проверка типа (real или integer)
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, f"Ожидался тип данных (real/integer) для поля {identifiers[0]}")
            return False
        
        if token.lexeme in ('real', 'integer'):
            self._next()
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался тип 'real' или 'integer', получено '{token.lexeme}'"
            )
            return False
        
        return True