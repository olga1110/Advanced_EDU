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
* с указанием уровня логирования: `python3 ./log_analyzer.py --level 'd'` либо </br>
```python3 ./log_analyzer.py -l 'd'```, где:</br>
d+: детальная иформация, вкл. справку по функции и время работы;   d: DEBUG, i:INFO, w: WARNING, c:CRITICAL, e:ERROR
* с параметрами по умолчанию: ```python3 ./log_analyzer.py``` (config.ini, INFO)
#### Запуск unittest:
```python3 ./test_log_report.py```
