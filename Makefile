venv:
	virtualenv -p python3.5 venv
	make pip

pip:
	venv/bin/pip install -r requirements.txt

