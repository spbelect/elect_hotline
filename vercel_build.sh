#python -m pip install -U pip
pip3.12 install pdm
python3.12 -m pdm install -v
#pip3.12 install -r requirements.txt
#pip3.12 install .
#python3.12 -c "from importlib import metadata; print(metadata.version('elect-hotline'))"
python3.12 ./src/manage.py collectstatic --noinput
python3.12 ./src/manage.py migrate
