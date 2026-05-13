import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QMenuBar, QMenu, QToolBar,
    QStatusBar, QSplitter, QFileDialog, QMessageBox, QDialog,
    QVBoxLayout, QDialogButtonBox, QLabel, QWidget, QStyle,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QHBoxLayout, QScrollArea, QListWidget, QPushButton, QTabWidget
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QTextCursor, QColor, QFont, QBrush
from PyQt6.QtCore import Qt, QSize

from lexical_analyzer import LexicalAnalyzer, Token
from syntax_analyzer import SyntaxAnalyzer, SyntaxError


class HelpDialog(QDialog):
    """Диалоговое окно справки"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Справка")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>📚 Справка языкового процессора</h2>
        
        <h3>📁 Меню "Файл"</h3>
        <ul>
            <li><b>Создать (Ctrl+N)</b> - создает новый документ</li>
            <li><b>Открыть (Ctrl+O)</b> - открывает существующий файл</li>
            <li><b>Сохранить (Ctrl+S)</b> - сохраняет текущий документ</li>
            <li><b>Сохранить как (Ctrl+Shift+S)</b> - сохраняет под новым именем</li>
            <li><b>Выход (Ctrl+Q)</b> - закрывает приложение</li>
        </ul>
        
        <h3>✏️ Меню "Правка"</h3>
        <ul>
            <li><b>Отменить (Ctrl+Z)</b> - отмена действия</li>
            <li><b>Повторить (Ctrl+Y)</b> - вернуть действия</li>
            <li><b>Вырезать (Ctrl+X)</b> - вырезать текст</li>
            <li><b>Копировать (Ctrl+C)</b> - копировать текст</li>
            <li><b>Вставить (Ctrl+V)</b> - вставить текст</li>
            <li><b>Удалить (Del)</b> - удалить текст</li>
            <li><b>Выделить все (Ctrl+A)</b> - выделить всё</li>
        </ul>
        
        <h3>▶️ Меню "Пуск"</h3>
        <ul>
            <li><b>Пуск (F5)</b> - полный анализ (лексический + синтаксический)</li>
        </ul>
        
        <h3>📝 Меню "Текст"</h3>
        <ul>
            <li>Информационные пункты и тестовые примеры</li>
        </ul>
        
        <h3>🌐 Меню "Язык"</h3>
        <ul>
            <li>Выбор языка интерфейса (будет реализовано)</li>
        </ul>
        """)
        
        layout.addWidget(help_text)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class AboutDialog(QDialog):
    """Диалоговое окно 'О программе'"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(500, 320)
        
        layout = QVBoxLayout()
        
        info_label = QLabel("""
        <h2>Языковой процессор</h2>
        <p><b>Версия:</b> 2.0</p>
        <p><b>Разработчик:</b> Зоркольцев И.А.</p>
        <p><b>Назначение:</b> Лексический и синтаксический анализ</p>
        <p><b>Вариант:</b> 13 - Объявление и определение записи (record) в Pascal</p>
        <p><b>Технологии:</b> Python + PyQt6</p>
        <hr>
        <p><b>Грамматика G[Z]:</b></p>
        <pre>
