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

## Scoring API
HTTP API сервис скоринга:
* метод online_score: возвращает балл скоринга либо информацию по ошибке аутентификации/валидации;
* метод clients_interests: возвращает словарь id клиента: список интересов либо информацию по ошибке аутентификации/валидации;

Аргументы командной строки:
* порт сервера: -p --port
* наименование лог файла: -l --log

#### Примеры post-запросов:
* online_score: curl -X POST -H "Content-Type: application/json" -d '{"account": '1', "token": "1ac26c0ce8a827368e6f2d3a6466541b861ecb0cc3393610b5b8a69f5100bb3c8e67b2d8a010e723ed8d4b3f72cdcfb95a71297da5ff13fd86f86f627b878191", "arguments": []}' http://127.0.0.1:8000/online_score/
* clients_interests:    curl -X POST -H "Content-Type: application/json" -d  '{"account": "account", "login": "admin", "method": "clients_interests", "token": "9deefae6d21ce2e9f98138f4c4f496a379d80a209d8396468463845d797dd92eff10a45d13ec84d46dddec98ffd529216b87d81963750bf4ac5f0a7abc2c28e9", "arguments": {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}}' http://127.0.0.1:8000/clients_interests/

