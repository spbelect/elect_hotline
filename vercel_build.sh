#python -m pip install -U pip
pip3.12 install -r requirements.txt
pip3.12 install .
python3.12 -c "from importlib import metadata; print(metadata.version('elect-hotline'))"
python3.12 manage.py collectstatic --noinput
python3.12 manage.py migrate
