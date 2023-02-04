import pytest
from MS_OVBA_Compression.decompressor import Decompressor

def test_normalCompression():
    comp = Decompressor()
    expected = b"#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
    compressed = b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00\x3C'
    result = comp.decompress(compressed)
    assert comp.decompress(compressed) == expected

def test_badSignatureByte():
    """
    The container must have a signature byte
    """
    comp = Decompressor()
    compressed = b'\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00\x3C'
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)

def test_containerTooShort():
    """
    The container must have a signature byte
    """
    comp = Decompressor()
    compressed = b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00'
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)

def test_containerTooLong():
    """
    The container must have a signature byte
    """
    comp = Decompressor()
    compressed = b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00\3C\x3F\xFF'
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)


def test_badRawChunkHeader():
    """
    Raw chinks must have 4096 bytes of data. Header = 0x3FFF
    """
    comp = Decompressor()
    compressed = b'\x01\xFE\x3F\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00'
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)

def test_flagWithNoData():
    comp = Decompressor()
    compressed = b'\x01\x29\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10'
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)

def test_badHeaderSignature():
    comp = Decompressor()
    compressed = b'\x01\x2F\xA0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00\x3C'
    with pytest.raises(Exception) as e_info:
        result = comp.decompress(compressed)
