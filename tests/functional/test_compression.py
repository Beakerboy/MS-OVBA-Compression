import pytest
from ms_ovba_compression import *

def test_normalCompresson():
    input = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    comp = compressor.Compressor()
    result = comp.compress(input)
    decomp = decompressor.Decompressor()
    assert decomp.decompress(result) == input
