[![vercel-beta](https://github.com/Fak3/elect_hotline/actions/workflows/vercel-beta.yml/badge.svg)](https://github.com/Fak3/elect_hotline/actions/workflows/vercel-beta.yml)

# Сервер сбора данных от наблюдателей
Описание.

# Демо сайт

TODO

# Installation

```
git clone https://bitbucket.org/fak3/npserver.git
cd npserver
mkvirtualenv -p python3 ufo
pip install pdm
pdm sync --verbose
```


## Production deployment

```
python manage.py check --tag email --deploy
python manage.py check --deploy --fail-level=WARNING && DJANGO_DEBUG=0 gunicorn "wsgi:application" --access-logfile - --workers 12 --threads 12 --reload
```

## Deploy with Neondb

```
zypper in postgresql
```

```
DJANGO_SETTINGS_MODULE=settings_neondb ./manage.py migrate
DJANGO_SETTINGS_MODULE=settings_neondb ./scripts/regions.py
```

### Deploy to Heroku
```
git remote add heroku https://git.heroku.com/spbtest-2019.git
cp env-local.example env-heroku
echo "DJANGO_SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1`" >> env-heroku
export HEROKUAPP=`git remote get-url heroku | python -c "print(input().split('/')[-1][:-4])"`
```

Отредактировать в env-heroku DATABASE_URL и все остальные необходимые переменные окружения

```
./push_heroku_env.py env-heroku
git push heroku master
heroku run sh -c './manage.py migrate --skip-checks'
heroku run sh -c './scripts/2020_ankety.py'
heroku run sh -c './scripts/regions.py populatedb'
heroku run sh -c './manage.py createsuperuser'
```


## Local deployment

```
cp env-local.example env-local
echo "DJANGO_SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1`" >> env-local
```

Отредактировать в env-local DATABASE_URL и все остальные необходимые переменные окружения.

```
pginit settings
./manage.py migrate
./manage.py collectstatic
./scripts/regions.py populatedb
./manage.py runserver 0.0.0.0:8000
```

## Создать учетную запись админа

`./manage.py createsuperuser`

На heroku - сначала запустить удаленную консоль `heroku run bash`

# Test

Установить зависимости
```
pipenv install --dev
```

Запустить
```
pytest -s -m 'not uitest' --doctest-modules -n auto --verbose
```
или скрипт `pdm test`

## Браузерные тесты

Проверяют полноценные сценарии взимодействия с сайтом.
```
pdm install --dev --group uitest
zypper in playwright
```

Запустить
```
pytest -s -m uitest --headed --tracing retain-on-failure  --verbose
```
или скрипт `pdm uitest`

Трейсы проваленных тестов можно посмотреть:
```
playwright show-trace test-results/test-ui-create-campaign-test-py-test-scenario-chromium/trace.zip
```


# Development notes

## Translation

Install requirements
```
zypper in gettext-tools
pdm install --dev --group translate
```

Parse all files for new messsages
`pdm makemessages`

Compile after making new translations
`pdm compilemessages`


## TailwindCSS

Istall requirements

```
npm install -D postcss-import
npm install -D daisyui@latest
npm install -D tailwindcss
npm install -D @tailwindcss/typography
```

Transpile postcss with command

`npx tailwindcss -i ./static/main.post.css -o ./static/main.css`


## Outdated packages
Чтобы узнать какие новые версии необходимых пакетов доступны для обновления, можно запустить `$ pdm outdated`

## Venv activation

Для упрощения активации venv можно добавить в ~/.bashrc:

```
pdm() {
  local command=$1

  if [[ "$command" == "shell" ]]; then
      eval $(pdm venv activate)
  else
      command pdm $@
  fi
}
```

## Update required python package

Чтобы обновить питоно-пакет (напр. djangorestframework), запустить `pdm update djangorestframework`.

Если pyproject.toml не указано ограничений версии то скорее всего этот пакет можно обновить на последнюю версию без изменений в коде проекта. Если же в pyproject.toml указано ограничение на версию пакета вида `<2.3`, то pdm позволит обновиться только до версии 2.2.x

Если нужно обновить пакет на более новую версию, чем ограничено в pyproject.toml, то необходимо сначала исправить версию в pyproject.toml, затем запустить `pdm update`
