###### !!! pip freeze > requirements.txt  # Обновление файла требуемых зависимостей. !!!


# **Подготовка к работе**

1. Clone repository:
    ```
    https://github.com/askazik/ion.git
    ```
1. Переключиться на необходимую ветку. Ветка master - для заливки на сервер (в нее можно делать только merge requests через web-интерфейс).
Ветка dev - для сбора веток разработчиков.
1. Install requirements:
    ```
    pip install -r requirements.txt
    ```
1. [Initialize the Database](readme/true_init_database.md)
1. Переместиться в директорию проекта: cd -> python_flask_bot<br/> 
Выполнить миграции
    ~~~
    $ export FLASK_APP=application
    $ flask db upgrade
    ~~~
1. Заполнение базы данных / запуск сервера:
    ~~~
    Запустить application/__init__.py
    ~~~
