# Homework_bot
### Python telegram bot

Telegram-бот, который обращаться к API сервиса Практикум.Домашка и узнает статус домашней работы: взята ли домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

Задачи бота:
- раз в 10 минут опрашивать API сервис Практикум.Домашка и проверяеть статус отправленной на ревью домашней работы;
- при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
- логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

###Сруктура

Функция **main()**: в ней описана основная логика работы программы. Все остальные функции запускаются из неё. Последовательность действий:
- Сделать запрос к API.
- Проверить ответ.
- Если есть обновления — получить статус работы из обновления и отправить 
  сообщение в Telegram.
- Подождать некоторое время и вернуться в пункт 1.

Функция **check_tokens()** проверяет доступность переменных окружения, которые необходимы для работы программы. Если отсутствует хотя бы одна переменная окружения — продолжать работу бота нет смысла.
Функция **get_api_answer()** делает запрос к единственному эндпоинту API-сервиса. В качестве параметра в функцию передается временная метка. В случае успешного запроса должна вернуть ответ API, приведя его из формата JSON к типам данных Python.
Функция **check_response()** проверяет ответ API на соответствие документации из урока API сервиса Практикум.Домашка. В качестве параметра функция получает ответ API, приведенный к типам данных Python.
Функция **parse_status()** извлекает из информации о конкретной домашней работе статус этой работы. В качестве параметра функция получает только один элемент из списка домашних работ. В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря HOMEWORK_VERDICTS.
Функция **send_message()** отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.

### Логирование событий
Пример сообщения в журнале логов
```
2021-10-09 15:34:45,150 [ERROR] Сбой в работе программы: Эндпоинт https://practicum.yandex.ru/api/user_api/homework_statuses/111 недоступен. Код ответа API: 404
2021-10-09 15:34:45,355 [DEBUG] Бот отправил сообщение "Сбой в работе программы: Эндпоинт [https://practicum.yandex.ru/api/user_api/homework_statuses/](https://practicum.yandex.ru/api/user_api/homework_statuses/) недоступен. Код ответа API: 404"
```

Логируются следующие события:
- отсутствие обязательных переменных окружения во время запуска бота (уровень CRITICAL).
- удачная отправка любого сообщения в Telegram (уровень DEBUG);
сбой при отправке сообщения в Telegram (уровень ERROR);
- недоступность эндпоинта https://practicum.yandex.ru/api/user_api/homework_statuses/ (уровень ERROR);
- любые другие сбои при запросе к эндпоинту (уровень ERROR);
отсутствие ожидаемых ключей в ответе API (уровень ERROR);
- неожиданный статус домашней работы, обнаруженный в ответе API (уровень ERROR);
- отсутствие в ответе новых статусов (уровень DEBUG).

События уровня ERROR не только логируются, но информация о них пересылается в ваш Telegram в тех случаях, когда это технически возможно (если API Telegram перестанет отвечать или при старте программы не окажется нужной переменной окружения — ничего отправить не получится).
Если при каждой попытке бота получить и обработать информацию от API ошибка повторяется — повтороное сообщение о ней в Telegram не отправляется: о такой ошибке отправлено лишь одно сообщение. При этом в логи записывается информация о каждой неудачной попытке.

Для работы с логами проекта применяется обработчик StreamHandler, логи выводятся в стандартный поток sys.stdout.

Если установить параметр from_date равным нулю — API вернёт актуальные статусы домашек за всё время.
