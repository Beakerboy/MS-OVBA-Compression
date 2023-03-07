import pytest
from ms_ovba_compression.ms_ovba import MsOvba


ceil_log2_data = [
    (1, 4),
    (2, 4),
    (3, 4),
    (4, 4),
    (9, 4),
    (17, 5),
    (50, 6),
]


@pytest.mark.parametrize("input, expected", ceil_log2_data)
def test_ciel_log2(input, expected):
    assert MsOvba.ceilLog2(input) == expected


packCopyTokenData = [
    ([3, 8, 9], 0x7000),
    ([4, 8, 17], 0x3801),
    ([3, 7, 24], 0x3000),
    ([5, 15, 32], 0x7002),
    ([7, 5, 38], 0x1004),
    ([3, 16, 54], 0x3C00),
]


@pytest.mark.parametrize("inputs, expected", packCopyTokenData)
def test_packCopyToken(inputs, expected):
    help = MsOvba.copyTokenHelp(inputs[2])
    assert MsOvba.packCopyToken(inputs[0], inputs[1], help) == expected


copytoken_help_data = [
    (9, [4, 0x0FFF, 0xF000]),
    (17, [5, 0x07FF, 0xF800]),
]


@pytest.mark.parametrize("input, expected", copytoken_help_data)
def test_copytoken_help(input, expected):
    result = MsOvba.copyTokenHelp(input)
    assert result["bitCount"] == expected[0]
    assert result["lengthMask"] == expected[1]
    assert result["offsetMask"] == expected[2]


unpack_copytoken_data = [
    ([9, 0x7000], [3, 8]),
    ([32, 0x7002], [5, 15]),
    ([54, 0x3C00], [3, 16]),
]


@pytest.mark.parametrize("inputs, expected", unpack_copytoken_data)
def test_unpack_copytoken(inputs, expected):
    help = MsOvba.copyTokenHelp(inputs[0])
    result = MsOvba.unpackCopyToken(inputs[1], help)
    assert result["length"] == expected[0]
    assert result["offset"] == expected[1]
