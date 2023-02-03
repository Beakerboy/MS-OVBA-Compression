import struct
from MS_OVBA_Compression.helpers import *
class Decompressor:

    def __init__(self, endian = 'little'):
        self.endian = endian
        self.uncompressedData = b''
        
        # The chunk after compression
        self.compressedChunk = b''

        #the size in bytes of the compressed chunk
        self.compressedChunkSize = 0

        # is the data compressed?
        self.compressed = 1

    def decompress(self, compressedContainer):
        if compressedContainer[0] != 0x01:
            raise Exception("The container signature byte must be \\x01.")
        chunks = compressedContainer[1:]
        while len(chunks) > 0:
            header = chunks[0:2]
            compressed, length = self.unpackHeader(header)
            cmpressedDataLength = length - 2
            if len(chunks) < length:
                raise Exception("Expecting " + str(length - 2) + " data bytes, but given " + str(len(chunks - 2)) + ".")
            compressedChunk = chunks[2:compressedDataLength + 2]
            chunks = chunks[length + 2:]
            self.uncompressedData += self.decompressChunk(compressedChunk)

    def unpackHeader(self, header):
        length = len(compressedHeader)
        if length != 2:
            raise Exception("The header must be two bytes. Given " + str(length) + ".")
        intHeader = int.from_bytes(compressedHeader, "little")
        # data is compressed if the least significat bit is 0b1
        compressed = (intHeader & 0x8000) >> 15

        # the 12 most significant bits is three less than the chunk size
        length = (intHeader & 0x0FFF) + 3
        if not(self.compressed) and self.compressedChunkSize != 4096:
            raise Exception("If uncompressed, chunk must be 4096 bytes.")
        signature = (intHeader & 0x7000) >> 12
        if signature != 3:
            raise Exception("Chunk signature must be three. Value is " + str(signature) + ".")
        return compressed, length

    def setCompressedHeader(self, compressedHeader):
        """
        The compressed header is two bytes. 12 signature byes followed by \011 and a single bit that is 0b1 if compressed
        The documentation differs from real-world MS implementation. It's possible that enian-ness affects the packing order of these bits.
        """
        length = len(compressedHeader)
        if length != 2:
            raise Exception("The header must be two bytes. Given " + str(length) + ".")
        intHeader = int.from_bytes(compressedHeader, "little")
        # data is compressed if the least significat bit is 0b1
        self.compressed = (intHeader & 0x8000) >> 15

        # the 12 most significant bits is three less than the chunk size
        self.compressedChunkSize = (intHeader & 0x0FFF) + 3
        if not(self.compressed) and self.compressedChunkSize != 4096:
            raise Exception("If uncompressed, chunk must be 4096 bytes.")
        self.compressedChunkSignature = (intHeader & 0x7000) >> 12
        if self.compressedChunkSignature != 3:
            raise Exception("Chunk signature must be three. Value is " + str(self.compressedChunkSignature) + ".")

    def getCompressedChunkSize(self):
        return self.compressedChunkSize

    def decompressChunk(self, compressedChunk):
        """
        Decompress a bytearray

        :param data bytes: bytes of compressed data
        :return: bytes
        :rtype: bytes
        """
        orig_data = data
        uncompressedChunk = b''
        while len(compressedChunk) > 0:
          #flag is one byte
          flagToken = data[0]
          compressedChunk = compressedChunk[1:]
          if len(compressedChunk) == 0:
              raise Exception("There must be at least one token in each TokenSequence.")
          flagMask = 1
          for i in range(8):
              flag = flagToken & flagMask
              flagMask = flagMask << 1
              if flag == 0:
                  if len(compressedChunk) > 0:
                      uncompressedChunk += compressedChunk[0]
                      compressedChunk = compressedChunk[1:]
              else:
                  if len(compressedChunk) < 2:
                      raise Exception("Copy Token does not exist. FlagToken was " + str(flagToken) + " and decompressed chunk is " + self.uncompressedData + '.')
                  help = copyTokenHelp(len(uncompressedData))
                  copyToken = unpackCopyToken(struct.unpack("<H", data[:2])[0], help)  # Note this this will always be little endian.
                  compressedChunk = compressedChunk[2:]
                  
                  for i in range(copyToken["length"]):
                      offset = copyToken["offset"]
                      length = len(uncompressedData)
                      uncompressedData += uncompressedData[-1 * offset]
        return self.uncompressedData
