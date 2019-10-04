aprspy - An APRS packet parser for Python
(c)2017-2019 Andy Smith VE6LY

The intention of the module is to provide a way to decode and encode various different types of APRS packets.

Currently supports:-

* Decoding
  * Standard compressed/uncompressed locations (PositionPacket)
  * Mic-E locations
  * Messages
  * Status reports

Brief usage explanation:-

```
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
```
