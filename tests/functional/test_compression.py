import pytest
from MS_OVBA_Compression.compressor import Compressor
from MS_OVBA_Compression.decompressor import Decompressor

def test_normalCompresson():
    input = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    comp = Compressor()
    result = comp.compress(input)
    decomp = Decompressor()
    assert decomp.decompress(result) == input
