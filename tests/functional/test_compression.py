import pytest
from MS_OVBA_Compression.compressor import Compressor
from MS_OVBA_Compression.decompressor import Decompressor

def test_normalCompresson():
    input = b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
    comp = Compressor()
    result = comp.compress(input)
    decomp = Decompressor()
    decomp.setCompressedHeader(result[1:3])
    chunk = result[3:]
    assert decomp.decompress(chunk) == input
