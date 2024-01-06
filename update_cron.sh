#!/bin/bash

if [ $# -eq 0 ]
then
  echo "Ошибка: не указано количество минут."
  exit 1
fi

SCRIPT="main.py"
MINUTES=$1
HOURS=$(($MINUTES / 60))
MINUTES=$(($MINUTES % 60))
NEW_CRON_JOB="$MINUTES */$HOURS * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/$SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

(crontab -l | grep -v "$SCRIPT") | crontab -
(crontab -l; echo "$NEW_CRON_JOB") | crontab -

echo "Задача обновлена: будет запускаться каждые $1 минут."
