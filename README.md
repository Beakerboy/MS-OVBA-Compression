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

# returns b'\x01\x19\xB0\x00abcdefgh\x00ijklmnop\x00qrstuv.'
input = b'abcdefghijklmnopqrstuv.'
comp = Compressor()
comp.compress(input)

# returns b"#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa"
comp = Decompressor()
compressed = b'\x01/°\x00#aaabcde²f\x00paghij\x018\x08akl\x000mnop\x06q\x02p\x04\x10rstuv\x10wxyz\x00<'
comp.decompress(compressed)


```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
