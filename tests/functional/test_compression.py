from ms_ovba_compression.ms_ovba import MsOvba


def test_normalCompresson():
    input = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    ms_ovba = MsOvba()
    result = ms_ovba.compress(input)
    assert ms_ovba.decompress(result) == input
