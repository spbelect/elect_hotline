![Tests](https://github.com/Fak3/elect_hotline/actions/workflows/test-main.yml/badge.svg)
[![codecov](https://codecov.io/gh/spbelect/elect_hotline/graph/badge.svg?token=K9145KKJHE)](https://codecov.io/gh/spbelect/elect_hotline)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-V3.1-blue)](https://spbelect.github.io/elect_hotline/mobile_api_v4.html)

Elect-hotline is a web server that receives data from [Paradox](https://github.com/spbelect/paradox) android app. It has a web frontend to browse answers history, and organizations registry for teams assisting election observers.

Production website that follows stable branch: https://elect-hotline.vercel.app/


# Installation

```
git clone https://github.com/spbelect/elect_hotline.git
cd elect_hotline
pipx install pdm
pdm install
cd src
```

Edit env-local file: set DATABASE_URL and other required variables

```
cp env-local.example env-local
echo "DJANGO_SECRET_KEY=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1`" >> env-local
```

In case you are using postgres, you can create user and database with `pginit settings`

```
./manage.py migrate
./manage.py collectstatic
./scripts/regions.py populatedb
```

Create admin user:
`./manage.py createsuperuser`

Finally, run:
`./manage.py runserver 0.0.0.0:8000`

# Deployment

See https://github.com/spbelect/elect_hotline_deploy


# Test

Install dependencies

```
pdm install --dev
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

Beta website that follows main branch: https://elect-hotline-fak3-roman-s-projects-e5269d83.vercel.app

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
