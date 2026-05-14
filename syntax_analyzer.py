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
        self.in_error = False  # Флаг: находимся ли в режиме восстановления после ошибки
    
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
        """Добавить синтаксическую ошибку (только если не в режиме восстановления)"""
        # Добавляем ошибку, даже если in_error True, но только если это первая в текущем месте
        # Для простоты добавляем всегда, но флаг in_error будем сбрасывать после синхронизации
        self.errors.append(SyntaxError(fragment, line, pos, desc))
    
    def _sync_to(self, *sync_tokens):
        """
        Пропускать токены до тех пор, пока не встретится один из sync_tokens
        Возвращает True, если синхронизация удалась, False если достигнут конец
        """
        while True:
            token = self._get_token()
            if token is None:
                return False
            if token.lexeme in sync_tokens:
                return True
            # Пропускаем текущий токен
            self.pos += 1
    
    def analyze(self, text):
        """Главный метод анализа"""
        self.errors = []
        self.in_error = False
        
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
        """
        Z → "type" ID "=" "record" FIELD_LIST "end" ";"
        """
        # 1. Проверка "type"
        token = self._get_token()
        if token is None:
            self._add_error("", 1, 1, "Пустая строка для анализа")
            return

        import re

        def is_type_misspelling(word):
            """Проверяет, является ли слово опечаткой 'type'"""
            word_lower = word.lower()
            
            # Паттерны для распространенных опечаток 'type'
            patterns = [
                r'^t{1,2}y?p?e?$',      # t, tt, ty, tp, te, tty, typ, tpe, tye
                r'^y?p?e?$',             # y, p, e, ye, pe, yp, ype
                r'^t{1,2}y?p?$',         # typ, tpy, ttyp
                r'^[tT][yY][pP][eE]?$',  # type без последней буквы
                r'^[tT][yY][pP0-9]',     # tyр, ty5
                r'^[tT][yY][^a-z]{0,2}[eE]',  # ty$pe, ty@pe
            ]
            
            for pattern in patterns:
                if re.match(pattern, word_lower):
                    return True
            
            # Проверка на количество совпадающих букв
            target = 'type'
            matches = sum(1 for a, b in zip(word_lower, target) if a == b)
            if len(word_lower) >= 3 and matches >= 2:
                return True
            
            return False

        if token.lexeme != 'type':
            if is_type_misspelling(token.lexeme):
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ошибка в ключевом слове: '{token.lexeme}' - возможно, вы хотели написать 'type'"
                )
            else:
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидалось ключевое слово 'type', получено '{token.lexeme}'"
                )
            
            if not self._sync_to('record', 'real', 'end'):
                return
        else:
            self._next()

        # 2. Идентификатор (имя типа) с проверкой на похожие варианты
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался идентификатор (имя типа)")
            return

        def is_similar_to_identifier(word):
            """Проверяет, похоже ли слово на идентификатор (начинается с буквы, содержит буквы/цифры/_)"""
            if not word:
                return False
            
            # Идентификатор должен начинаться с буквы
            if word[0].isalpha():
                return True
            
            # Если начинается с цифры или спецсимвола, но похож на слово
            # Например: "1d", "id123", "_name"
            if len(word) > 1 and (word[1:].isalnum() or '_' in word):
                return True
            
            return False

        if token.token_type != 'идентификатор':
            if is_similar_to_identifier(token.lexeme):
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ошибка в идентификаторе: '{token.lexeme}' - идентификатор должен начинаться с буквы и содержать только буквы, цифры и '_'"
                )
            else:
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидался идентификатор, получено '{token.lexeme}'"
                )
            # Не делаем синхронизацию здесь, просто пропускаем и продолжаем
            self._next()
        else:
            self._next()

        # 3. Оператор '=' с проверкой опечаток
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидался оператор '='")
            return

        def is_similar_to_equals(word):
            """Проверяет, похоже ли слово на оператор '='"""
            word_lower = word.lower()
            
            # Похожие символы и последовательности
            similar_patterns = [
                r'^==$',        # == (как в C/Java)
                r'^:=?$',       # : или := (Pascal присваивание)
                r'^-\s*>$',     # -> (стрелка)
                r'^=+$',        # ==, === и т.д.
                r'^≈$',         # приблизительно равно
                r'^≠$',         # не равно
                r'^<=$',        # <= (меньше или равно)
                r'^>=$',        # >= (больше или равно)
                r'^<-$',        # <- (стрелка)
            ]
            
            for pattern in similar_patterns:
                if re.match(pattern, word_lower):
                    return True
            
            # Если содержит знак равно
            if '=' in word:
                return True
            
            return False

        if token.lexeme != '=':
            if is_similar_to_equals(token.lexeme):
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ошибка в операторе: '{token.lexeme}' - возможно, вы хотели написать '='"
                )
            else:
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидался оператор '=', получено '{token.lexeme}'"
                )
            # Синхронизация: ищем 'record'
            if not self._sync_to('record'):
                return
        else:
            self._next()

        # 4. Ключевое слово 'record' с проверкой опечаток
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось ключевое слово 'record'")
            return

        def is_similar_to_record(word):
            """Проверяет, похоже ли слово на 'record' с возможными опечатками"""
            word_lower = word.lower()
            target = 'record'
            
            # Точное совпадение
            if word_lower == target:
                return True
            
            # Проверка на опечатки (аналогично type)
            if abs(len(word_lower) - len(target)) == 1:
                # Пропущена буква
                for i in range(len(target)):
                    if word_lower == target[:i] + target[i+1:]:
                        return True
                # Лишняя буква
                for i in range(len(word_lower)):
                    if word_lower[:i] + word_lower[i+1:] == target:
                        return True
            
            # Замена букв
            if len(word_lower) == len(target):
                diff_count = sum(1 for a, b in zip(word_lower, target) if a != b)
                if 1 <= diff_count <= 2:
                    return True
            
            # Перестановка букв
            if len(word_lower) == len(target):
                for i in range(len(word_lower) - 1):
                    swapped = list(word_lower)
                    swapped[i], swapped[i+1] = swapped[i+1], swapped[i]
                    if ''.join(swapped) == target:
                        return True
            
            # Распространенные опечатки
            common_misspellings = ['recrd', 'rcord', 'recordd', 'rekord', 'recod', 'recoed']
            if word_lower in common_misspellings:
                return True
            
            # Проверка на похожие символы
            if len(word_lower) >= 4:
                matches = sum(1 for a, b in zip(word_lower[:4], target[:4]) if a == b)
                if matches >= 3:
                    return True
            
            return False

        if token.lexeme != 'record':
            if is_similar_to_record(token.lexeme):
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ошибка в ключевом слове: '{token.lexeme}' - возможно, вы хотели написать 'record'"
                )
            else:
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидалось ключевое слово 'record', получено '{token.lexeme}'"
                )
            # Синхронизация: ищем 'end' или поле (идентификатор)
            if not self._sync_to('end', 'record'):
                return
            # Если нашли 'record' — съедаем его
            if token.lexeme == 'record':
                self._next()
        else:
            self._next()

        # 5. Разбор списка полей
        self.parse_FIELD_LIST()

        # 6. Ключевое слово 'end' с проверкой опечаток
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалось ключевое слово 'end' для завершения записи")
            return

        def is_similar_to_end(word):
            """Проверяет, похоже ли слово на 'end' с возможными опечатками"""
            word_lower = word.lower()
            target = 'end'
            
            # Точное совпадение
            if word_lower == target:
                return True
            
            # Проверка на опечатки
            if abs(len(word_lower) - len(target)) == 1:
                for i in range(len(target)):
                    if word_lower == target[:i] + target[i+1:]:
                        return True
                for i in range(len(word_lower)):
                    if word_lower[:i] + word_lower[i+1:] == target:
                        return True
            
            # Замена букв
            if len(word_lower) == len(target):
                diff_count = sum(1 for a, b in zip(word_lower, target) if a != b)
                if diff_count == 1:
                    return True
            
            # Перестановка букв
            if word_lower in ['edn', 'ned']:
                return True
            
            # Распространенные опечатки
            common_misspellings = ['endd', 'eend', 'and', 'ent', 'nd', 'ennd']
            if word_lower in common_misspellings:
                return True
            
            return False

        if token.lexeme != 'end':
            if is_similar_to_end(token.lexeme):
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ошибка в ключевом слове: '{token.lexeme}' - возможно, вы хотели написать 'end'"
                )
            else:
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидалось ключевое слово 'end', получено '{token.lexeme}'"
                )
            # Синхронизация: ищем ';' или конец
            self._sync_to(';')
        else:
            self._next()

        # 7. Точка с запятой ';' после end с проверкой опечаток
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, "Ожидалась ';' после 'end'")
            return

        def is_similar_to_semicolon(word):
            """Проверяет, похоже ли слово на точку с запятой ';'"""
            # Похожие разделители
            similar = [',', '.', ':', ';;', '；', '; ', ' ;']
            if word in similar:
                return True
            
            # Если содержит точку с запятой
            if ';' in word:
                return True
            
            return False

        if token.lexeme != ';':
            if is_similar_to_semicolon(token.lexeme):
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ошибка в разделителе: '{token.lexeme}' - возможно, вы хотели написать ';'"
                )
            else:
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидалась ';', получено '{token.lexeme}'"
                )
            # Не синхронизируем, просто завершаем
        else:
            self._next()

        # Проверка на лишние токены (необязательно)
        token = self._get_token()
        if token is not None:
            if token.lexeme != 'end' and token.token_type != 'разделитель (новая строка)':
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Неожиданный токен '{token.lexeme}' после конца объявления"
                )
    
    def parse_FIELD_LIST(self):
        """
        FIELD_LIST → ( FIELD_DEF ";" )* FIELD_DEF
        """
        while True:
            token = self._peek_token()
            if token is None:
                break
            if token.lexeme == 'end':
                break

            # Пытаемся разобрать поле
            if not self.parse_FIELD_DEF():
                # Не удалось разобрать поле – пропускаем токен и продолжаем
                self._next()
                continue

            # После поля обязательно должна быть ';'
            token = self._get_token()
            if token is None:
                line, pos = self._get_last_position()
                self._add_error("", line, pos, "Ожидалась ';' после определения поля, но достигнут конец файла")
                break

            if token.lexeme != ';':
                # Ошибка: пропущена ';'
                self._add_error(
                    token.lexeme, token.line, token.start_pos,
                    f"Ожидалась ';' после определения поля, получено '{token.lexeme}'"
                )
                # Пропускаем этот ошибочный токен
                self._next()
                # Не требуем ';' – продолжаем разбор следующего поля
                continue

            # Если ';' есть – проглатываем её
            self._next()
    
    def parse_FIELD_DEF(self):
        """
        FIELD_DEF → ID_LIST ":" TYPE_NAME
        ID_LIST → ID ( "," ID )*
        TYPE_NAME → "real" | "integer" | "string"
        """
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
        
        # Проверка типа
        token = self._get_token()
        if token is None:
            line, pos = self._get_last_position()
            self._add_error("", line, pos, f"Ожидался тип данных (real/integer/string) для поля {identifiers[0]}")
            return False
        
        if token.lexeme in ('real', 'integer', 'string'):
            self._next()
        else:
            self._add_error(
                token.lexeme, token.line, token.start_pos,
                f"Ожидался тип 'real', 'integer' или 'string', получено '{token.lexeme}'"
            )
            return False
        
        return True