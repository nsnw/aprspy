#!/usr/bin/env python

import re
import logging
import math

from datetime import datetime, timedelta

from typing import Union, Tuple, Optional

from .exceptions import ParseError

# Set up logging
logger = logging.getLogger(__name__)


class APRSUtils:
    """
    Useful generic functions for APRS parsing and decoding.

    This class provides functions for parsing and decoding different kinds of APRS packets.
    Packet type-specific functions are defined under the different :class:`APRSPacket` subclasses.
    """
    @staticmethod
    def _get_utc():
        return datetime.utcnow()

    @staticmethod
    def decode_uncompressed_latitude(latitude: str) -> Tuple[Union[int, float], int]:
        """
        Convert an uncompressed latitude string to a latitude and an ambiguity
        value.

        :param str latitude: an uncompressed latitude, in the form ``DDMM.HHC``

        Uncompressed latitudes have the format DDMM.HHC, where:-
         * DD are the degrees
         * MM are the minutes
         * HH are the hundredths of minutes
         * C is either N (for the northern hemisphere) or S (southern)

        MM and HH can be replaced with spaces (" ") to provide positional
        ambiguity (C6 P24).

        See also APRS 1.01 C6 P23.
        """
        logger.debug("Input latitude: {}".format(latitude))

        # Regex match to catch any obviously-invalid latitudes
        if not re.match(r'^[0-9]{2}[\s0-9]{2}\.[\s0-9]{2}[NS]$', latitude):
            raise ValueError("Invalid latitude: {}".format(latitude))

        # Determine the level of ambiguity, and replace the spaces with zeroes
        # See C6 P24
        ambiguity = latitude.count(' ')
        latitude = latitude.replace(' ', '0')
        logger.debug("Ambiguity: {}".format(ambiguity))

        try:
            # Extract the number of degrees
            degrees = int(latitude[:2])
            if degrees > 90:
                raise ValueError("Invalid degrees: {}".format(degrees))

            logger.debug("Degrees: {}".format(degrees))

            # Extract the number of minutes, convert it to a fraction of a degree,
            # and round it to 6 decimal places
            minutes = round(float(latitude[2:-1])/60, 6)
            logger.debug("Minutes: {}".format(minutes))

            # Extract the north/south
            direction = latitude[-1]
            logger.debug("Direction: {}".format(direction))

        except Exception as e:
            raise ParseError("Couldn't parse latitude {}: {}".format(
                latitude, e
            ))

        # Add the degrees and minutes to give the latitude
        lat = degrees + minutes

        # If the latitude is south of the equator, make it negative
        if direction == "S":
            lat *= -1

        logger.debug("Output latitude: {}, ambiguity: {}".format(
            lat, ambiguity
        ))
        return (lat, ambiguity)

    @staticmethod
    def encode_uncompressed_latitude(latitude: Union[float, int], ambiguity: int = 0) -> str:
        """
        Encode a latitude into an uncompressed latitude format.

        :param float/int latitude: a latitude
        :param int ambiguity: an optional ambiguity level

        For more information see :func:`decode_uncompressed_latitude`
        """

        # The latitude must be a float
        if type(latitude) is not float:
            if type(latitude) is int:
                latitude = float(latitude)
            else:
                raise TypeError("Latitude must be an float ({} given)".format(type(latitude)))

        # The latitude must be between -90 and 90 inclusive
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 inclusive ({} given)".format(
                latitude
            ))

        # The ambiguity must be an int
        if ambiguity and type(ambiguity) is not int:
            raise TypeError("Ambiguity must be an int ({} given)".format(type(ambiguity)))

        # The ambiguity must be between 0 and 4 inclusive
        if ambiguity < 0 or ambiguity > 4:
            raise ValueError("Ambiguity must be between 0 and 4 inclusive ({} given)".format(
                ambiguity
            ))

        # Determine if the latitude is north or south
        if latitude < 0:
            # Direction is south
            direction = "S"
            latitude *= -1
        else:
            direction = "N"

        # Get the degrees of latitude
        degrees = math.floor(latitude)

        # Get the minutes of latitude
        minutes = "{:0.2f}".format(round((latitude - degrees) * 60, 2)).zfill(5)

        # Apply ambiguity
        if ambiguity == 0:
            lat = "{}{}".format(degrees, minutes)
        elif ambiguity == 1:
            lat = "{}{} ".format(degrees, minutes[:-1])
        elif ambiguity == 2:
            lat = "{}{}  ".format(degrees, minutes[:-2])
        elif ambiguity == 3:
            lat = "{}{} .  ".format(degrees, minutes[:-4])
        elif ambiguity == 4:
            lat = "{}  .  ".format(degrees)

        return f"{lat}{direction}"

    @staticmethod
    def encode_uncompressed_longitude(longitude: float, ambiguity: int = 0) -> str:
        """
        Encode a longitude into an uncompressed longitude format.

        :param float longitude: a longitude
        :param int ambiguity: an optional ambiguity level

        For more information see :func:`decode_uncompressed_latitude`
        """

        # The longitude must be a float
        if type(longitude) is not float:
            if type(longitude) is int:
                longitude = float(longitude)
            else:
                raise TypeError("Longitude must be a float ({} given)".format(type(longitude)))

        # The longitude must be between -180 and 180 inclusive
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 inclusive ({} given)".format(
                longitude
            ))

        # The ambiguity must be an int
        if ambiguity and type(ambiguity) is not int:
            raise TypeError("Ambiguity must be an int ({} given)".format(type(ambiguity)))

        # The ambiguity must be between 0 and 4 inclusive
        if ambiguity < 0 or ambiguity > 4:
            raise ValueError("Ambiguity must be between 0 and 4 inclusive ({} given)".format(
                ambiguity
            ))

        # Determine if the longitude is east or west
        if longitude < 0:
            # Direction is south
            direction = "W"
            longitude *= -1
        else:
            direction = "E"

        # Get the degrees of longitude
        degrees = math.floor(longitude)

        # Get the minutes of longitude
        minutes = "{:0.2f}".format(round((longitude - degrees) * 60, 2)).zfill(5)

        # Apply ambiguity
        if ambiguity == 0:
            lng = "{}{}".format(degrees, minutes)
        elif ambiguity == 1:
            lng = "{}{} ".format(degrees, minutes[:-1])
        elif ambiguity == 2:
            lng = "{}{}  ".format(degrees, minutes[:-2])
        elif ambiguity == 3:
            lng = "{}{} .  ".format(degrees, minutes[:-4])
        elif ambiguity == 4:
            lng = "{}  .  ".format(degrees)

        return f"{lng}{direction}"

    @staticmethod
    def decode_uncompressed_longitude(longitude: str, ambiguity: int = 0) -> float:
        """
        Convert an uncompressed longitude string to a longitude value, with an
        optional ambiguity level applied.

        :param str longitude: the longitude, in the format ``DDDMM.HHC``
        :param int ambiguity: the level of ambiguity, between 1 and 4

        Uncompressed longitudes have the format DDDMM.HHC, where:-
         * DD are the degrees
         * MM are the minutes
         * HH are the hundreths of minutes
         * C is either W (for west of the meridian) or E (for east)

        Positional ambiguity is handled by the latitude, and so should be
        honoured regardless of the precision of the longitude given (as per C6 P24).
        """
        logger.debug("Input longitude: {}, ambiguity: {}".format(
            longitude, ambiguity
        ))

        # Regex match to catch any obviously-invalid longitudes
        if not re.match(r'^[0-1][0-9]{2}[\s0-9]{2}\.[\s0-9]{2}[EW]$', longitude):
            raise ValueError("Invalid longitude: {}".format(longitude))

        # If the ambiguity value is more than 0, replace longitude digits with
        # spaces as required.
        if 0 <= ambiguity <= 4:
            longitude = longitude.replace(' ', '0')
        else:
            raise ValueError("Invalid ambiguity level: {} (maximum is 4)".format(
                ambiguity
            ))

        # Extract the number of degrees
        degrees = int(longitude[:3])
        if degrees > 180:
            raise ValueError("Invalid degrees: {}".format(degrees))

        logger.debug("Degrees: {}".format(degrees))

        # Since we don't want to replace the '.', if the ambiguity is more than
        # 2, increment it by 1.
        if ambiguity > 2:
            ambiguity_level = ambiguity + 1
        else:
            ambiguity_level = ambiguity

        # Extract the number of minutes, and round it to 6 decimal places
        if ambiguity == 1:
            mins = longitude[3:-2] + "0"
        elif ambiguity == 2:
            mins = longitude[3:-3] + "00"
        elif ambiguity == 3:
            mins = longitude[3:-5] + "0.00"
        elif ambiguity == 4:
            mins = longitude[3:-6] + "00.00"
        else:
            mins = longitude[3:-1]

        minutes = round(float(mins)/60, 6)
        logger.debug("Ambiguity level: {}".format(ambiguity_level))
        logger.debug("Minutes: {}".format(minutes))

        # Extract the east/west
        direction = longitude[-1]

        logger.debug("Direction: {}".format(direction))

        # Add the degrees and minutes to give the longitude
        lng = degrees + minutes

        # If the longitude is west of the meridian, make it negative
        if direction == "W":
            lng *= -1

        logger.debug("Output longitude: {}".format(lng))
        return lng

    @staticmethod
    def decode_compressed_latitude(latitude: str) -> float:
        """
        Convert a compressed latitude string to a latitude value.

        :param str latitude: a latitude in a compressed format

        Compressed latitudes have the format YYYY, where all values are base-91
        printable ASCII characters.

        See also APRS 1.01 C9 P38.
        """
        logger.debug("Input compressed latitude: {}".format(latitude))

        # The compressed latitude string must be 4 characters
        if len(latitude) != 4:
            raise ValueError("Input compressed latitude must be 4 characters ({} given)".format(
                len(latitude)
            ))

        # As per APRS 1.01, if the compressed latitude is y1y2y3y4, the latitude
        # can be determined with:-
        # 90 - ((y1-33) x 913 + (y2-33) x 912 + (y3-33) x 91 + y4-33) / 380926
        lat = 90 - (
            (ord(latitude[0])-33) * 91**3 +
            (ord(latitude[1])-33) * 91**2 +
            (ord(latitude[2])-33) * 91 +
            (ord(latitude[3])-33)
        ) / 380926
        lat = round(lat, 6)

        if lat > 90 or lat < -91:
            raise ParseError("Invalid compressed latitude (greater than 90 or less than -90)")

        # Return latitude
        logger.debug("Output latitude: {}".format(lat))
        return lat

    @staticmethod
    def decode_compressed_longitude(longitude: str) -> float:
        """
        Convert a compressed longitude string to a latitude value.

        :param str longitude: a longitude in compressed format

        Compressed longitude have the format XXXX, where all values are base-91
        printable ASCII characters

        See also APRS 1.01 C9 P38
        """
        logger.debug("Input compressed longitude: {}".format(longitude))

        # The compressed longitude must be 4 characters
        if len(longitude) != 4:
            raise ValueError("Input compressed longitude must be 4 characters ({} given)".format(
                len(longitude)
            ))

        # If the compressed longitude is x1x2x3x4, the longitude can be determined
        # with:-
        # -180 + ((x1-33) x 913 + (x2-33) x 912  + (x3-33) x 91 + x4-33) / 190463
        lng = -180 + (
            (ord(longitude[0])-33) * 91**3 +
            (ord(longitude[1])-33) * 91**2 +
            (ord(longitude[2])-33) * 91 +
            (ord(longitude[3])-33)
        ) / 190463
        lng = round(lng, 6)

        if lng > 180 or lng < -180:
            raise ParseError("Invalid compressed longitude (greater than 180 or less than -180)")

        # Return longitude
        logger.debug("Output longitude: {}".format(lng))
        return lng

    @staticmethod
    def encode_compressed_latitude(latitude: Union[float, int]) -> str:
        """
        Convert a latitude to a compressed latitude value.

        :param float/int latitude: a latitude

        Compressed latitudes have the format YYYY, where all values are base-91
        printable ASCII characters.

        See also APRS 1.01 C9 P38.
        """
        logger.debug("Input latitude: {}".format(latitude))

        # Ensure float or int, and between -90 and 90
        if type(latitude) is not float and type(latitude) is not int:
            raise TypeError("Latitude must be a 'float' or 'int' ({} given)".format(type(latitude)))

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 ({} given)".format(latitude))

        total = 380926 * (90 - latitude)
        (a, remainder) = divmod(total, 91 ** 3)
        (b, remainder) = divmod(remainder, 91 ** 2)
        (c, d) = divmod(remainder, 91 ** 1)

        lat = "{}{}{}{}".format(
            chr(int(a)+33),
            chr(int(b)+33),
            chr(int(c)+33),
            chr(int(d)+33)
        )

        # Return latitude
        logger.debug("Output latitude: {}".format(lat))
        return lat

    @staticmethod
    def encode_compressed_longitude(longitude: Union[float, int]) -> str:
        """
        Convert a longitude to a compressed latitude value.

        :param float/int longitude: a longitude

        Compressed longitude have the format XXXX, where all values are base-91
        printable ASCII characters

        See also APRS 1.01 C9 P38
        """
        logger.debug("Input longitude: {}".format(longitude))

        # Ensure float or int, and between -180 and 180
        if type(longitude) is not float and type(longitude) is not int:
            raise TypeError("Longitude must be a 'float' or 'int' ({} given)".format(
                type(longitude)
            ))

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180 ({} given)".format(longitude))

        total = 190463 * (180 + longitude)
        (a, remainder) = divmod(total, 91 ** 3)
        (b, remainder) = divmod(remainder, 91 ** 2)
        (c, d) = divmod(remainder, 91 ** 1)

        lng = "{}{}{}{}".format(
            chr(int(a)+33),
            chr(int(b)+33),
            chr(int(c)+33),
            chr(int(d)+33)
        )

        # Return longitude
        logger.debug("Output longitude: {}".format(lng))
        return lng

    @staticmethod
    def decode_timestamp(raw_timestamp: str) -> datetime:
        """
        Decode a timestamp.

        :param str raw_timestamp: a string representing a timestamp

        Timestamps can take a number of different forms:-
         * Zulu, identified with a trailing 'z', which refers to zulu time
         * Local, identified with a trailing '/', which has no timezone information
         * A hour/minute/second timestamp without any date information
        """

        logger.debug("Raw timestamp is {}".format(raw_timestamp))
        ts = re.match(r'^(\d{6})(.)', raw_timestamp)
        if ts:
            timestamp, timestamp_type = ts.groups()

            # Parse the timestamp type
            # APRS 1.01 specifies 'z' for zulu time, but some clients use 'Z'
            if timestamp_type == 'z' or timestamp_type == 'Z':
                timestamp_type = 'zulu'
                logger.debug("Timestamp is zulu time")
            elif timestamp_type == '/':
                timestamp_type = 'local'
                logger.debug("Timestamp is local time")
            elif timestamp_type == 'h':
                timestamp_type = 'hms'
                logger.debug("Timestamp is hhmmss time")
            else:
                # This is against spec, but as usual with APRS a lot of clients violate this - so
                # assume they're zulu time
                logger.warning("{} is an invalid timestamp type, assuming zulu".format(timestamp_type))
                timestamp_type = 'zulu'

            # Get the current UTC ('zulu') time for comparison. Since timestamps in HHMMSS format
            # have no date information, we need to determine if the timestamp is for today or
            # yesterday
            utc = APRSUtils._get_utc()

            if timestamp_type == 'hms':
                # HHMMSS format

                # Parse out the hour, minute and second
                hour = int(timestamp[0:2])
                minute = int(timestamp[2:4])
                second = int(timestamp[4:6])

                try:
                    # Generate a datetime object
                    ts = datetime(utc.year, utc.month, utc.day, hour, minute, second)
                except ValueError as e:
                    logger.error("Error parsing timestamp '{}': {}".format(raw_timestamp, e))
                    raise ParseError("Error parsing timestamp '{}': {}".format(raw_timestamp, e))

                # Check it's not in the future
                if ts > utc:
                    # The timestamp is in the future, so go back a day
                    ts -= timedelta(days=1)

                # Convert to seconds
                timestamp = int(ts.timestamp())
                logger.debug("Timestamp is {}".format(ts.strftime("%Y%m%d%H%M%S")))

            elif timestamp_type == 'zulu' or timestamp_type == 'local':
                if timestamp_type == 'local':
                    # Assume local time is zulu time
                    # NOTE: this is against the spec, but without knowing the local
                    # timezone, it's impossible to work out. APRS 1.01 C6 P22 states "It is
                    # recommended that future APRS implementations only transmit zulu format on the
                    # air", so hopefully this shouldn't be a problem in reality.
                    logger.info("Local time specified in timestamp, assuming UTC.")

                # Sometimes, 000000 is used to indicate no timestamp is available
                if timestamp[0:6] == "000000":
                    logger.warning("Timestamp specified but is set to all zeroes.")
                    return None, timestamp_type

                # DDHHMM
                day = int(timestamp[0:2])
                hour = int(timestamp[2:4])
                minute = int(timestamp[4:6])

                # TODO - handle broken timestamps a bit nicer
                try:
                    ts = datetime(utc.year, utc.month, day, hour, minute, 0)
                except ValueError as e:
                    logger.warning("Error parsing timestamp '{}': {}".format(timestamp, e))
                    raise ParseError("Error parsing timestamp '{}': {}".format(timestamp, e))

                # Check it's not in the future
                if ts > utc:
                    logger.debug("Timestamp day in previous month.")
                    # The time is in the future, so go back a month
                    # timedelta doesn't support subtracting months, so here be
                    # dirty hacks.
                    if 1 < ts.month <= 12:
                        month = ts.month - 1
                        ts = datetime(utc.year, month, day, hour, minute, 0)
                    elif ts.month == 1:
                        year = ts.year - 1
                        month = 12
                        ts = datetime(year, month, day, hour, minute, 0)

                # Convert to seconds
                logger.debug("Timestamp is {}".format(ts.strftime("%Y%m%d%H%M%S")))

            return ts, timestamp_type

        else:
            raise ParseError("No valid timestamp found")

    @staticmethod
    def encode_timestamp(timestamp: datetime, timestamp_type: str = "zulu") -> str:
        """
        Encode a timestamp.

        :param datetime timestamp: a timestamp
        :param str timestamp_type: the timestamp type (`zulu`, `hms` or `local`)
        """
        if type(timestamp) is not datetime:
            raise TypeError("Timestamp must be of type 'datetime' ({} given)".format(
                type(timestamp)
            ))

        if timestamp_type == "zulu":
            return "{}{}{}z".format(
                str(timestamp.day).zfill(2),
                str(timestamp.hour).zfill(2),
                str(timestamp.minute).zfill(2)
            )
        elif timestamp_type == "local":
            return "{}{}{}/".format(
                str(timestamp.day).zfill(2),
                str(timestamp.hour).zfill(2),
                str(timestamp.minute).zfill(2)
            )
        elif timestamp_type == "hms":
            return "{}{}{}h".format(
                str(timestamp.hour).zfill(2),
                str(timestamp.minute).zfill(2),
                str(timestamp.second).zfill(2)
            )
        else:
            raise ValueError(
                "Timestamp type must be one of 'zulu', 'hms' or 'local' ({} given)".format(
                    timestamp_type
                )
            )

    @staticmethod
    def decode_phg(phg: str) -> Tuple[int, int, int, Optional[int]]:
        """
        Decode a PHG (Power, Effective Antenna Height/Gain/Directivity) value and return the
        individual values.

        :param str phg: a PHG value, minus the initial ``PHG`` identifier

        The PHG extension provides a way of specifying approximate values for:-
         * Power (in watts)
         * Height above average local terrain (in feet)
         * Antenna gain (in dB)
         * Directivity (in degrees)

        PHG values are 4 characters long, and each digit is responsible for one of the above values.
        As per the APRS spec, the height value can be any ASCII character from 0 upwards.

        See APRS 1.01 C7 P28
        """

        # Ensure this is a valid PHG value
        if not re.match(r'^[0-9]\w[0-9]{2}$', phg):
            raise ValueError(f"Invalid PHG value: {phg}")

        # Decode the power value
        # To get this, we square the value
        power = int(phg[0])**2
        logger.debug(f"Power is {power} watts")

        # Decode the height value
        # To get this, we raise 2 to the power of the ASCII value of the character, minus 48, then
        # times it by 10
        height = (2 ** (ord(phg[1])-48)) * 10
        logger.debug(f"Height is {height} feet")

        # Decode the gain value
        # The gain is just the digit, in dB
        gain = int(phg[2])
        logger.debug(f"Gain is {gain}dB")

        # Decode the directivity
        # The directivity is 360 divided by 8, times the directivity value
        # A value of 0 implies an omnidirectional antenna
        if int(phg[3]) == 0:
            directivity = None
            logger.debug(f"Directivity is omnidirectional")
        else:
            directivity = int((360/8) * int(phg[3]))
            logger.debug(f"Directivity is {directivity} degrees")

        return (power, height, gain, directivity)

    @staticmethod
    def encode_phg(power: int, height: int, gain: int, directivity: Union[int, str]) -> str:
        """
        Encode a PHG (Power, Effective Antenna Height/Gain/Directivity) value from individual
        values.

        :param int power: the power, in watts
        :param int height: the antenna height, in feet
        :param int gain: the antenna gain, in dB
        :param int/str directivity: the antenna directivity, in degrees

        For more information, see :func:`decode_phg`.
        """

        # Validate the given values
        # Power must be a value between 0 to 9 squared
        if type(power) is not int:
            raise TypeError("Power must be of type 'int' ({} given)".format(type(power)))
        elif power not in [v ** 2 for v in range(0, 10)]:
            raise ValueError("Power must be one of {} ({} given)".format(
                [v ** 2 for v in range(0, 10)], power
            ))
        else:
            p = int(math.sqrt(power))
            logger.debug(f"Encoded power {power} is {p}")

        # Antenna height must be a value that is 2 raised to the power of the ASCII value higher
        # than or equal to '0' minus 48, then multiplied by 10
        if type(height) is not int:
            raise TypeError("Height must be of type 'int' ({} given)".format(type(height)))
        elif height not in [(2 ** (v-48))*10 for v in range(48, 127)]:
            raise ValueError("Height must be one of {} ({} given)".format(
                [(2 ** (v-48))*10 for v in range(48, 127)], height
            ))
        else:
            h = chr(int((math.log((height/10), 2)+48)))

        # Antenna gain must be a number between 0 and 9 inclusive
        if type(gain) is not int:
            raise TypeError("Gain must be of type 'int' ({} given)".format(type(gain)))
        elif not 0 <= gain <= 9:
            raise ValueError("Gain must be between 0 and 9 inclusive ({} given)".format(
                gain
            ))
        else:
            g = gain

        # Directivity must be a multiple of 45
        if directivity is None:
            d = 0
        elif type(directivity) is int:
            if directivity % (360/8) != 0.0:
                raise ValueError("Directivity must be a multiple of 45 ({} given)".format(
                    directivity
                ))
            else:
                d = int(directivity / 45)
        else:
            raise TypeError(
                "Directivity must either be of type 'int' or None ({} given)".format(
                    type(directivity)
                ))

        # Return the encoded PHG value
        return f"{p}{h}{g}{d}"

    @staticmethod
    def decode_dfs(dfs: str) -> Tuple[int, int, int, Optional[int]]:
        """
        Decode a DFS (Omni-DF Signal Strength) value and return the individual values.

        :param str dfs: a DFS value, minus the initial ``DFS`` identifier

        The DFS extension provides a way of specifying approximate values for:-
         * Received signal strength (in S-points)
         * Antenna height above average terrain (in feet)
         * Antenna gain (in dB)
         * Directivity (in degrees)

        Like PHG values, DFS values are 4 characters long, and each digit is responsible for one of
        the above values. The APRS spec does not specify it, but it is assumed that - like the PHG
        value - the antenna height can be any ASCII value from 0 upwards.

        See APRS 1.01 C7 P29
        """

        # Ensure this is a valid DFS value
        if not re.match(r'^[0-9]\w[0-9]{2}$', dfs):
            raise ValueError(f"Invalid DFS value: {dfs}")

        # Decode the strength value
        # This just the digit, in dB
        strength = int(dfs[0])
        logger.debug(f"Strength is S{strength}")

        # Decode the height value
        # To get this, we raise 2 to the power of the ASCII value of the character, minus 48, then
        # times it by 10
        height = (2 ** (ord(dfs[1])-48)) * 10
        logger.debug(f"Height is {height} feet")

        # Decode the gain value
        # The gain is just the digit, in dB
        gain = int(dfs[2])
        logger.debug(f"Gain is {gain}dB")

        # Decode the directivity
        # The directivity is 360 divided by 8, times the directivity value
        # A value of 0 implies an omnidirectional antenna
        if int(dfs[3]) == 0:
            directivity = None
            logger.debug(f"Directivity is omnidirectional")
        else:
            directivity = (360/8) * int(dfs[3])
            logger.debug(f"Directivity is {directivity} degrees")

        return (strength, height, gain, directivity)

    @staticmethod
    def encode_dfs(strength: int, height: int, gain: int, directivity: int = None) -> str:
        """
        Encode a DFS (Omni-DF Signal Strength) value from individual values.

        :param int strength: the received signal strength, in S-points
        :param int height: the antenna height, in feet
        :param int gain: the antenna gain, in dB
        :param int/str directivity: the antenna directivity, in degrees, or ``omni``

        For more information, see :func:`decode_dfs`.
        """

        # Signal strength must be a digit between 0 and 9 inclusive

        if type(strength) is not int:
            raise TypeError("Signal strength must be of type 'int' ({} given)".format(
                type(strength)
            ))
        elif not 0 <= strength <= 9:
            raise ValueError(
                "Signal strength must be between 0 and 9 inclusive ({} given)".format(
                    strength
                ))
        else:
            s = strength

        # Antenna height must be a value that is 2 raised to the power of the ASCII value higher
        # than or equal to '0' minus 48, then multiplied by 10
        if type(height) is not int:
            raise TypeError("Height must be of type 'int' ({} given)".format(type(height)))
        elif height not in [(2 ** (v-48))*10 for v in range(48, 127)]:
            raise ValueError("Height must be one of {} ({} given)".format(
                [(2 ** (v-48))*10 for v in range(48, 127)], height
            ))
        else:
            h = chr(int((math.log((height/10), 2)+48)))

        # Antenna gain must be a number between 0 and 9 inclusive
        if type(gain) is not int:
            raise TypeError("Gain must be of type 'int' ({} given)".format(type(gain)))
        if not 0 <= gain <= 9:
            raise ValueError("Gain must be between 0 and 9 inclusive ({} given)".format(
                gain
            ))
        else:
            g = gain

        # Directivity must be a multiple of 45
        if directivity is None:
            d = 0
        elif type(directivity) is int:
            if directivity % (360/8) != 0.0:
                raise ValueError("Directivity must be a multiple of 45 ({} given)".format(
                    directivity
                ))
            else:
                d = int(directivity / 45)
        else:
            raise TypeError(
                "Directivity must either be of type 'int' or None ({} given)".format(
                    type(directivity)
                ))

        return f"{s}{h}{g}{d}"

    @staticmethod
    def decode_nrq(nrq: str) -> Tuple[Optional[Union[float, str]], Optional[int], Optional[int]]:
        """
        Parse an NRQ (Number/Range/Quality) value and return the individual values.

        :param str nrq: an NRQ value

        For direction-finding reports, the NRQ value provides:-
         * The number of hits per period relative to the length of the time period (as a percentage)
         * The range (in miles)
         * The bearing accuracy (in degrees)

        NRQ values are 3 digits long, and all digits from 0 to 9. An 'N' value of 0 implies that the
        rest of the values are meaningless. An 'N' value of 9 indicates that the report is manual.

        The bearing accuracy represents the degree of accuracy, so a 'Q' value of 3 is 64, meaning
        that the accuracy is to less than 64 degrees.

        See APRS 1.01 C7 P30
        """

        # Ensure this is a valid NRQ value
        if not re.match(r'^[0-9]{3}$', nrq):
            raise ValueError(f"Invalid NRQ value: {nrq}")

        # Decode the number of hits
        # We can get this by dividing 100 / 8, then multiplying by the value
        if nrq[0] == "0":
            number = None
            rng = None
            quality = None
        else:
            if nrq[0] == "9":
                number = "manual"
                logger.debug(f"NRQ value is manually reported")
            else:
                number = (100/8) * int(nrq[0])
                logger.debug(f"Number of hits is {number}%")

            # The range is 2 to the power of the range value
            rng = 2 ** int(nrq[1])
            logger.debug(f"Range is {rng} miles")

            # The quality is in degrees. 9 through 3 double the value each time, starting at 1.
            # 2 and 1 are 120 and 240 respectively. 0 implies a useless quality level.
            if int(nrq[2]) > 2:
                quality = 2 ** (9-int(nrq[2]))
            elif int(nrq[2]) == 2:
                quality = 120
            elif int(nrq[2]) == 1:
                quality = 240
            else:
                quality = None

            if quality:
                logger.debug(f"Bearing accuracy is < {quality} degrees")
            else:
                logger.debug("Bearing accuracy is useless")

        return (number, rng, quality)

    @staticmethod
    def generate_passcode(callsign: str) -> str:
        """
        Generate an APRS-IS passcode for a given callsign.

        :param str callsign: a callsign, with or without an SSID

        This will generate an APRS-IS passcode for a callsign, after stripping the SSID (if given).
        """
        # Initialise the passcode with 0x73e2
        passcode = 0x73e2

        # Strip the SSID off the callsign, and convert it to uppercase
        base_call = callsign.split("-")[0].upper()

        # The algorithm XORs each character of the callsign with the passcode, alternating between
        # shifting the ASCII value 8 bits to the left
        high = True
        for c in base_call:
            if high:
                passcode ^= (ord(c) << 8)
                high = False
            else:
                passcode ^= ord(c)
                high = True

        # Return the passcode as a string
        return str(passcode)

    @classmethod
    def validate_passcode(cls, callsign: str, passcode: str) -> bool:
        """
        Validate an APRS-IS passcode for a given callsign.

        :param str callsign: a callsign, with or without an SSID
        :param str passcode: a passcode

        This will generate a passcode for the given callsign, and compare it to the provided
        passcode.
        """
        # Strip the SSID off the callsign, and convert it to uppercase
        base_call = callsign.split("-")[0].upper()

        # Generate a passcode for the given callsign
        generated_passcode = cls.generate_passcode(base_call)

        # Check to see if it matches the passcode we generated
        if passcode == generated_passcode:
            # Passcode matches
            return True
        else:
            # Passcode does not match
            return False
