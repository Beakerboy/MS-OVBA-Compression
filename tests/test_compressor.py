import pytest
from MS_OVBA_Compression.compressor import Compressor

def test_unableToCompress():
    input = b'abcdefghijklmnopqrstuv.'
    comp = Compressor()
    expected = b'\x01\x19\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E'
    assert comp.compress(input) == expected

def test_maxCompression():
    input = b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    comp = Compressor()
    expected = b'\x01\x03\xB0\x02\x61\x45\x00'
    assert comp.compress(input) == expected

def test_longPoorCompression():
    """
    Every sequence of 8 bytes has a flag byte prepended to the compressed token sequence. In theory a 3640 byte sequence could
    "compress" to be larger than 4096 bytes.
    """
    data = b''
    for i in range(7):
        for j in range(256):
            data += i.to_bytes(i, "little") + j.to_bytes(1, "little")
    for j in range(72):
            data += i.to_bytes(8, "little") + j.to_bytes(1, "little")
    comp = Compressor()
    result = comp.compress(data)
    # the length is 1 container signature byte, 2 header bytes, and the original data padded to 4096 bytes
    assert len(result) == 4099
    # The resulting chunk header will be 0xBFFF
    assert result[3] & 0xF0 == 0x30

"""
tests for private methods...for reference / troubleshooting. Note private methods may change in future releases without warning.
matchingData = [
    (b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [0, 0]),
    (b'aaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [3, 8]),
    (b'aaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa', [4, 8]),
    (b'aaamnopqaaaaaaaaaaaarstuvwxyzaaa', [3, 5]), # MS Office for some reason chooses [3, 7]
    (b'aaaaaaaaaaaarstuvwxyzaaa', [5, 15]),
    (b'aaaaaaarstuvwxyzaaa', [7, 1]),              # MS Office for some reason chooses [7, 3]
    (b'aaa', [3, 12]),                             # MS Office for some reason chooses [7, 16]
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
    assert tokenSequence == b'\x00\x23\x61\x61\x61\x62\x63\x64\x65'
"""
