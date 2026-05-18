test:
	pytest

cleandoc:
	make -C docs/ clean

htmldoc:
	make -C docs/ html

doc: cleandoc htmldoc

dist:
	poetry build

clean:
	rm -rfv build dist aprspy.egg-info

upload:
	poetry publish

release: clean cleandoc htmldoc cleandoc dist upload
