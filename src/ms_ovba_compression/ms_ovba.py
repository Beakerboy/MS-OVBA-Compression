class MsOvba:

    def __init__(self, endian='little'):
        self._endian = endian

    def decompress(self, compressed_container):
        """
        Decompress a compressed container usng the MS-OVBA Compression
        Algorithm

        :param compressedContainer bytes: bytes of compressed data
        :return: Uncompressed data
        :rtype: bytes
        """
        uncompressed_data = b''
        # The compressed container must begin with the byte \x01
        if compressed_container[0] != 0x01:
            message = ("The container signature byte must be \\x01, not "
                       + str(compressed_container[0]) + ".")
            raise Exception(message)
        # Pop off the signature byte. Everything else is compressed chunks
        chunks = compressed_container[1:]
        while len(chunks) > 0:
            # The first two bytes of each chunk is the header. It will tell us
            # how long the compressed data is in this chunk. All chunks must be
            # 4096 bytes uncompressed except for the last chunk.
            header = chunks[0:2]
            compressed, length = self._unpack_header(header)

            # The unpackHeader method gives us the chunk length. The data
            # portion is two less than that.
            compressed_data_length = length - 2

            # If we have less data then we are supposed to, we have a problem.
            if len(chunks) < length:
                message = ("Expecting " + str(length - 2)
                           + " data bytes, but given " + str(len(chunks) - 2)
                           + ".")
                raise Exception(message)

            # Split out the compresseddata from the chunk buffer.
            compressed_chunk = chunks[2:compressed_data_length + 2]

            # Pop off the data we are working on from the buffer
            chunks = chunks[length + 2:]
            decompressed_chunk = self._decompress_chunk(compressed_chunk)
            uncompressed_data += decompressed_chunk

            # If the last chunk is less than 4096 bytes, there better not be
            # anything left in the buffer. Should this raise a warning instead?
            if len(decompressed_chunk) < 4096 and len(chunks) > 0:
                message = "The provided compressed container is too long."
                raise Exception(message)
        return uncompressed_data

    def _unpack_header(self, compressed_header):
        # Need to find out if this bit order is endian dependent. It seems the
        # real world data had the bits packed little endian and then the
        # resulting two bytes packed little endian into the binary file.
        int_header = int.from_bytes(compressed_header, self._endian)

        # Data is compressed if the least significat bit is 0b1
        compressed = (int_header & 0x8000) >> 15

        # the 12 most significant bits is three less than the chunk size
        length = (int_header & 0x0FFF) + 3
        if compressed == 0 and length != 4098:
            raise Exception("If uncompressed, chunk must be 4096 bytes.")
        signature = (int_header & 0x7000) >> 12
        if signature != 3:
            message = ("Chunk signature must be three. Value is "
                       + str(signature) + ".")
            raise Exception(message)
        return compressed, length

    def _decompress_chunk(self, compressed_chunk) -> bytes:
        """
        Decompress bytes object

        :param data bytes: bytes of compressed data
        :return: bytes
        :rtype: bytes
        """
        uncompressed_chunk = b''
        while len(compressed_chunk) > 0:
            # The Flag Byte is one byte. pop it off
            flagByte = compressed_chunk[0]
            compressed_chunk = compressed_chunk[1:]

            # If we have a flag byte, we better have data to go with it.
            if len(compressed_chunk) == 0:
                message = ("There must be at least one token "
                           "in each TokenSequence.")
                raise Exception(message)
            flagMask = 1
            for i in range(8):
                # Extract Flag bit from the token with the mask
                flagBit = flagByte & flagMask

                if flagBit == 0:
                    # If the flag bit is zero, no compression ocurred, so just
                    # move the byte over.
                    if len(compressed_chunk) > 0:
                        byte = compressed_chunk[0].to_bytes(1, "little")
                        uncompressed_chunk += byte
                        compressed_chunk = compressed_chunk[1:]
                else:
                    # If the flag bit is one, grab the 2 byte copy token and
                    # determine the offset and length of the replacement
                    # string. There better be 2 bytes or we're in trouble.
                    if len(compressed_chunk) < 2:
                        message = "Copy Token does not exist."
                        raise Exception(message)
                    help = MsOvba.copyTokenHelp(len(uncompressed_chunk))
                    # The copy Token is always packed into the compressed chuck
                    # little endian.
                    copyToken = int.from_bytes(compressed_chunk[:2], "little")
                    copyTokenData = MsOvba.unpackCopyToken(copyToken, help)
                    compressed_chunk = compressed_chunk[2:]
                    offset = copyTokenData["offset"]

                    # Copy data from the uncompressed chunk, {offset} bytes
                    # away, {length} number of times. Note that this can mean
                    # that we could possibly copy new data multiple times, ie.
                    # offset 1 length 7
                    for i in range(copyTokenData["length"]):
                        copyInt = uncompressed_chunk[-1 * offset]
                        copyByte = copyInt.to_bytes(1, "little")
                        uncompressed_chunk += copyByte
                # Move the mask for the next round
                flagMask = flagMask << 1
        return uncompressed_chunk

    def compress(self, data) -> bytes:
        """
        Compress a bytearray
        :param data bytes: bytes of compressed data
        :return: compressed data
        :rtype: bytes
        """
        # The compressed container begins with a sgnature byte.
        compressed_container = b'\x01'

        # Each chunk must hold 4096 bytes of data except the final chunk.
        number_of_chunks = (len(data) - 1) // 4096 + 1

        # Grab 4096 bytes, compress the chunk, and add it to the container
        for i in range(number_of_chunks):
            start = i * 4096
            end = (i + 1) * 4096
            compressed_chunk = self._compress_chunk(data[start: end])
            compressed_container += compressed_chunk

        return compressed_container

    def _compress_chunk(self, data):
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
        The token that is returned will be packed into the required little
        endian packing.
        Should the flag bit be returned as bool instead of int?
        :return: (packed copy token, flag bit)
        :rtype: (bytes, int)
        """
        packedToken = b''
        tokenFlag = 0
        offset, length = self._matching()
        if offset > 0:
            tokenFlag = 1

            # Pack the offset and length data into the CopyToken, then pack
            # the token little-endian.
            difference = len(self._activeChunk) - len(self._uncompressedData)
            help = MsOvba.copyTokenHelp(difference)
            tokenInt = MsOvba.packCopyToken(length, offset, help)
            packedToken = tokenInt.to_bytes(2, "little")

            # Update the uncompressed buffer by removing the length we were
            # able to match.
            self._uncompressedData = self._uncompressedData[length:]
        else:
            tokenFlag = 0

            # No matching data was found, copy the literal token over.
            packedToken = self._uncompressedData[0].to_bytes(1, "little")
            self._uncompressedData = self._uncompressedData[1:]
        return packedToken, tokenFlag

    def _matching(self):
        """
        Work backwards through the uncompressed data that has already been
        compressed to find the longest series of matching bytes.
        :return: (offset, length)
        :rtype: (int, int)
        """
        offset = 0
        length = 0
        best_length = 0
        best_candidate = 0
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
            if L > best_length:
                best_length = L
                best_candidate = candidate
            candidate -= 1

        if best_length >= 3:
            difference = len(self._activeChunk) - len(self._uncompressedData)
            help = MsOvba.copyTokenHelp(difference)
            maximumLength = help["maxLength"]
            length = min(maximumLength, best_length)
            offset = (len(self._activeChunk) - len(self._uncompressedData)
                      - best_candidate)

        return offset, length

    @staticmethod
    def copyTokenHelp(difference):
        """
        Calculate a lengthMask, offsetMask, and bitCount from the length of the
        uncompressedData.
        """
        bit_count = MsOvba.ceilLog2(difference)
        length_mask = 0xFFFF >> bit_count
        offset_mask = ~length_mask & 0xFFFF
        max_length = 0xFFFF << bit_count + 3
        return {
            "lengthMask": length_mask,
            "offsetMask": offset_mask,
            "bitCount": bit_count,
            "maxLength": max_length
        }

    @staticmethod
    def unpackCopyToken(copytoken, help):
        """
        calculate an offset and length from a 16 bit copytoken
        """
        length = (copytoken & help["lengthMask"]) + 3
        temp1 = copytoken & help["offsetMask"]
        temp2 = 16 - help["bitCount"]
        offset = (temp1 >> temp2) + 1
        return {
            "length": length,
            "offset": offset
        }

    @staticmethod
    def packCopyToken(length, offset, help):
        """
        Create the copy token from the length, offset, and currect position
        return bytes
        """
        temp1 = offset - 1
        temp2 = 16 - help["bitCount"]
        temp3 = length - 3
        return (temp1 << temp2) | temp3

    @staticmethod
    def ceilLog2(int):
        i = 4
        while 2 ** i < int:
            i += 1
        return i
