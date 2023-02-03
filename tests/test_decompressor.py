import pytest
from MS_OVBA_Compression.decompressor import Decompressor

def test_Decompressor():
    comp = Decompressor()
    header = b'\x19\xB0'
    comp.setCompressedHeader(header)
    expected = 28
    result = comp.getCompressedChunkSize()
    assert expected == result
    data = b'\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E'
    comp.setCompressedData(data)
    assert comp.getCompressedChunk() == bytearray(header) + bytearray(data)

def test_normalCompression():
    comp = Decompressor()
    expected = "#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
    compressed = bytearray(b'\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00\x3C')
    header = bytearray(compressed[:2])
    del compressed[:2]
    comp.setCompressedHeader(header)
    result = comp.decompress(compressed)
    assert bytearray(expected, "ascii") == result

def test_compressRaw():
    comp = Decompressor()
    #comp.setCompression(False)
    #input = "a"
    #result = comp.compress(input);
    #header = bytearray(b'\xFF\x3F')
    #start = header + b'\x61'
    #expected = start.ljust(4095, b'\x00')
    #assert expected == result

def test_ChunkSizeMismatch():
    comp = Decompressor()
    header = b'\x19\xB0'
    comp.setCompressedHeader(header)
    data = b'\x00\x61\x62'
    with pytest.raises(Exception) as e_info:
        comp.setCompressedData(data)

def test_decompressUnableToCompressOneToken():
    compressed = bytearray(b'\x08\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68')
    comp = Decompressor()
    header = bytearray(compressed[:2])
    del compressed[:2]
    comp.setCompressedHeader(header)
    result = comp.decompress(compressed)
    expected = bytearray("abcdefgh", "ascii")
    assert expected == result

def test_zeroTokens():
    compressed = bytearray(b'\x00\xB0\x00')
    comp = Decompressor()
    header = bytearray(compressed[:2])
    del compressed[:2]
    comp.setCompressedHeader(header)
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)
    
def test_decompressUnableToCompressOneToken1():
    compressed = bytearray(b'\x19\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E')
    comp = Decompressor()
    header = bytearray(compressed[:2])
    del compressed[:2]
    comp.setCompressedHeader(header)
    result = comp.decompress(compressed)
    expected = bytearray("abcdefghijklmnopqrstuv.", "ascii")
    assert expected == result

def test_smallHeader():
    comp = Decompressor()
    with pytest.raises(Exception) as e_info:
        comp.setCompressedHeader(b'\x07')
