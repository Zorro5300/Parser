@echo off
chcp 65001 >nul
echo ============================================
echo  Сборка исполняемого файла Языковой процессор
echo ============================================
echo.

REM Проверка наличия PyInstaller
where pyinstaller >nul 2>nul
if errorlevel 1 (
    echo PyInstaller не найден. Устанавливаем...
    pip install pyinstaller
    if errorlevel 1 (
        echo Ошибка установки PyInstaller.
        pause
        exit /b 1
    )
)

REM Проверка наличия зависимостей
if not exist requirements.txt (
    echo Файл requirements.txt не найден. Создаем...
    echo PyQt6>=6.5.0 > requirements.txt
)

echo Установка/обновление зависимостей из requirements.txt...
pip install -r requirements.txt --upgrade
if errorlevel 1 (
    echo Ошибка установки зависимостей.
    pause
    exit /b 1
)

REM Удаление предыдущих сборок
echo Очистка предыдущих сборок...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist "Языковой процессор.spec" del "Языковой процессор.spec"

REM Сборка
echo Запуск PyInstaller...
pyinstaller --onefile --windowed --name "Языковой процессор" main.py
if errorlevel 1 (
    echo Ошибка сборки.
    pause
    exit /b 1
)

REM Проверка результата
if exist "dist\Языковой процессор.exe" (
    echo.
    echo ============================================
    echo Сборка успешно завершена!
    echo Исполняемый файл: dist\Языковой процессор.exe
    echo Размер: 
    for %%F in ("dist\Языковой процессор.exe") do echo   %%~zF байт
    echo ============================================
) else (
    echo Ошибка: исполняемый файл не создан.
    pause
    exit /b 1
)

echo.
echo Для запуска программы дважды щелкните по файлу "Языковой процессор.exe" в папке dist.
pause