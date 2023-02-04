import struct
from MS_OVBA_Compression.helpers import *
class Decompressor:

    def __init__(self, endian = 'little'):
        self.endian = endian
        self.uncompressedData = b''

    def decompress(self, compressedContainer):
        if compressedContainer[0] != 0x01:
            raise Exception("The container signature byte must be \\x01, not " + str(compressedContainer[0]) + ".")
        chunks = compressedContainer[1:]
        while len(chunks) > 0:
            header = chunks[0:2]
            compressed, length = self.unpackHeader(header)
            compressedDataLength = length - 2
            if len(chunks) < length:
                raise Exception("Expecting " + str(length - 2) + " data bytes, but given " + str(len(chunks - 2)) + ".")
            compressedChunk = chunks[2:compressedDataLength + 2]
            chunks = chunks[length + 2:]
            self.uncompressedData += self.decompressChunk(compressedChunk)
            # if there are more chunks, this chunk must be 4096 bytes uncompressed

    def unpackHeader(self, compressedHeader):
        length = len(compressedHeader)
        if length != 2:
            raise Exception("The header must be two bytes. Given " + str(length) + ".")
        intHeader = int.from_bytes(compressedHeader, "little")
        # data is compressed if the least significat bit is 0b1
        compressed = (intHeader & 0x8000) >> 15

        # the 12 most significant bits is three less than the chunk size
        length = (intHeader & 0x0FFF) + 3
        if compressed == 0 and length != 4098:
            raise Exception("If uncompressed, chunk must be 4096 bytes.")
        signature = (intHeader & 0x7000) >> 12
        if signature != 3:
            raise Exception("Chunk signature must be three. Value is " + str(signature) + ".")
        return compressed, length

    def decompressChunk(self, compressedChunk):
        """
        Decompress bytes object

        :param data bytes: bytes of compressed data
        :return: bytes
        :rtype: bytes
        """
        uncompressedChunk = b''
        while len(compressedChunk) > 0:
            # The Flag Byte is one byte. pop it off
            flagByte = compressedChunk[0]
            compressedChunk = compressedChunk[1:]

            # If we have a flag byte, we better have data to go with it.
            if len(compressedChunk) == 0:
                raise Exception("There must be at least one token in each TokenSequence.")
            flagMask = 1
            for i in range(8):
                # Extract Flag bit from the token with the mask
                flagBit = flagByte & flagMask
                
                if flagBit == 0:
                    # If the flag bit is zero, no compression ocurred, so just move the byte over.
                    if len(compressedChunk) > 0:
                        uncompressedChunk += compressedChunk[0].to_bytes(1, "little")
                        compressedChunk = compressedChunk[1:]
                else:
                    # If the flag bit is one, grab the 2 byte copy token and determine the offset and length of the replacement string.
                    # There better be 2 bytes or we're in trouble.
                    if len(compressedChunk) < 2:
                        raise Exception("Copy Token does not exist. FlagToken was " + str(flagToken) + " and decompressed chunk is " + self.uncompressedData + '.')
                    help = copyTokenHelp(len(uncompressedChunk))
                    # The copy Token is always packed into the compressed chuck little endian
                    copyToken = struct.unpack("<H", data[:2])
                    copyTokenData = unpackCopyToken(copyToken, help)
                    compressedChunk = compressedChunk[2:]
                    offset = copyTokenData["offset"]
                    for i in range(copyTokenData["length"]):
                        # Copy data from the uncompressed chunk, {offset} bytes away, {length} number of times.
                        # Note that this can mean that we could possibly copy new data multiple times, ie. offset 1 length 7
                        uncompressedChunk += uncompressedChunk[-1 * offset].to_bytes(1, "little")
                # Move the mask for the next round
                flagMask = flagMask << 1
        return self.uncompressedData
