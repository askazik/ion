###### !!! pip freeze > requirements.txt  # Обновление файла требуемых зависимостей. !!!


# **Подготовка к работе**

1. Clone repository:
    ```
    git clone https://git.zuzex.com/math/python_flask_bot
    ```
1. Переключиться на необходимую ветку. Ветка master - для заливки на сервер (в нее можно делать только merge requests через web-интерфейс).
Ветка dev - для сбора веток разработчиков.
1. Install requirements:
    ```
    pip install -r requirements.txt
    ```
1. Create default folder for logs, provide access
    ```
    $ cd /var/log/
    $ sudo mkdir employee_app
    $ sudo chown user:group /var/log/employee_app
    ex.: sudo chown redhat:users /var/log/employee_app
    ```
1. [Initialize the Database](readme/true_init_database.md)
1. Переместиться в директорию проекта: cd -> python_flask_bot<br/> 
Выполнить миграции
    ~~~
    $ export FLASK_APP=employee_app
    $ flask db upgrade
    ~~~
1. Заполнение базы данных / запуск сервера:
    ~~~
    Запустить employee_app/__init__.py
    ~~~

# Документация разработчика
1. [Внешние программы](readme/external_programs.md)
1. [Структура БД](readme/db_structure.md)
1. [Система инициализации (настройки программы)](readme/config_ini.md)
1. [Система журналирования](readme/logging.md)
1. [Локализация (i18n)](readme/localization.md)
1. [Фоновые задачи](readme/flask_backgroundscheduler.md)
1. [Роли (Сотрудник, Руководитель, Администратор)](readme/roles.md)
1. [Docker](readme/docker.md)
1. [Система тестирования](readme/tests.md)
1. [Линтер](readme/pylint.md)
1. [Сервер для разработки и релизный сервер](readme/servers.md)

---
## Инструкции для работы с модулями системы:
1. [Работа с flask-SQLAlchemy](readme/flask-SQLAlchemy.md)
1. [Выходные дни](readme/holidays.md)
1. [Работа с сервером](readme/work_with_server.md)
1. [Начальный файл справки с заглушками для всех страниц](readme/help-init.md)
---
### Bugs
1. [Перевод БД из latin1 в utf8](readme/bug_db_collation.md)
    ~~~
    /.../PycharmProjects/.../venv/lib/python3.6/site-packages/pymysql/cursors.py:170: Warning: (1300, "Invalid utf8mb4 character string: '80037D'")
    ~~~