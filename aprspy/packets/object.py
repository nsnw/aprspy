#!/usr/bin/env python

import logging

from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class ObjectPacket(GenericPacket):

    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        if self.source:
            return "<ObjectPacket: {}>".format(self.source)
        else:
            return "<ObjectPacket>"
