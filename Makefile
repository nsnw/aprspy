test:
	pytest

check_readme:
	python -m rstvalidator README.rst

cleandoc:
	make -C docs/ clean

htmldoc:
	make -C docs/ html

doc: cleandoc htmldoc

dist:
	python setup.py sdist bdist_wheel

clean:
	rm -rfv build dist aprspy.egg-info

upload:
	twine upload dist/*

release: clean check_readme cleandoc htmldoc cleandoc dist upload
