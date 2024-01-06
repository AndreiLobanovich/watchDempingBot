#!/bin/bash

sudo apt-get update
sudo apt-get install -y python3.10-venv

# Установка пути к директории скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Создание виртуального окружения Python
python3 -m venv "$SCRIPT_DIR/venv"

# Активация виртуального окружения
source "$SCRIPT_DIR/venv/bin/activate"

# Установка зависимостей из файла requirements.txt
pip install -r "$SCRIPT_DIR/requirements.txt"

# Добавление задачи в crontab
(crontab -l 2>/dev/null; echo "0 */2 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/main.py >> $SCRIPT_DIR/log.txt 2>&1") | crontab -

# Деактивация виртуального окружения
deactivate
