# Yatube
### Содержание:
 + [Использованные технологии](#Tech)
 + [Описание](#Description)
 + [Как запустить проект](#EasyStart)
 + [Об авторе](#About)

<br>
<a id="Tech"></a>

### Использованные технологии:

* Python 
* Django 2.2.16
* Pillow 8.3.1
* Pytest 6.2.4
* Bootstrap

<br>
<a name="Description"></a>

### Описание:

Небольшой проект социальной сети с шутливым названием Yatube. После запуска сервера пользователю доступно: 
- регистрация нового пользователя
- просмотр постов других пользователей
- добавление/редактирование/удаление личных постов
- подписка на других авторов
- просмотр комментариев к постам
- добавление/редактирование/удаление личных комментариев к постам
- восстановление (по email) или смена пароля пользователя

<br>
<a id="EasyStart"></a>

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/gras5/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Создать суперпользователя:

```
python3 manage.py createsuperuser
```


Запустить проект:

```
python3 manage.py runserver
```


<br>
<a name="About"></a>

### Об авторе
Github: https://github.com/gras5
