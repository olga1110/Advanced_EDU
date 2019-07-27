# Part1. Homeworks
## Log parser
Программа <b>log_analyzer.py</b> предназначена для анализа времени загрузки url-адресов. </br>
Формирует web-отчет со статистикой в разрезе url.</br>
Настройки необходимо задавать в файле config.ini:
* директории исходных данных, отчета и лога;
* % допустимых ошибок парсинга
По всем функциям доступна справка
Логи сохраняются в файле <b>report.log</b>
#### Пример запуска скрипта:
* с указанием расположения config файла: `python3 ./log_analyzer.py --config './config.ini'` либо </br>
```python3 ./log_analyzer.py -c './config.ini'```
* с config файлом по умолчанию: ```python3 ./log_analyzer.py```
#### Запуск unittest:
```python3 ./test_log_report.py```
