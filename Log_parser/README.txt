Программа log_analyzer.py предназначена для анализа времени загрузки url-адресов.
Формирует web-отчет со статистикой в разрезе url.
Настройки необходимо задавать в файле config.ini:
диретории исходных данных, отчета и лога; % допустимых ошибок парсинга
По всем функциям доступна справка: help()/__doc__
Логи сохраняются в файле report.log.

Пример запуска скрипта:
- с указанием расположения config файла: python3 ./log_analyzer.py --config './config.ini' либо
python3 ./log_analyzer.py -c './config.ini'
- с config файлом по умолчанию: python3 ./log_analyzer.py

Запуск unittest:
python3 ./test_log_report.py
