#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError
from ..utils import APRSUtils
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class StatusPacket(GenericPacket):
    """
    Class to represent status report packets.

    As per APRS 1.01, status reports "announce(s) the station's current mission or any other single
    line status to everyone". The data type identifier for status reports is ">".

    See APRS 1.01 C16 P80
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status_message = None
        self._maidenhead_locator = None

    @property
    def status_message(self) -> str:
        """Get the status message"""
        return self._status_message

    @status_message.setter
    def status_message(self, value: str):
        """Set the status message"""
        self._status_message = value

    @property
    def maidenhead_locator(self) -> str:
        """Get the Maidenhead locator (if set)"""
        return self._maidenhead_locator

    @maidenhead_locator.setter
    def maidenhead_locator(self, value: str):
        """Set the Maidenhead locator"""
        self._maidenhead_locator = value

    def _parse(self) -> bool:
        """
        Parse a status report packet.

        Status reports contain a status message and optionally a timestamp or Maidenhead locator
        (but not both), and/or a beam heading and ERP value.

        Parse and decoded values are stored in the current object.
        """

        # Maidenhead locators, if present, must be first, and can be 4 or 6 characters.
        # They must also include a symbol table and symbol code (P81).
        # Therefore, if the status report matches [A-Z]{2}[0-9]{2}([A-Z]{2})? and a valid symbol
        # table and id, then it's a Maidenhead locator.
        # Valid symbol table IDs: /, \, 0-9, A-Z (C20 P91)
        mh_4 = None
        mh_6 = None

        if len(self._info) >= 6:
            mh_4 = self._info[0:6]
            logger.debug("Considering as Maidenhead locator: {}".format(mh_4))

        if len(self._info) >= 8:
            mh_6 = self._info[0:8]
            logger.debug("Considering as Maidenhead locator: {}".format(mh_6))

        if mh_6 is not None and re.match("[A-Z]{2}[0-9]{2}[A-Z]{2}[/\\\0-9A-Z].", mh_6):
            # Maidenhead locator (GGnngg)
            self.maidenhead_locator = mh_6[0:6]

            self.symbol_table = mh_6[6]
            self.symbol_id = mh_6[7]

            logger.debug("Status with Maidenhead locator {}, symbol {} {}".format(
                self.maidenhead_locator, self.symbol_table, self.symbol_id
            ))

            if len(self._info) != 8:
                # First character of the text must be " " (C16 P82)
                if self._info[8] != " ":
                    # TODO
                    raise ParseError("Status message is invalid", self)
                else:
                    self.status_message = self._info[9:]
                    logger.debug("Status message is {}".format(self.status_message))
            else:
                logger.debug("No status message")

        elif mh_4 is not None and re.match(r'[A-Z]{2}[0-9]{2}[/\\\0-9A-Z].', mh_4):
            # Maidenhead locator (GGnn)
            self.maidenhead_locator = mh_4[0:4]

            self.symbol_table = mh_4[4]
            self.symbol_id = mh_4[5]

            logger.debug("Status with Maidenhead locator {}, symbol {} {}".format(
                self.maidenhead_locator, self.symbol_table, self.symbol_id
            ))

            if len(self._info) != 6:

                # First character of the text must be " " (C16 P82)
                if self._info[6] != " ":
                    # TODO
                    raise ParseError("Status message is invalid", self)
                else:
                    self.status_message = self._info[7:]
                    logger.debug("Status message is {}".format(self.status_message))
            else:
                logger.debug("No status message")

        else:
            # Check for a timestamp
            if re.match("^[0-9]{6}z", self._info):
                try:
                    self.timestamp = APRSUtils.decode_timestamp(self._info[0:7])
                    # TODO Sanity check the timestamp type - status reports can only use zulu
                    # or local, so if hms is used, throw an error.
                    # if timestamp_type == 'h' and data_type_id == '>':
                    #     logger.error("Timestamp type 'h' cannot be used for status reports")
                    #     raise ParseError("Timestamp type 'h' cannot be used for status reports")
                    logger.debug("Status message timestamp is {}".format(self.timestamp))

                except ParseError:
                    self.timestamp = None

                self.status_message = self._info[7:]
                logger.debug("Status message is {}".format(self.status_message))

            else:
                self.status_message = self._info
                logger.debug("No timestamp found")
                logger.debug("Status message is {}".format(self.status_message))

        # Check for a beam heading and ERP
        # TODO - Parse and decode the beam and ERP values
        if self.status_message and re.match(r'[\^].{2}', self.status_message[-3:]):
            logger.debug("Status message heading and power: {}".format(self.status_message[-2:]))

        return True

    def __repr__(self):
        if self.source:
            return "<StatusPacket: {}>".format(self.source)
        else:
            return "<StatusPacket>"
