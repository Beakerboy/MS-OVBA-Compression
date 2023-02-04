from MS_OVBA_Compression.helpers import *
class Decompressor:

    def __init__(self, endian = 'little'):
        self.endian = endian

    def decompress(self, compressedContainer):
        uncompressedData = b''
        # The compressed container must begin with the byte \x01
        if compressedContainer[0] != 0x01:
            raise Exception("The container signature byte must be \\x01, not " + str(compressedContainer[0]) + ".")
        # Pop off the signature byte. Everything else is compressed chunks
        chunks = compressedContainer[1:]
        while len(chunks) > 0:
            # The first two bytes of each chunk is the header. It will tell us how long the compressed data is in this chunk.
            # All chunks must be 4096 bytes uncompressed except for the last chunk.
            header = chunks[0:2]
            compressed, length = self._unpackHeader(header)

            # The unpackHeader method gives us the chunk length. the data potion is two less than that.
            compressedDataLength = length - 2

            # If we have less data then we are supposed to, we have a problem.
            if len(chunks) < length:
                raise Exception("Expecting " + str(length - 2) + " data bytes, but given " + str(len(chunks - 2)) + ".")

            # Split out the compresseddata from the chunk buffer.
            compressedChunk = chunks[2:compressedDataLength + 2]

            # Pop off the data we are working on from the buffer
            chunks = chunks[length + 2:]
            decompressedChunk = self._decompressChunk(compressedChunk)
            uncompressedData += decompressedChunk

            # If the last chunk is less than 4096 bytes, there better not be anything left in the buffer.
            # Should this raise a warning instead?
            if len(decompressedChunk) < 4096 and len(chunks) > 0:
                raise Exception("The provided compressed container is too long.")
        return uncompressedData

    def _unpackHeader(self, compressedHeader):
        # Need to find out if this byte order is endian dependent. It seems the real world data had the bits packed little
        # endian and then the resulting two bytes packed little endian into the binary file.
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

    def _decompressChunk(self, compressedChunk):
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
                    copyToken = int.from_bytes(compressedChunk[:2], "little")
                    copyTokenData = unpackCopyToken(copyToken, help)
                    compressedChunk = compressedChunk[2:]
                    offset = copyTokenData["offset"]
                    for i in range(copyTokenData["length"]):
                        # Copy data from the uncompressed chunk, {offset} bytes away, {length} number of times.
                        # Note that this can mean that we could possibly copy new data multiple times, ie. offset 1 length 7
                        uncompressedChunk += uncompressedChunk[-1 * offset].to_bytes(1, "little")
                # Move the mask for the next round
                flagMask = flagMask << 1
        return uncompressedChunk
