import pytest
from MS_OVBA_Compression.compressor import Compressor

matchingData = [
    (b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [0, 0]),
    (b'aaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [3, 8]),
    (b'aaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [4, 8]),
    (b'aaamnopqaaaaaaaaaaaarstuvwxyzaaa', [3, 5]),
    (b'aaaaaaaaaaaarstuvwxyzaaa', [5, 15]),
    (b'aaaaaaarstuvwxyzaaa', [7, 1]),
    (b'aaa', [3, 12]),
]

@pytest.mark.parametrize("input, expected", matchingData)
def test_matching(input, expected):
    comp = Compressor()
    comp.activeChunk = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    offset, length =  comp.matching(input)
    assert length == expected[0]
    assert offset == expected[1]

compressTokenData = [
    (b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [b'aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', b'\x23', 0]),
    (b'aaaaghiaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [b'aghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', b'\x70\x00', 1]),
]
@pytest.mark.parametrize("input, expected", compressTokenData)
def test_compressToken(input, expected):
    comp = Compressor()
    comp.activeChunk = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    uncompressed, token, flag = comp.compressToken(input)
    assert uncompressed == expected[0]
    assert flag == expected[2]
    assert token == expected[1]

