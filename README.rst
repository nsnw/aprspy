=========================================
aprspy - An APRS packet parser for Python
=========================================

|version| |license| |build| |docs| |issues| |coverage-status|

Introduction
------------

**aprspy** is an APRS packet parser and generator for Python.

Currently supports:-

- Decoding
   - Standard compressed/uncompressed location packets
   - Mic-E location packets
   - Message packets (including bulletins and announcements)
   - Status report packets


- Encoding
   - Uncompressed location packets
   - Message packets


Usage
-----

Brief usage explanation::

   >>> from aprspy import APRS
   >>> packet = APRS.parse('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet')
   >>> packet
   <PositionPacket: XX1XX>
   >>> packet.latitude
   50.508333
   >>> packet.longitude
   -100.338333
   >>> packet.course
   221

Documentation
-------------

Documentation can be found at https://aprspy.readthedocs.io/en/latest/.

Development
-----------

Dependencies needed for development can be installed with ``pip install -r dev-requirements.txt``.

The documentation can be built locally by running ``make`` in the ``docs/`` folder.

Copyright
---------

This module is released under the MIT License, and is copyright 2019 Andy Smith <andy@nsnw.ca>

.. |version| image:: https://img.shields.io/pypi/v/aprspy.svg
   :target: https://pypi.python.org/pypi/aprspy
.. |issues| image:: https://img.shields.io/github/issues/nsnw/aprspy.svg
   :target: https://github.com/nsnw/aprspy/issues
.. |license| image:: https://img.shields.io/pypi/l/aprspy.svg
   :target: https://github.com/nsnw/aprspy/blob/master/COPYING
.. |build| image:: https://travis-ci.org/nsnw/aprspy.svg?branch=master
   :target: https://travis-ci.org/nsnw/aprspy
.. |coverage-status| image:: https://coveralls.io/repos/github/nsnw/aprspy/badge.svg?branch=master
   :target: https://coveralls.io/github/nsnw/aprspy?branch=master  
.. |docs| image:: https://readthedocs.org/projects/aprspy/badge/?version=latest
   :target: https://aprspy.readthedocs.io/en/latest/?badge=latest
