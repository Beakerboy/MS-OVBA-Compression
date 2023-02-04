import ms_ovba_compression.helpers as helpers


class Compressor:

    def __init__(self, endian='little'):
        self._endian = endian

    def compress(self, data):
        """
        Compress a bytearray

        :param data bytes: bytes of compressed data
        :return: compressed data
        :rtype: bytes
        """
        # The compressed container begins with a sgnature byte.
        compressedContainer = b'\x01'

        # Each chunk must hold 4096 bytes of data except the final chunk.
        numberOfChunks = (len(data) - 1) // 4096 + 1

        # Grab 4096 bytes, compress the chunk, and add it to the container
        for i in range(numberOfChunks):
            start = i * 4096
            end = (i + 1) * 4096
            compressedChunk = self._compressChunk(data[start: end])
            compressedContainer += compressedChunk

        return compressedContainer

    def _compressChunk(self, data):
        """
        A chunk of data is 4096 bytes or less. This will return a stream of max
        length 4098, a 2 byte header and up to 4096 bytes of data.
        """

        # A record of the uncompressed data is needed after compression for the
        # matching algorithm.
        self._activeChunk = data

        # Initialize with an empty header
        # Is endian-ness supposed to affect the header organization?
        # The docs state 12 length bits + 0b011 + compression-bit but real
        # world little endian file has compression-bit + 0b011 + 12 length bits
        compressAndSig = 0xB000

        # Buffer of data to be compressed and moved to compressedChunk
        self._uncompressedData = data

        # Buffer of compressed data.
        compressedChunk = b''

        # While there is data in the uncompressed buffer, build a token 
        # sequence and compress it and add the compressed sequence to the
        # compressed buffer.
        while len(self._uncompressedData) > 0:
            compressedChunk += self._compressTokenSequence()

        # After we are done, we need to ensure the final compressed chunk is
        # not larger than the original to the point that it exceeds 4096 bytes.
        # If it has, we can copy the original 4096 bytes of uncompressed data
        # and flag this chunk as using "raw" compression by setting the
        # compression but to 0.
        # This chunk size is three less then the "total" chunk size, which is
        # data plus the two byte header.
        chunkSizeMinusThree = len(compressedChunk) - 1

        if chunkSizeMinusThree > 4095:
            chunkSizeMinusThree = 4095
            # Raw chunks must be 4096 bytes in size. Even if the starting data
            # is less than 4096 bytes. This means after decompressing, there
            # may be unexpected padding.
            compressedChunk = data.ljust(4096, b'\x00')
            compressAndSig = 0x3000

        # Join the 12 bit chunk size with the compress bit and three bit
        # siganture.
        header = compressAndSig | chunkSizeMinusThree

        # Prepend the header to the compressed chunk data and return the
        # complete chunk.
        compressedChunk = header.to_bytes(2, self._endian) + compressedChunk
        return compressedChunk

    def _compressTokenSequence(self):
        """
        A token sequence is a 1 byte token flag followed by 8 tokens. Each
        tokenis one or two bytes. Each bit of the flag byte incates if the
        token is a 1 byte literal token or a 2 byte copy token. The least
        significant bit of the flag byte refers to the first token in the
        stream.
        """

        tokenFlag = 0
        tokens = b''
        for i in range(8):
            if len(self._uncompressedData) > 0:
                packedToken, flag = self._compressToken()

                # The flag is a 1 or 0, left shift it and pack it into the flag
                # byte.
                tokenFlag = (flag << i) | tokenFlag
                tokens += packedToken
        tokenSequence = tokenFlag.to_bytes(1, "little") + tokens
        return tokenSequence

    def _compressToken(self):
        """
        Given a sequence of uncompressed data, return a single compressed
        token. Tokens are either one byte representing the value of the
        token or two bytes indicating the location and length of the
        replacement sequence. The flag byte is 1 if replacement took place.
        """
        packedToken = b''
        tokenFlag = 0
        offset, length = self._matching()
        if offset > 0:
            difference = len(self._activeChunk) - len(self._uncompressedData)
            help = helpers.copyTokenHelp(difference)
            tokenInt = helpers.packCopyToken(length, offset, help)
            packedToken = tokenInt.to_bytes(2, "little")

            self._uncompressedData = self._uncompressedData[length:]
            tokenFlag = 1
        else:
            tokenFlag = 0
            packedToken = self._uncompressedData[0].to_bytes(1, "little")
            self._uncompressedData = self._uncompressedData[1:]
        return packedToken, tokenFlag

    def _matching(self):
        """
        Work backwards through the uncompressed data that has already been
        compressed to find the longest series of matching bytes.
        """
        offset = 0
        length = 0
        bestLength = 0
        bestCandidate = 0
        candidate = len(self._activeChunk) - len(self._uncompressedData) - 1
        while candidate >= 0:
            C = candidate
            D = len(self._activeChunk) - len(self._uncompressedData)
            L = 0
            while (D < len(self._activeChunk)
                   and self._activeChunk[D] == self._activeChunk[C]):
                C += 1
                D += 1
                L += 1
            if L > bestLength:
                bestLength = L
                bestCandidate = candidate
            candidate -= 1

        if bestLength >= 3:
            difference = len(self._activeChunk) - len(self._uncompressedData)
            help = helpers.copyTokenHelp(difference)
            maximumLength = help["maxLength"]
            length = min(maximumLength, bestLength)
            offset = (len(self._activeChunk) - len(self._uncompressedStream)
                      - bestCandidate)

        return offset, length
