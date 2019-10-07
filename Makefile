test:
	pytest

dist:
	python setup.py sdist bdist_wheel

clean:
	rm -rfv build dist aprspy.egg-info

upload:
	twine upload dist/*

release: clean dist upload
