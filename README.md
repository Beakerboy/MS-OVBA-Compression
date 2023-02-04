[![Coverage Status](https://coveralls.io/repos/github/Beakerboy/MS-OVBA-Compression/badge.svg?branch=main)](https://coveralls.io/github/Beakerboy/MS-OVBA-Compression?branch=main)![Build Status](https://github.com/Beakerboy/MS-OVBA-Compression/actions/workflows/python-package.yml/badge.svg)
# MS-OVBA-Compression

Compress or decompress data streams using the MS-OVBA compression algorithm

Microsoft Office files are zip archives that contain a variety of files that work together. One of these files is vbaProject.bin, a binary OLE container which includes
any VBA source code in the project. The VBA sources are compressed using the MS-OVBA compression algorithm.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install MS_OVBA_Compression
```

## Usage
All inputs and outputs are bytes objects. This library does not operate on files, but on compressed or uncompressed byte streams.

```python
from MS_OVBA_Copression.compressor import Compressor
from MS_OVBA_Copression.decompressor import Decompressor

# returns b'\x01\x19\xB0\x00\x61\x62\x63\x64\x65\x66\x67\x68\x00\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x00\x71\x72\x73\x74\x75\x76\x2E'
input = b'abcdefghijklmnopqrstuv.'
comp = Compressor()
comp.compress(input)

# returns b"#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
comp = Decompressor()
expected = b"#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
compressed = b'\x01\x2F\xB0\x00\x23\x61\x61\x61\x62\x63\x64\x65\x82\x66\x00\x70\x61\x67\x68\x69\x6A\x01\x38\x08\x61\x6B\x6C\x00\x30\x6D\x6E\x6F\x70\x06\x71\x02\x70\x04\x10\x72\x73\x74\x75\x76\x10\x77\x78\x79\x7A\x00\x3C'
comp.decompress(compressed)


```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
