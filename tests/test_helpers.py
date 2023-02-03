import pytest
import MS_OVBA_Compression.helpers

ceilLog2Data = [
    (1, 4),
    (2, 4),
    (3, 4),
    (4, 4),
    (9, 4),
    (17, 5),
    (50, 6),
]
@pytest.mark.paramatrize("input, expected", ceilLog2Data)
def test_cielLog2(input, expected):
    assert helpers.ceilLog2(input) == expected
