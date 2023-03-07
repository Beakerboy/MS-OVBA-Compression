from ms_ovba_compression.ms_ovba import MsOvba


def test_unable_to_compress():
    input = b'abcdefghijklmnopqrstuv.'
    ms_ovba = MsOvba()
    expected = (b'\x01\x19\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A'
                + b'\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E')
    assert ms_ovba.compress(input) == expected


def test_max_compression():
    input = (b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
             + b'aaaaaaaaaa')
    ms_ovba = MsOvba()
    expected = b'\x01\x03\xB0\x02\x61\x45\x00'
    assert ms_ovba.compress(input) == expected


def test_long_poor_compression():
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


def test_unable_to_compress_big():
    input = b'abcdefghijklmnopqrstuv.'
    ms_ovba = MsOvba("big")
    expected = (b'\x01\xB0\x19\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A'
                + b'\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E')
    assert ms_ovba.compress(input) == expected
