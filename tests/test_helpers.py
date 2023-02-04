import pytest
import ms_ovba_compression.helpers as helpers


ceilLog2Data = [
    (1, 4),
    (2, 4),
    (3, 4),
    (4, 4),
    (9, 4),
    (17, 5),
    (50, 6),
]


@pytest.mark.parametrize("input, expected", ceilLog2Data)
def test_cielLog2(input, expected):
    assert helpers.ceilLog2(input) == expected


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
    help = helpers.copyTokenHelp(inputs[2])
    assert helpers.packCopyToken(inputs[0], inputs[1], help) == expected


copytokenHelpData = [
    (9, [4, 0x0FFF, 0xF000]),
    (17, [5, 0x07FF, 0xF800]),
]


@pytest.mark.parametrize("input, expected", copytokenHelpData)
def test_copytokenHelp(input, expected):
    result = helpers.copyTokenHelp(input)
    assert result["bitCount"] == expected[0]
    assert result["lengthMask"] == expected[1]
    assert result["offsetMask"] == expected[2]


unpackCopyTokenData = [
    ([9, 0x7000], [3, 8]),
    ([32, 0x7002], [5, 15]),
    ([54, 0x3C00], [3, 16]),
]


@pytest.mark.parametrize("inputs, expected", unpackCopyTokenData)
def test_unpackCopyToken(inputs, expected):
    help = helpers.copyTokenHelp(inputs[0])
    result = helpers.unpackCopyToken(inputs[1], help)
    assert result["length"] == expected[0]
    assert result["offset"] == expected[1]
