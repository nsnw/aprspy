TEST_PACKET = "XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet"
TEST_SOURCE = "XX1XX"
TEST_DESTINATION = "APRS"
TEST_PATH = "TCPIP*,qAC,FOURTH"
TEST_DATA_TYPE_ID = "="
TEST_INFO = "5030.50N/10020.30W$221/000/A=005Test packet"

VALID_SOURCES = [
    "XX1XX",
    "XX1XX-1",
    "XX1XX-11"
]
INVALID_SOURCES = [
    "ZZZ1ZZZ",
    "ZZZ1ZZZ-1",
    "ZZ1ZZZ-111",
]

VALID_DESTINATIONS = [
    "XX1XX",
    "XX1XX-1",
    "XX1XX-11"
]
INVALID_DESTINATIONS = [
    "ZZZ1ZZZ",
    "ZZZ1ZZZ-1",
    "ZZ1ZZZ-111",
]

VALID_POSITION_WITH_TIMESTAMP_WITH_MESSAGING_PACKETS = [
    # From APRS 1.01 C8 P32.
    # With timestamp, with APRS messaging, local time, with comment.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:@092345/4903.50N/07201.75W>Test1234"
]
VALID_POSITION_WITH_TIMESTAMP_WITHOUT_MESSAGING_PACKETS = [
    # From APRS 1.01 C8 P32.
    # With timestamp, no APRS messaging, UTC time, with comment.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:/092345z4903.50N/07201.75W>Test1234"
]
VALID_POSITION_WITHOUT_TIMESTAMP_WITH_MESSAGING_PACKETS = [
    # From APRS 1.01 C8 P33.
    # Without timestamp, with APRS messaging, with PHG.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:=4903.50N/07201.75W#PHG5132"
]
VALID_POSITION_WITH_X1J_HEADER_PACKETS = [
    # No timestamp, no APRS messaging, with X1J node header.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:TheNet X-1J4  (BFLD)!4903.50N/07201.75Wn",
]
VALID_POSITION_WITHOUT_TIMESTAMP_WITHOUT_MESSAGING_PACKETS = [
    # From APRS 1.01 C8 P32.
    # No timestamp, no APRS messaging, with comment.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:!4903.50N/07201.75W-Test 001234",
    # No timestamp, no APRS messaging, altitude is 1234 ft.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:!4903.50N/07201.75W-Test /A=001234",
    # No timestamp, no APRS messaging, location to nearest degree.
    f"{TEST_SOURCE}>{TEST_DESTINATION},{TEST_PATH}:!49  .  N/072  .  W-",
    *VALID_POSITION_WITH_X1J_HEADER_PACKETS
]
VALID_POSITION_PACKETS = [
    *VALID_POSITION_WITH_TIMESTAMP_WITH_MESSAGING_PACKETS,
    *VALID_POSITION_WITH_TIMESTAMP_WITHOUT_MESSAGING_PACKETS,
    *VALID_POSITION_WITHOUT_TIMESTAMP_WITH_MESSAGING_PACKETS,
    *VALID_POSITION_WITHOUT_TIMESTAMP_WITHOUT_MESSAGING_PACKETS
]

POSITION_TIMESTAMP_MESSAGING_DATA_TYPE_IDS = [
    (True, True, "@"),      # With timestamp, messaging capable
    (True, False, "/"),     # With timestamp, not messaging capable
    (False, True, "="),     # Without timestamp, messaging capable
    (False, False, "!"),    # Without timestamp, not messaging capable
]
