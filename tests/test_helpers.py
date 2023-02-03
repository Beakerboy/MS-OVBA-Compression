import pytest
from MS_OVBA_Compression.helpers import *

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
    assert ceilLog2(input) == expected

packCopyTokenData = [
    ([3, 8, 9], 0x7000),
    ([4, 8, 17], 0x3801),
    ([3, 5, 24], 0x3000),
]

@pytest.mark.parametrize("inputs, expected", packCopyTokenData)
def test_packCopyToken(inputs, expected):
    help = copytokenHelp(inputs[2])
    assert packCopyToken(inputs[0] ,inputs[1], help) == expected
