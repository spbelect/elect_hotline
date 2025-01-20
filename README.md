![Tests](https://github.com/Fak3/elect_hotline/actions/workflows/test-main.yml/badge.svg)


Elect-hotline is a web server that receives data from [Paradox](https://github.com/spbelect/paradox) android app. It has a web frontend to browse answers history, and organizations registry for teams assisting election observers.

Beta website that follows main branch: https://elect-hotline-fak3-roman-s-projects-e5269d83.vercel.app

Production website that follows stable branch: https://elect-hotline.vercel.app


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

Edit env-heroku file: set DATABASE_URL and other required variables

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

Edit env-local file: set DATABASE_URL and other required variables

```
pginit settings
./manage.py migrate
./manage.py collectstatic
./scripts/regions.py populatedb
./manage.py runserver 0.0.0.0:8000
```

## Создать учетную запись админа

`./manage.py createsuperuser`

# Test

Install dependencies

```
pipenv install --dev
```

Run tests

```
pytest -s -m 'not uitest' --doctest-modules -n auto --verbose
```

Or just `pdm test`

## Browser tests

Website user interaction scenarios with playwright automation

```
pdm install --dev --group uitest
playwright install chromium
```

Run playwright tests

```
pytest -s -m uitest --headed --tracing retain-on-failure  --verbose
```

Or just `pdm uitest`

Traces of failed playwright tests can be viewed:

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

`npx tailwindcss -i ./static/main.post.css -o ./static/main.css` or just `pdm makecss`

Use `pdm makecss --watch` to automatically transpile postcss when html file changes.


## Outdated packages

To check for new versions of depndencies run `$ pdm outdated`

## Venv activation

To simplify virtual environment activation, add to  `~/.bashrc`:

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

First you need to check package version number constraints in pyproject.toml, edit constraints to match the desired new version. Then run `pdm update <package>`
