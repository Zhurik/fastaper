# FASTAPER

Тестовое задание на backend разраба.

## Установка и запуск

Из корня:

```text
docker-compose up --build
```

## API

### /add_rates

Получает на вход структуру из примера и возвращает в ответе количество обработанных полей.

### /rate

Можно либо отправить ему json с определенной структурой, в которую он запишет результат вычислений, либо в url указать необходимые данные и он вернет json с результатом.

## Тестирование

Для тестов необходимо доставить следующие пакеты:

```text
pip install pytest asynctest
```

Запускаем тесты:

```text
pytest
```

## Замечания

Неплохо было бы сделать модель, в которой первичным ключом был бы составной ключ из даты и типа груза, но доки TortoiseORM говорят, что пока так не умеют(.

В примере в поле `rate` была строка, хотя по логике правильнее было бы заменить ее на float или хотя бы int.

Не совсем понял, что понимается под "тариф должен загружаться из файла JSON", поэтому просто при запуске подгружаются данные из примера в БД.