Z → "type" ID "=" "record" FIELD_LIST "end" ";"
FIELD_LIST → FIELD_DEF ( ";" FIELD_DEF )*
FIELD_DEF → ID_LIST ":" TYPE_NAME
ID_LIST → ID ( "," ID )*
TYPE_NAME → "real" | "integer"
        </pre>
        <p>Метод анализа: рекурсивный спуск + метод Айронса</p>
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(info_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class TextEditor(QMainWindow):
    """Главное окно текстового редактора с языковым процессором"""
    
    def __init__(self):
        super().__init__()
        
        self.current_file_path = None
        self.is_modified = False
        self.lexical_analyzer = LexicalAnalyzer()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.current_tokens = []
        self.current_errors = []
        
        self.text_menu_info = {
            "Постановка задачи": """
                <h3>📋 Постановка задачи</h3>
                <hr>
                <p><b>Вариант 13:</b> Объявление и определение записи (record) в Pascal</p>
                <p>Разработать языковой процессор, включающий:</p>
                <ol>
                    <li><b>Лексический анализатор</b> - выделение лексем</li>
                    <li><b>Синтаксический анализатор</b> - проверка структуры</li>
                </ol>
                <p><b>Пример корректной программы:</b></p>
                <pre>type complex = record
    re,im: real;
end;</pre>
                <p><b>Метод нейтрализации ошибок:</b> Айронса</p>
            """,
            
            "Грамматика": """
                <h3>📐 Грамматика G[Z]</h3>
                <hr>
                <pre>
Z → "type" ID "=" "record" FIELD_LIST "end" ";"
FIELD_LIST → FIELD_DEF ( ";" FIELD_DEF )*
FIELD_DEF → ID_LIST ":" TYPE_NAME
ID_LIST → ID ( "," ID )*
TYPE_NAME → "real" | "integer"

Терминалы:
- type, record, end, real, integer, ;, ,, :, =, идентификатор
                </pre>
            """,
            
            "Классификация грамматики": """
                <h3>🏷️ Классификация грамматики</h3>
                <hr>
                <p><b>По Хомскому:</b> Контекстно-свободная (Тип 2)</p>
                <ul>
                    <li>✓ Однозначная</li>
                    <li>✓ Без левой рекурсии</li>
                    <li>✓ Допускает нисходящий разбор</li>
                </ul>
                <p><b>Метод анализа:</b> Рекурсивный спуск</p>
            """,
            
            "Метод анализа": """
                <h3>🔍 Метод анализа</h3>
                <hr>
                <p><b>Метод:</b> Нисходящий разбор + метод Айронса</p>
                <p><b>Алгоритм:</b></p>
                <ol>
                    <li>Получение токенов от лексического анализатора</li>
                    <li>Рекурсивный спуск по правилам грамматики</li>
                    <li>При ошибке - восстановление методом Айронса</li>
                </ol>
                <p><b>Восстанавливающие символы:</b> ';', 'type', 'end'</p>
            """,
            
            "Тестовый пример": """
                <h3>🧪 Тестовые примеры</h3>
                <hr>
                <p>Доступно 12 тестовых примеров (корректные и с ошибками)</p>
                <p><b>Корректный пример:</b></p>
                <pre>type complex = record
    re,im: real;
    name: string;  // string для демонстрации (не поддерживается)
end;</pre>
            """,
            
            "Список литературы": """
                <h3>📚 Список литературы</h3>
                <hr>
                <ol>
                    <li><b>Ахо А., Ульман Дж.</b> Теория синтаксического анализа, перевода и компиляции. - М.: Мир, 1978.</li>
                    <li><b>Грис Д.</b> Конструирование компиляторов. - М.: Мир, 1975.</li>
                    <li><b>Хантер Р.</b> Основные концепции компиляторов. - М.: Вильямс, 2002.</li>
                    <li><b>Jensen K., Wirth N.</b> Pascal User Manual and Report. - Springer, 1974.</li>
                </ol>
            """,
            
            "Исходный код программы": """
                <h3>💻 Исходный код</h3>
                <hr>
                <pre>
project/
├── main.py
├── lexical_analyzer.py
├── syntax_analyzer.py
└── requirements.txt
                </pre>
                <p><b>Язык:</b> Python 3.8+</p>
                <p><b>GUI:</b> PyQt6</p>
            """
        }
        
        self.test_examples = {
            "✅ Корректный пример (complex)": 
                "type complex = record\n    re,im: real;\nend;",
            
            "✅ Корректный пример (person)": 
                "type person = record\n    name, surname: string;\n    age: integer;\nend;",
            
            "✅ Корректный пример (одно поле)": 
                "type point = record\n    x,y,z: real;\nend;",

        }
        
        self.init_ui()
    
    def get_icon(self, standard_icon):
        return self.style().standardIcon(standard_icon)
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Языковой процессор (Pascal record)")
        self.setMinimumSize(1100, 750)
        
        self.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_FileIcon))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Введите объявление записи (record) на Pascal...\n\n"
            "Пример:\n"
            "type complex = record\n"
            "    re,im: real;\n"
            "end;"
        )
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.setFont(QFont("Courier New", 12))
        
        self.tab_widget = QTabWidget()
        
        # Вкладка "Лог"
        self.log_tab = QWidget()
        log_layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Лог выполнения анализаторов...")
        self.output_area.setStyleSheet("background-color: #f5f5f5; font-family: 'Courier New';")
        log_layout.addWidget(self.output_area)
        self.log_tab.setLayout(log_layout)
        self.tab_widget.addTab(self.log_tab, "📋 Лог")
        
        # Вкладка "Ошибки"
        self.errors_tab = QWidget()
        errors_layout = QVBoxLayout()
        
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(3)
        self.error_table.setHorizontalHeaderLabels([
            "Неверный фрагмент", "Местоположение", "Описание ошибки"
        ])
        self.error_table.horizontalHeader().setStretchLastSection(True)
        self.error_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.error_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.error_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.error_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.error_table.setAlternatingRowColors(True)
        self.error_table.cellClicked.connect(self.on_error_table_clicked)
        
        errors_layout.addWidget(self.error_table)
        self.errors_tab.setLayout(errors_layout)
        self.tab_widget.addTab(self.errors_tab, "❌ Ошибки")
        
        # Вкладка "Лексемы"
        self.tokens_tab = QWidget()
        tokens_layout = QVBoxLayout()
        
        self.token_table = QTableWidget()
        self.token_table.setColumnCount(4)
        self.token_table.setHorizontalHeaderLabels([
            "Условный код", "Тип лексемы", "Лексема", "Местоположение"
        ])
        self.token_table.horizontalHeader().setStretchLastSection(True)
        self.token_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.token_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.token_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.token_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.token_table.setAlternatingRowColors(True)
        self.token_table.cellClicked.connect(self.on_token_table_clicked)
        
        tokens_layout.addWidget(self.token_table)
        self.tokens_tab.setLayout(tokens_layout)
        self.tab_widget.addTab(self.tokens_tab, "🔤 Лексемы")
        
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(self.editor)
        main_splitter.addWidget(self.tab_widget)
        main_splitter.setSizes([500, 400])
        
        main_layout.addWidget(main_splitter)
        
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
    
    def create_actions(self):
        # Файл
        self.new_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileIcon), "Создать", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogOpenButton), "Открыть...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.open_file)
        
        self.save_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Сохранить как...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogCloseButton), "Выход", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        
        # Правка
        self.undo_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_ArrowBack), "Отменить", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.editor.undo)
        
        self.redo_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_ArrowForward), "Повторить", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.editor.redo)
        
        self.cut_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_CommandLink), "Вырезать", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.triggered.connect(self.editor.cut)
        
        self.copy_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Копировать", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.editor.copy)
        
        self.paste_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_FileDialogContentsView), "Вставить", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self.editor.paste)
        
        self.delete_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_TrashIcon), "Удалить", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self.delete_text)
        
        self.select_all_action = QAction("Выделить все", self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.triggered.connect(self.editor.selectAll)
        
        # Текст
        self.task_action = QAction("Постановка задачи", self)
        self.task_action.triggered.connect(lambda: self.show_text_menu_info("Постановка задачи"))
        
        self.grammar_action = QAction("Грамматика", self)
        self.grammar_action.triggered.connect(lambda: self.show_text_menu_info("Грамматика"))
        
        self.classification_action = QAction("Классификация грамматики", self)
        self.classification_action.triggered.connect(lambda: self.show_text_menu_info("Классификация грамматики"))
        
        self.analysis_method_action = QAction("Метод анализа", self)
        self.analysis_method_action.triggered.connect(lambda: self.show_text_menu_info("Метод анализа"))
        
        self.test_example_action = QAction("Тестовый пример", self)
        self.test_example_action.setShortcut("Ctrl+T")
        self.test_example_action.triggered.connect(self.show_test_examples_dialog)
        
        self.literature_action = QAction("Список литературы", self)
        self.literature_action.triggered.connect(lambda: self.show_text_menu_info("Список литературы"))
        
        self.source_code_action = QAction("Исходный код программы", self)
        self.source_code_action.triggered.connect(lambda: self.show_text_menu_info("Исходный код программы"))
        
        # Пуск
        self.run_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MediaPlay), "Пуск", self)
        self.run_action.setShortcut("F5")
        self.run_action.setStatusTip("Запустить полный анализ")
        self.run_action.triggered.connect(self.run_analyzer)
        
        # Справка
        self.help_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_DialogHelpButton), "Вызов справки", self)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_action.triggered.connect(self.show_help)
        
        self.about_action = QAction(self.get_icon(QStyle.StandardPixmap.SP_MessageBoxInformation), "О программе", self)
        self.about_action.triggered.connect(self.show_about)
    
    def create_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        edit_menu = menubar.addMenu("Правка")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.delete_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)
        
        text_menu = menubar.addMenu("Текст")
        text_menu.addAction(self.task_action)
        text_menu.addAction(self.grammar_action)
        text_menu.addAction(self.classification_action)
        text_menu.addAction(self.analysis_method_action)
        text_menu.addSeparator()
        text_menu.addAction(self.test_example_action)
        text_menu.addAction(self.literature_action)
        text_menu.addAction(self.source_code_action)
        
        run_menu = menubar.addMenu("Пуск")
        run_menu.addAction(self.run_action)
        
        help_menu = menubar.addMenu("Справка")
        help_menu.addAction(self.help_action)
        help_menu.addAction(self.about_action)
        
        language_menu = menubar.addMenu("Язык")
        lang_ru = QAction("Русский", self)
        lang_ru.setEnabled(False)
        language_menu.addAction(lang_ru)
        lang_en = QAction("English", self)
        lang_en.setEnabled(False)
        language_menu.addAction(lang_en)
    
    def create_toolbar(self):
        toolbar = QToolBar("Панель инструментов")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.cut_action)
        toolbar.addAction(self.paste_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_action)
        toolbar.addSeparator()
        toolbar.addAction(self.help_action)
        toolbar.addAction(self.about_action)
    
    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Готов к работе")
    
    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.update_title()
    
    def update_title(self):
        if self.current_file_path:
            filename = os.path.basename(self.current_file_path)
            title = f"{filename}{'*' if self.is_modified else ''} - Языковой процессор (Pascal record)"
        else:
            title = f"Без имени{'*' if self.is_modified else ''} - Языковой процессор (Pascal record)"
        self.setWindowTitle(title)
    
    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file_path = None
            self.is_modified = False
            self.update_title()
            self.clear_results()
            self.statusbar.showMessage("Создан новый документ")
    
    def open_file(self):
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Открыть файл", "",
                "Текстовые файлы (*.txt);;Файлы Pascal (*.pas);;Все файлы (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self.editor.setText(file.read())
                    self.current_file_path = file_path
                    self.is_modified = False
                    self.update_title()
                    self.clear_results()
                    self.statusbar.showMessage(f"Открыт файл: {os.path.basename(file_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")
    
    def save_file(self):
        if self.current_file_path:
            return self.save_file_to_path(self.current_file_path)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "",
            "Текстовые файлы (*.txt);;Файлы Pascal (*.pas);;Все файлы (*.*)"
        )
        if file_path:
            return self.save_file_to_path(file_path)
        return False
    
    def save_file_to_path(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
            self.current_file_path = file_path
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Файл сохранен: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
            return False
    
    def maybe_save(self):
        if not self.is_modified:
            return True
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Сохранение изменений")
        dialog.setText("Документ был изменен.")
        dialog.setInformativeText("Сохранить изменения?")
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Save)
        
        result = dialog.exec()
        
        if result == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif result == QMessageBox.StandardButton.Cancel:
            return False
        else:
            return True
    
    def delete_text(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
    
    def clear_results(self):
        self.output_area.clear()
        self.token_table.setRowCount(0)
        self.error_table.setRowCount(0)
        self.current_tokens = []
        self.current_errors = []
    
    def show_text_menu_info(self, title):
        """Показать информацию из меню Текст"""
        info_html = self.text_menu_info.get(title, f"<h3>{title}</h3><p>Информация будет добавлена позже.</p>")
        
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(550, 400)
        dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        
        layout = QVBoxLayout()
        
        info_label = QLabel(info_html)
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setStyleSheet("padding: 10px;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_label)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_test_examples_dialog(self):
        """Показать диалог выбора тестового примера"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Тестовые примеры")
        dialog.setMinimumSize(650, 500)
        dialog.setWindowIcon(self.get_icon(QStyle.StandardPixmap.SP_FileDialogInfoView))
        
        layout = QVBoxLayout()
        
        title_label = QLabel("<h3>🧪 Выберите тестовый пример для загрузки в редактор</h3>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        example_names = list(self.test_examples.keys())
        
        list_widget = QListWidget()
        for example_name in example_names:
            list_widget.addItem(example_name)
        
        preview = QTextEdit()
        preview.setReadOnly(True)
        preview.setFont(QFont("Courier New", 11))
        preview.setMaximumHeight(150)
        preview.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc;")
        
        def on_selection_changed():
            selected = list_widget.currentItem()
            if selected:
                example_name = selected.text()
                preview.setText(self.test_examples[example_name])
        
        list_widget.currentItemChanged.connect(on_selection_changed)
        
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)
        
        button_layout = QHBoxLayout()
        
        load_button = QPushButton("📂 Загрузить в редактор")
        load_button.setStyleSheet("padding: 8px; font-weight: bold; background-color: #4CAF50; color: white;")
        
        close_button = QPushButton("Закрыть")
        close_button.setStyleSheet("padding: 8px;")
        
        def load_example():
            selected = list_widget.currentItem()
            if selected:
                example_name = selected.text()
                example_text = self.test_examples[example_name]
                self.editor.setText(example_text)
                self.clear_results()
                self.statusbar.showMessage(f"Загружен: {example_name}", 5000)
                dialog.accept()
        
        load_button.clicked.connect(load_example)
        close_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(close_button)
        
        layout.addWidget(QLabel("<b>Доступные примеры:</b>"))
        layout.addWidget(list_widget)
        layout.addWidget(QLabel("<b>Предпросмотр:</b>"))
        layout.addWidget(preview)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def run_analyzer(self):
        """Запуск полного анализа"""
        text = self.editor.toPlainText()
        
        self.clear_results()
        
        if not text.strip():
            self.output_area.append("⚠️ Пуск: текст пуст. Добавьте данные для анализа.")
            self.statusbar.showMessage("Текст пуст. Добавьте данные для анализа.")
            self.tab_widget.setCurrentIndex(0)
            return
        
        self.output_area.append("="*60)
        self.output_area.append("ЗАПУСК ПОЛНОГО АНАЛИЗА")
        self.output_area.append("="*60)
        self.output_area.append(f"Анализируемый текст:\n{text}\n")
        
        # Лексический анализ
        self.output_area.append("-"*60)
        self.output_area.append("ЭТАП 1: ЛЕКСИЧЕСКИЙ АНАЛИЗ")
        self.output_area.append("-"*60)
        
        try:
            tokens, lexical_errors = self.lexical_analyzer.analyze(text)
            self.current_tokens = tokens
            
            # Заполнение таблицы лексем (только значащие токены для удобства)
            significant_tokens = [t for t in tokens if t.token_type not in ['разделитель (пробел)', 'разделитель (новая строка)']]
            self.token_table.setRowCount(len(significant_tokens))
            
            for i, token in enumerate(significant_tokens):
                code_item = QTableWidgetItem(str(token.code))
                code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                type_item = QTableWidgetItem(token.token_type)
                lexeme_item = QTableWidgetItem(token.lexeme)
                
                location_text = f"строка {token.line}, поз. {token.start_pos}-{token.end_pos}"
                location_item = QTableWidgetItem(location_text)
                
                if token.is_error:
                    error_color = QColor(255, 220, 220)
                    code_item.setBackground(QBrush(error_color))
                    type_item.setBackground(QBrush(error_color))
                    lexeme_item.setBackground(QBrush(error_color))
                    location_item.setBackground(QBrush(error_color))
                
                self.token_table.setItem(i, 0, code_item)
                self.token_table.setItem(i, 1, type_item)
                self.token_table.setItem(i, 2, lexeme_item)
                self.token_table.setItem(i, 3, location_item)
            
            if lexical_errors:
                self.output_area.append(f"Лексических ошибок: {len(lexical_errors)}")
                for err in lexical_errors:
                    self.output_area.append(f"  • {err['message']} (строка {err['line']}, позиция {err['position']})")
            else:
                self.output_area.append("Лексический анализ завершен без ошибок")
                self.output_area.append(f"Выделено значащих лексем: {len(significant_tokens)}")
            
            # Синтаксический анализ
            self.output_area.append("\n" + "-"*60)
            self.output_area.append("ЭТАП 2: СИНТАКСИЧЕСКИЙ АНАЛИЗ")
            self.output_area.append("-"*60)
            
            success, syntax_errors = self.syntax_analyzer.analyze(text)
            self.current_errors = syntax_errors
            
            if syntax_errors:
                self.error_table.setRowCount(len(syntax_errors))
                
                for i, error in enumerate(syntax_errors):
                    fragment_item = QTableWidgetItem(error.fragment if error.fragment else "(пусто)")
                    fragment_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    location_text = f"строка {error.line}, позиция {error.position}"
                    location_item = QTableWidgetItem(location_text)
                    location_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    description_item = QTableWidgetItem(error.description)
                    
                    error_color = QColor(255, 200, 200)
                    fragment_item.setBackground(QBrush(error_color))
                    location_item.setBackground(QBrush(error_color))
                    description_item.setBackground(QBrush(error_color))
                    # Черный текст
                    fragment_item.setForeground(QBrush(QColor(0, 0, 0)))
                    location_item.setForeground(QBrush(QColor(0, 0, 0)))
                    description_item.setForeground(QBrush(QColor(0, 0, 0)))
                    # Жирный шрифт
                    font = QFont()
                    font.setBold(True)
                    fragment_item.setFont(font)
                    location_item.setFont(font)
                    description_item.setFont(font)
                    
                    self.error_table.setItem(i, 0, fragment_item)
                    self.error_table.setItem(i, 1, location_item)
                    self.error_table.setItem(i, 2, description_item)
                    
                    self.output_area.append(
                        f"  • {error.description} (строка {error.line}, позиция {error.position})"
                    )
                
                self.output_area.append(f"\nОбщее количество синтаксических ошибок: {len(syntax_errors)}")
                self.statusbar.showMessage(f"Анализ завершен: {len(syntax_errors)} синтаксических ошибок")
                self.tab_widget.setCurrentIndex(1)
            else:
                self.error_table.setRowCount(1)
                ok_item = QTableWidgetItem("✓ Синтаксических ошибок нет")
                ok_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                ok_font = QFont()
                ok_font.setBold(True)
                ok_item.setFont(ok_font)
                ok_item.setBackground(QBrush(QColor(200, 255, 200)))
                ok_item.setForeground(QBrush(QColor(0, 0, 0)))  # Черный текст
                self.error_table.setItem(0, 0, ok_item)
                self.error_table.setSpan(0, 0, 1, 3)
                
                self.output_area.append("✓ Синтаксический анализ завершен без ошибок")
                self.statusbar.showMessage("Анализ успешно завершен")
                self.tab_widget.setCurrentIndex(1)
                
        except Exception as e:
            self.output_area.append(f"\nКритическая ошибка анализа: {str(e)}")
            self.statusbar.showMessage("Ошибка анализа")
            self.tab_widget.setCurrentIndex(0)
    
    def on_token_table_clicked(self, row, column):
        if 0 <= row < len(self.current_tokens):
            token = self.current_tokens[row]
            self._navigate_to_position(token.line, token.start_pos, token.end_pos)
    
    def on_error_table_clicked(self, row, column):
        if 0 <= row < len(self.current_errors):
            error = self.current_errors[row]
            self._navigate_to_position(error.line, error.position, error.position)
    
    def _navigate_to_position(self, line, start_pos, end_pos):
        cursor = self.editor.textCursor()
        
        lines = self.editor.toPlainText().split('\n')
        position = 0
        
        for i in range(min(line - 1, len(lines))):
            position += len(lines[i]) + 1
        
        position += start_pos - 1
        
        text_length = len(self.editor.toPlainText())
        position = min(position, max(0, text_length - 1))
        
        cursor.setPosition(position)
        
        if start_pos != end_pos:
            end_position = position + (end_pos - start_pos + 1)
            end_position = min(end_position, text_length)
            cursor.setPosition(end_position, QTextCursor.MoveMode.KeepAnchor)
        
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        
        self.statusbar.showMessage(f"Переход: строка {line}, позиция {start_pos}", 5000)
    
    def show_help(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec()
        self.statusbar.showMessage("Открыта справочная система", 3000)
    
    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()
        self.statusbar.showMessage("Информация о программе", 3000)
    
    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Языковой процессор")
    app.setApplicationDisplayName("Языковой процессор (Pascal record)")
    
    app.setStyle("Fusion")
    
    editor = TextEditor()
    editor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()