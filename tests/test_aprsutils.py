import pytest

from aprspy.utils import APRSUtils


def test_decode_uncompressed_latitude_without_ambiguity():
    # Test uncompressed latitude without ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("4903.55N")

    assert lat == 49.059167
    assert ambiguity == 0


def test_decode_uncompressed_latitude_with_ambiguity_1():
    # Test uncompressed latitude with 1 level of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("4903.5 N")

    assert lat == 49.058333
    assert ambiguity == 1


def test_decode_uncompressed_latitude_with_ambiguity_2():
    # Test uncompressed latitude with 2 levels of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("4903.  N")

    assert lat == 49.05
    assert ambiguity == 2


def test_decode_uncompressed_latitude_with_ambiguity_3():
    # Test uncompressed latitude with 3 levels of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("490 .  N")

    assert lat == 49
    assert ambiguity == 3


def test_decode_uncompressed_latitude_with_ambiguity_4():
    # Test uncompressed latitude with 4 levels of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("49  .  N")

    assert lat == 49
    assert ambiguity == 4


def test_decode_uncompressed_latitude_invalid_latitude():
    with pytest.raises(ValueError):
        # 91 degrees north is not a valid latitude
        APRSUtils.decode_uncompressed_latitude("9100.00N")


def test_decode_uncompressed_latitude_invalid_direction():
    with pytest.raises(ValueError):
        # West is not a valid latitude direction
        APRSUtils.decode_uncompressed_latitude("4903.50W")


def test_decode_uncompressed_latitude_malformed_latitude():
    with pytest.raises(ValueError):
        # Period is in the wrong position
        APRSUtils.decode_uncompressed_latitude("49035.0N")


def test_decode_uncompressed_latitude_invalid_ambiguity():
    with pytest.raises(ValueError):
        # >4 units of ambiguity is invalid for latitude
        APRSUtils.decode_uncompressed_latitude("5   . N")


def test_decode_uncompressed_latitude_complete_garbage():
    with pytest.raises(ValueError):
        # Random garbage
        APRSUtils.decode_uncompressed_latitude("GARBAGE")


def test_encode_uncompressed_latitude_without_ambiguity():
    # Test latitude
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821)
    assert latitude == "5128.43N"


def test_encode_uncompressed_latitude_with_ambiguity_1():
    # Test latitude with differing levels of ambiguity
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 1)
    assert latitude == "5128.4 N"


def test_encode_uncompressed_latitude_with_ambiguity_2():
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 2)
    assert latitude == "5128.  N"


def test_encode_uncompressed_latitude_with_ambiguity_3():
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 3)
    assert latitude == "512 .  N"


def test_encode_uncompressed_latitude_with_ambiguity_4():
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 4)
    assert latitude == "51  .  N"


def test_encode_uncompressed_latitude_with_int():
    # ints are allowed too
    latitude = APRSUtils.encode_uncompressed_latitude(51)
    assert latitude == "5100.00N"


def test_encode_uncompressed_latitude_with_southern_latitude():
    # Ensure that southern latitudes work
    latitude = APRSUtils.encode_uncompressed_latitude(-51)
    assert latitude == "5100.00S"


def test_encode_uncompressed_latitude_with_incorrect_latitude_type():
    with pytest.raises(TypeError):
        # Must be a float or int
        APRSUtils.encode_uncompressed_latitude("51")


def test_encode_uncompressed_latitude_with_invalid_latitude():
    with pytest.raises(ValueError):
        # Must be be between -90 and 90
        APRSUtils.encode_uncompressed_latitude(91)


def test_encode_uncompressed_latitude_with_incorrect_ambiguity_type():
    with pytest.raises(TypeError):
        # Ambiguity must be an int
        APRSUtils.encode_uncompressed_latitude(51, "1")


def test_encode_uncompressed_latitude_with_invalid_ambiguity():
    with pytest.raises(ValueError):
        # ...and it must be be between 0 and 4
        APRSUtils.encode_uncompressed_latitude(51, 5)


def test_decode_uncompressed_longitude_without_ambiguity():
    # Test uncompressed longitude without ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W")

    assert lng == -72.195833


