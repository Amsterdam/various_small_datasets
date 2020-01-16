.PHONY: install
install:
	pip install -r requirements_dev.txt

.PHONY: install-sync
install-sync:
	pip-sync requirements.txt requirements_dev.txt

.PHONY: requirements
requirements: requirements.in
	pip-compile -v --output-file requirements.txt requirements.in

.PHONY: upgrade
upgrade:
	pur --patch=Django -r requirements.in
	pur --no-recursive -r requirements_dev.txt
	pip-compile -v --upgrade --output-file requirements.txt requirements.in

.PHONY: test
test:
	./manage.py test -v1
