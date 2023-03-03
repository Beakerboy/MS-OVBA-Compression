from ms_ovba_compression.ms_ovba import MsOvba


def test_unableToCompress():
    input = b'abcdefghijklmnopqrstuv.'
    ms_ovba = MsOvba()
    expected = (b'\x01\x19\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A'
                + b'\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E')
    assert ms_ovba.compress(input) == expected


def test_maxCompression():
    input = (b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
             + b'aaaaaaaaaa')
    ms_ovba = MsOvba()
    expected = b'\x01\x03\xB0\x02\x61\x45\x00'
    assert ms_ovba.compress(input) == expected


def test_longPoorCompression():
    """
    Every sequence of 8 bytes has a flag byte prepended to the compressed token
    sequence. In theory a 3640 byte sequence could "compress" to be larger than
    4096 bytes.
    """
    data = b''
    for i in range(7):
        for j in range(256):
            data += i.to_bytes(1, "little") + j.to_bytes(1, "little")
    i = 8
    for j in range(72):
        data += i.to_bytes(1, "little") + j.to_bytes(1, "little")
    assert len(data) < 4096
    ms_ovba = MsOvba()
    result = ms_ovba.compress(data)
    # the length is 1 container signature byte, 2 header bytes, and the
    # original data padded to 4096 bytes
    assert len(result) == 4099
    # The resulting chunk header will be 0x3FFF
    assert result[2] & 0xF0 == 0x30


def test_unableToCompressBig():
    input = b'abcdefghijklmnopqrstuv.'
    ms_ovba = MsOvba("big")
    expected = (b'\x01\xB0\x19\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A'
                + b'\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E')
    assert ms_ovba.compress(input) == expected


def test_normalCompression():
    ms_ovba = MsOvba()
    input = b"#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
    expected = (b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66'
                + b'\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00'
                + b'\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74'
                + b'\x75\x76\x10\x77\x78\x79\x7A\x00\x3C')
    assert ms_ovba.compress(input) == expected
