init:
	poetry install
lint: init
	poetry run isort --line-length 80 --profile google fshg
	poetry run pyink --line-length 80 --pyink --preview --unstable fshg
	poetry run pylint --rcfile .pylintrc fshg
install:
	pip install .
.PHONY: init lint install