=======
aprspy - An APRS packet parser for Python
=======

|version| |license| |build| |issues| |coverage-status|

Introduction
------------

The intention of the module is to provide a way to decode and encode various different types of APRS packets.

Currently supports:-

* Decoding
  * Standard compressed/uncompressed locations (PositionPacket)
  * Mic-E locations
  * Messages
  * Status reports

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
