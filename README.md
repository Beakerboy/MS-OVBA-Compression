[![Coverage Status](https://coveralls.io/repos/github/Beakerboy/MS-OVBA-Compression/badge.png?branch=main)](https://coveralls.io/github/Beakerboy/MS-OVBA-Compression?branch=main) ![Build Status](https://github.com/Beakerboy/MS-OVBA-Compression/actions/workflows/python-package.yml/badge.svg)
# MS-OVBA-Compression

Compress or decompress data streams using the MS-OVBA compression algorithm

Microsoft Office files are zip archives that contain a variety of files that work together. One of these files is vbaProject.bin, a binary OLE container which includes
any VBA source code in the project. The VBA sources are compressed using the MS-OVBA compression algorithm.

It's worth noting that the compressed output may differ between this and a Microsoft Office applcation. The way the compression algorithm works, multiple valid
compressed byte seqences are able to be decompressed into the same uncompressed stream. This project follows the algorithm documented in the 
[MS-OVBA specification](https://interoperability.blob.core.windows.net/files/MS-OVBA/%5bMS-OVBA%5d.pdf), while one of the test cases has a compressed container
that is slightly different than is produced using it's own documented procedure.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install MS_OVBA_Compression.

```bash
pip install ms_ovba_compression
```

## Usage
All inputs and outputs are bytes objects. This library does not operate on files, but on compressed or uncompressed byte streams. Any raw VBA files require a certain
amount of normalization before compression. If you are interested in writing or modifying the whole OLE container, refer to
[Beakerboy/vbaProject-Compiler](https://github.com/Beakerboy/vbaProject-Compiler).

```python
from ms_ovba_compression.ms_ovba import MsOvba

# returns b'\x01\x19°\x00abcdefgh\x00ijklmnop\x00qrstuv.'
input = b'abcdefghijklmnopqrstuv.'
ms_ovba = MsOvba()
ms_ovba.compress(input)

# returns b'#aaabcdefaaaaghijaaaaaklaaamnopqaaaaaaaaaaaarstuvwxyzaaa'
ms_ovba = MsOvba()
compressed = b'\x01/°\x00#aaabcde²f\x00paghij\x018\x08akl\x000mnop\x06q\x02p\x04\x10rstuv\x10wxyz\x00<'
ms_ovba.decompress(compressed)

```
The objects can be initialized to indicate the endianness if the default little-endian is not desired.
```python
# returns b'\x01°\x19\x00abcdefgh\x00ijklmnop\x00qrstuv.'
input = b'abcdefghijklmnopqrstuv.'
ms_ovba = MsOvba("big")
ms_ovba.compress(input)

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
