from MS_OVBA_Compression.helpers import *

class Compressor:
    def __init__(self, endian='little'):
        self.endian = endian

        # The compressed container begins with a sgnature byte and an empty header
        self.compressedContainer = bytearray(b'\x01')

    def compress(self, data):
        """
        Compress a bytearray

        :param data bytes: bytes of compressed data
        :return: compressed data
        :rtype: bytes
        """
	
        self.originalData = data

        numberOfChunks = (len(data) - 1) // 4096 + 1
        
        for i in range(numberOfChunks):
            compressedChunk = self.compressChunk(data[i * 4096: (i + 1) * 4096])
            self.compressedContainer += compressedChunk
            
        return self.compressedContainer

    def compressChunk(self, data):
        """
        A chunk of data is 4096 bytes or less. This will return a stream of max length 4098, a 2 byte header and up to 4096 bytes of data.
        """
        self.activeChunk = data
        # Initialize with an empty header
        # Is endian-ness supposed to affect the header organization?
        # The docs state 12 length bits + 0b011 + compression-bit but real world little endian file has compression-bit + 0b011 + 12 length bits
        compressAndSig = 0xB000
        uncompressedData = bytearray(data)
        chunk = b''
        i = 0
        while len(uncompressedData) > 0:
            uncompressedData, compressedTokenSequence = self.compressTokenSequence(uncompressedData)
            chunk += compressedTokenSequence
            i += 1

        chunkSize = len(chunk)
        # if the compression algorithm produces a chunk too large, use raw.
        if chunkSize > 4096:
            chunkSize = 4096
            chunk = data.ljust(4096, '\0')
            compressAndSig = 0x3000
        header = compressAndSig & chunkSize
        chunk = header.to_bytes(2, self.endian) + chunk
        return chunk

    def compressTokenSequence(self, data):
        uncompressedData = data
        tokenFlag = 0
        tokens = b''
        for i in range(8):
            if len(uncompressedData) > 0:
                token = b''
                uncompressedData, packedToken, flag = self.compressToken(uncompressedData)
                tokenFlag = (flag << i) | tokenFlag
                tokens += packedToken
        tokenSequence = tokenFlag.to_bytes(1, "little") + tokens
        return uncompressedData, tokenSequence

    def compressToken(self, uncompressedData):
        """
        Given a sequence of uncompressed data, return a single compressed token. Tokens are either:
        one byte representing the value of the token
        two bytes indicating the location and length of the replacement sequence
        the flag byte is 1 if replacement took place
        """
        packedToken = b''
        tokenflag = 0
        offset, length = self.matching(uncompressedData)
        if offset > 0:
            difference =  len(self.activeChunk) - len(uncompressedData)
            help = copyTokenHelp(difference)
            packedToken = packCopyToken(length, offset, help).to_bytes(2, "little")

            uncompressedData = uncompressedData[length:]
            tokenFlag = 1
        else:
            tokenFlag = 0
            packedToken = uncompressedData[0].to_bytes(1, "little")
            uncompressedData = uncompressedData[1:]
        return uncompressedData, packedToken, tokenFlag

    def matching(self, uncompressedStream):
        """
        Work backwards through the uncompressed data that has already been compressed to find the longest series of matching bytes.
        """
        offset = 0
        length = 0
        bestLength = 0
        bestCandidate = 0
        candidate = len(self.activeChunk) - len(uncompressedStream) - 1
        while candidate >= 0:
            C = candidate
            D = len(self.activeChunk) - len(uncompressedStream)
            L = 0
            while D < len(self.activeChunk) and self.activeChunk[D] == self.activeChunk[C]:
                C += 1
                D += 1
                L += 1
            if L > bestLength:
                bestLength = L
                bestCandidate = candidate
            candidate -= 1
            
        if bestLength >= 3:
            difference =  len(self.activeChunk) - len(uncompressedStream)
            help = copyTokenHelp(difference)
            maximumLength = help["maxLength"]
            length = min(maximumLength, bestLength)
            offset = len(self.activeChunk) - len(uncompressedStream) - bestCandidate

        return offset, length