def test_decode_uncompressed_longitude_with_ambiguity_1():
    # Test uncompressed longitude with 1 level of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 1)

    assert lng == -72.195


def test_decode_uncompressed_longitude_with_ambiguity_2():
    # Test uncompressed longitude with 2 levels of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 2)

    assert lng == -72.183333


def test_decode_uncompressed_longitude_with_ambiguity_3():
    # Test uncompressed longitude with 3 levels of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 3)

    assert lng == -72.166667


def test_decode_uncompressed_longitude_with_ambiguity_4():
    # Test uncompressed longitude with 4 levels of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 4)

    assert lng == -72.0


def test_decode_uncompressed_longitude_invalid_longitude():
    with pytest.raises(ValueError):
        # 181 degrees west is not a valid longitude
        APRSUtils.decode_uncompressed_longitude("18100.00W")


def test_decode_uncompressed_longitude_invalid_direction():
    with pytest.raises(ValueError):
        # North is not a valid longitude direction
        APRSUtils.decode_uncompressed_longitude("07201.75N")


def test_decode_uncompressed_longitude_malformed_longitude():
    with pytest.raises(ValueError):
        # Period is in the wrong position
        APRSUtils.decode_uncompressed_longitude("072017.5N")


def test_decode_uncompressed_longitude_invalid_ambiguity():
    with pytest.raises(ValueError):
        # Ambiguity must be 1-4
        APRSUtils.decode_uncompressed_longitude("07201.75W", 5)


def test_decode_uncompressed_longitude_complete_garbage():
    with pytest.raises(ValueError):
        # Random garbage
        APRSUtils.decode_uncompressed_longitude("GARBAGE")


def test_encode_uncompressed_longitude_without_ambiguity():
    # Test longitude
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325)
    assert longitude == "11426.06W"


def test_encode_uncompressed_longitude_with_ambiguity_1():
    # Test longitude with differing levels of ambiguity
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 1)
    assert longitude == "11426.0 W"


def test_encode_uncompressed_longitude_with_ambiguity_2():
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 2)
    assert longitude == "11426.  W"


def test_encode_uncompressed_longitude_with_ambiguity_3():
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 3)
    assert longitude == "1142 .  W"


def test_encode_uncompressed_longitude_with_ambiguity_4():
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 4)
    assert longitude == "114  .  W"


def test_encode_uncompressed_longitude_with_eastern_direction():
    # Test eastern latitudes too
    longitude = APRSUtils.encode_uncompressed_longitude(114.434325, 4)
    assert longitude == "114  .  E"


def test_encode_uncompressed_longitude_incorrect_longitude_type():
    with pytest.raises(TypeError):
        # Must be a float or int
        APRSUtils.encode_uncompressed_longitude("114")


def test_encode_uncompressed_longitude_invalid_longitude():
    with pytest.raises(ValueError):
        # Must be be between -180 and 180
        APRSUtils.encode_uncompressed_longitude(181)


def test_encode_uncompressed_longitude_incorrect_ambiguity_type():
    with pytest.raises(TypeError):
        # Ambiguity must be an int
        APRSUtils.encode_uncompressed_longitude(114, "1")


def test_encode_uncompressed_longitude_invalid_ambiguity():
    with pytest.raises(ValueError):
        # ...and it must be be between 0 and 4
        APRSUtils.encode_uncompressed_longitude(114, 5)


def test_decode_compressed_latitude():
    # Test compressed latitude
    lat = APRSUtils.decode_compressed_latitude("5L!!")

    assert lat == 49.5


def test_decode_compressed_latitude_invalid_latitude():
    with pytest.raises(ValueError):
        # Length must be 4
        APRSUtils.decode_compressed_latitude("5L!!!")


def test_decode_compressed_longitude():
    # Test compressed longitude
    lng = APRSUtils.decode_compressed_longitude("<*e7")

    assert lng == -72.750004


def test_decode_compressed_longitude_invalid_longitude():
    with pytest.raises(ValueError):
        # Length must be 4
        APRSUtils.decode_compressed_latitude("<*e77")
