import pytest
from MS_OVBA_Compression.compressor import Compressor

def test_unableToCompress():
    input = b'abcdefghijklmnopqrstuv.'
    comp = Compressor(input)
    expected = b'\x01\x19\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E'
    #assert comp.compress(input) == expected

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
    (b'aaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [b'aghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', b'\x00\x70', 1]),
]
@pytest.mark.parametrize("input, expected", compressTokenData)
def test_compressToken(input, expected):
    comp = Compressor()
    comp.activeChunk = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    uncompressed, packedToken, flag = comp.compressToken(input)
    assert uncompressed == expected[0]
    assert flag == expected[2]
    assert packedToken == expected[1]

def test_compressTokenSequence():
    comp = Compressor()
    comp.activeChunk = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    uncompressedData, tokenSequence = comp.compressTokenSequence(b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa')
    assert uncompressedData == b'faaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    assert tokenSequence == b'\x00\x61\x62\x63\x64\x65\x66\x67\x68'
