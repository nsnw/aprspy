#!/usr/bin/env python

import logging

from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class ObjectPacket(GenericPacket):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        if self.source:
            return "<ObjectPacket: {}>".format(self.source)
        else:
            return "<ObjectPacket>"

    def _parse(self) -> bool:
        return True
