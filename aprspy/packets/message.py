#!/usr/bin/env python

import re
import logging

from ..exceptions import ParseError, GenerateError
from ..warnings import ParseWarningCode
from .generic import GenericPacket

# Set up logging
logger = logging.getLogger(__name__)


class MessagePacket(GenericPacket):
    """
    Class to represent APRS message packets.

    APRS message packets can be from one station to another, or general bulletins or announcements
    which are intended for a wider audience.

    See also APRS 1.01 C14 P71
    """

    def __init__(self, addressee: str = None, message: str = None, message_id: str = None,
                 bulletin_id: int = None, announcement_id: str = None,
                 group_bulletin_name: str = None, *args, **kwargs):
        """
        Create a new :class:`MessagePacket` object.

        :param str addressee: the message addressee
        :param str message: the message
        :param str message_id: an optional message ID
        :param int bulletin_id: the bulletin ID
        :param str announcement_id: the announcement ID
        :param str group_bulletin_name: the group bulletin name
        """
        super().__init__(*args, **kwargs)
        self._addressee = addressee
        self._message = message
        self._message_id = message_id
        self._bulletin_id = bulletin_id
        self._announcement_id = announcement_id
        self._group_bulletin_name = group_bulletin_name

        # Set the data type ID
        self.data_type_id = ":"

    @property
    def addressee(self) -> str:
        """Get the addressee of the message"""
        return self._addressee

    @addressee.setter
    def addressee(self, value: str):
        """Set the addressee of the message"""
        if value is None:
            # Clear the addressee
            self._addressee = None
        elif type(value) is str:
            if len(value) > 9:
                # The maximum length of the addressee is 9 characters
                raise ValueError(
                    "Addressee length cannot be longer than 9 characters ({} given)".format(
                        len(value)
                    )
                )
            else:
                self._addressee = value
        else:
            raise TypeError("Addressee must be of type 'str' ({} given)".format(type(value)))

    @property
    def message(self) -> str:
        """Get the message"""
        return self._message

    @message.setter
    def message(self, value: str):
        """Set the message"""
        if value is None:
            # Clear the message
            self._message = None
        elif type(value) is str:
            if len(value) > 67:
                # The maximum length of a message is 67 characters (C14 P71)
                self._warn(
                    ParseWarningCode.MESSAGE_TOO_LONG,
                    "Message length should not be longer than 67 characters ({} given)".format(
                        len(value)
                    )
                )
            self._message = value
        else:
            raise TypeError("Message must be of type 'str' ({} given)".format(type(value)))

    @property
    def message_id(self) -> str:
        """Get the message ID"""
        return self._message_id

    @message_id.setter
    def message_id(self, value: str):
        """Set the message ID"""
        if value is None:
            # Clear the message ID
            self._message_id = None
        elif type(value) is str:
            if len(value) > 5:
                # The maximum length of a message ID is 5 characters
                raise ValueError(
                    "Message ID length cannot be longer than 5 characters ({} given)".format(
                        len(value)
                    )
                )
            else:
                self._message_id = value
        else:
            raise TypeError("Message ID must be of type 'str' ({} given)".format(type(value)))

    @property
    def bulletin_id(self) -> int:
        """Get the bulletin ID"""
        return self._bulletin_id

    @bulletin_id.setter
    def bulletin_id(self, value: int):
        """Set the bulletin ID"""
        if value is None:
            # Clear the bulletin ID
            self._bulletin_id = None
        elif type(value) is int:
            if 0 <= value <= 9:
                self._bulletin_id = value
            else:
                # The bulletin must be 0 to 9
                raise ValueError(
                    "Bulletin ID must be a value between 0 and 9 inclusive ({} given)".format(
                        value
                    )
                )
        else:
            raise TypeError("Bulletin ID must be of type 'int' ({} given)".format(type(value)))

    @property
    def announcement_id(self) -> str:
        """Get the announcement ID"""
        return self._announcement_id

    @announcement_id.setter
    def announcement_id(self, value: str):
        """Set the announcement ID"""
        if value is None:
            # Clear the announcement ID
            self._announcement_id = None
        elif type(value) is str:
            if len(value) != 1:
                # An announcement ID is a single character
                raise ValueError(
                    "Announcement IDs must be a single character ({} given)".format(len(value)))
            else:
                self._announcement_id = value
        else:
            raise TypeError("Announcement ID must be of type 'str' ({} given)".format(type(value)))

    @property
    def group_bulletin_name(self) -> str:
        """Get the group bulletin name"""
        return self._group_bulletin_name

    @group_bulletin_name.setter
    def group_bulletin_name(self, value: str):
        """Set the group bulletin name"""
        if value is None:
            # Clear the group bulletin name
            self._group_bulletin_name = None
        elif type(value) is str:
            if len(value) > 5:
                # The maximum length of a group bulletin name is 5 characters
                raise ValueError(
                    "Group bulletin names cannot be longer than 5 characters ({} given)".format(
                        len(value)
                    )
                )
            else:
                self._group_bulletin_name = value
        else:
            raise TypeError("Group bulletin name must be of type 'str' ({} given)".format(
                type(value))
            )

    def parse(self) -> bool:
        """
        Parse a message packet.

        The parsed values are stored within the current object.
        """

        # The spec requires ':' at position 9 (9-char addressee), but real-world senders sometimes
        # omit the space padding. Accept ':' anywhere in positions 1–10.
        sep = self._info.find(':')
        if sep < 1 or sep > 10:
            raise ParseError("Invalid message packet (missing : in 9th position)", self)

        # Split the message into the addressee and the actual message
        addressee = self._info[:sep]
        self.addressee = addressee.rstrip()
        message = self._info[sep + 1:]

        logger.debug("Message is addressed to {}, message is {}".format(addressee, message))

        # Is this a bulletin/announcement?
        if addressee[0:3] == "BLN":
            logger.debug("Message is a bulletin")

            if re.match("[0-9]", addressee[3]):
                # Bulletins have the format BLNn or BLNnaaaaa, where n is a digit between 0 and 9
                # and aaaaa is an optional group bulletin identifier
                if addressee[4:9] == "     ":
                    # Bulletin
                    self.bulletin_id = int(addressee[3])
                    logger.debug("Bulletin {}".format(self.bulletin_id))
                else:
                    # Group bulletin
                    self.group_bulletin_name = addressee[4:9].rstrip()
                    self.bulletin_id = int(addressee[3])

                    logger.debug("Group bulletin {} ({})".format(
                        self.group_bulletin_name, self.bulletin_id
                    ))

            elif re.match("[A-Z]", addressee[3]):
                # Announcements have the format BLNa, where a is a character between A and Z
                if addressee[4:].rstrip() == "":
                    # Standard announcement
                    self.announcement_id = addressee[3]
                    logger.debug("Announcement {}".format(self.announcement_id))
                else:
                    # Non-standard: extra chars after the single-letter announcement ID (e.g.
                    # BLNALUX). Treat as announcement, ignore the extra identifier.
                    self.announcement_id = addressee[3]
                    logger.debug("Non-standard announcement: {}".format(addressee))

            elif addressee[3:].rstrip() == "":
                # BLN with no identifier (e.g. "BLN      ") — treat as unnumbered bulletin
                logger.debug("Bulletin with no identifier: {}".format(addressee))

            else:
                # Incorrectly-formatted bulletin
                raise ParseError("Incorrectly-formatted bulletin: {}".format(addressee), self)

        if '{' in message:
            # Check for a message ID; some clients use {ID} with a } terminator
            message, message_id = message.split("{", maxsplit=1)
            if '}' in message_id:
                message_id = message_id[:message_id.index('}')]
            logger.debug("Message has message ID {}".format(message_id))

            # Message IDs must not be longer than 5 characters (C14 P71)
            if len(message_id) > 5:
                raise ParseError("Invalid message ID: {}".format(message_id), self)

            try:
                self.message = message

            except ValueError as e:
                # Message was too long
                raise ParseError("Message too long: {}".format(e))

            self.message_id = message_id
        else:
            try:
                self.message = message

            except ValueError as e:
                # Message was too long
                raise ParseError("Message too long: {}".format(e))

        return True

    @property
    def info(self) -> str:
        """Generate the information field for a message packet (used for packet generation).
        Raw parsed info is stored in _info and accessed directly by parse()."""
        info = ""
        if self.addressee:
            info += self.addressee.ljust(9)
        elif self.group_bulletin_name:
            info += "BLN{}{}".format(self.bulletin_id, self.group_bulletin_name).ljust(9)
        elif self.announcement_id:
            info += "BLN{}".format(self.announcement_id).ljust(9)
        elif self.bulletin_id:
            info += "BLN{}".format(self.bulletin_id).ljust(9)
        else:
            raise GenerateError("No addressee, announcement or bulletin details", self)

        if self.message is not None:
            info += ":{}".format(self.message)
        else:
            raise GenerateError("No message", self)

        if self.message_id:
            info += "{" + self.message_id

        return info

    @info.setter
    def info(self, value: str):
        self._info = value

    def __repr__(self):
        if self.source:
            if self.group_bulletin_name:
                return "<MessagePacket: {} -> Group Bulletin {} #{}>".format(
                    self.source, self.group_bulletin_name, self.bulletin_id
                )
            elif self.bulletin_id:
                return "<MessagePacket: {} -> Bulletin #{}>".format(self.source, self.bulletin_id)
            elif self.announcement_id:
                return "<MessagePacket: {} -> Announcement {}>".format(
                    self.source, self.announcement_id
                )
            elif self.addressee:
                return "<MessagePacket: {} -> {}>".format(self.source, self.addressee)
            else:
                return "<MessagePacket: {}>".format(self.source)
        else:
            return "<MessagePacket>"
