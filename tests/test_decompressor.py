import pytest
from ms_ovba_compression.ms_ovba import MsOvba


def test_normal_compression():
    ms_ovba = MsOvba()
    expected = b"#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
    compressed = (b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x10\x77\x78\x79\x7A\x00\x3C')
    assert ms_ovba.decompress(compressed) == expected


def test_bad_signature_byte():
    """
    The container must have a signature byte
    """
    ms_ovba = MsOvba()
    compressed = (b'\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00'
                  + b'\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30'
                  + b'\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75'
                  + b'\x76\x10\x77\x78\x79\x7A\x00\x3C')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_container_too_short():
    """
    The container cannot be shorter then specified by the header
    """
    ms_ovba = MsOvba()
    compressed = (b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x10\x77\x78\x79\x7A\x00')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_container_too_long():
    """
    The container must not be longer then specified in the header
    """
    ms_ovba = MsOvba()
    compressed = (b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x10\x77\x78\x79\x7A\x00\3C\x3F\xFF')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_bad_raw_chunk_header():
    """
    Raw chunks must have 4096 bytes of data. Header = 0x3FFF
    """
    ms_ovba = MsOvba()
    compressed = (b'\x01\xFE\x3F\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x10\x77\x78\x79\x7A\x00')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_flag_with_no_data():
    """
    If a flag byte is present, there must be data after it.
    """
    ms_ovba = MsOvba()
    compressed = (b'\x01\x29\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x10')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_bad_header_signature():
    """
    The header signature must be 0b011
    """
    ms_ovba = MsOvba()
    compressed = (b'\x01\x2F\xA0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x10\x77\x78\x79\x7A\x00\x3C')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_incomplete_copytoken():
    """
    A copy token must be two bytes. test for early termination
    """
    ms_ovba = MsOvba()
    compressed = (b'\x01\x2A\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                  + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                  + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                  + b'\x75\x76\x01\x77')
    with pytest.raises(Exception):
        ms_ovba.decompress(compressed)


def test_decompress_unable_to_compress_big():
    expected = b'abcdefghijklmnopqrstuv.'
    ms_ovba = MsOvba("big")
    input = (b'\x01\xB0\x19\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A'
             + b'\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E')
    assert ms_ovba.decompress(input) == expected
