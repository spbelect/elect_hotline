#python -m pip install -U pip
pip3.12 install -r requirements.txt
python3.12 manage.py collectstatic --noinput
python3.12 manage.py migrate
