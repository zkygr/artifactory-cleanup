copy-examples:
	cp tests/data/cleanup.yaml examples/artifactory-cleanup.yaml
	cp tests/data/myrule.py examples/myrule.py
	cp tests/data/policies.py examples/python_style_config.py

build:
	 docker build . --file docker/Dockerfile --tag devopshq/artifactory-cleanup

publish-pypi:
	pipenv run python -m build

	pipenv run twine upload \
		--repository pypi \
		--username __token__ \
		dist/*
