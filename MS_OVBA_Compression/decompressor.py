import struct
from MS_OVBA_Compression.helpers import *
class Decompressor:

    def __init__(self, endian = 'little'):
        self.endian = endian
        self.uncompressedData = bytearray(b'')
        
        # The chunk after compression
        self.compressedData = bytearray(b'')

        #the size in bytes of the chunk after compression
        self.compressedChunkSize = 0

        # is the data compressed?
        self.compressed = 1

    def setCompressedData(self, data):
        """
        set the Compressed data attribute
        """
        if len(data) != self.compressedChunkSize - 2:
            raise Exception("Expecting " + str(self.compressedChunkSize - 2) + " bytes, but given " + str(len(data)) + ".")
        self.compressedData = data

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

    def getCompressedChunk(self):  
        return self.getCompressedChunkHeader() + self.compressedData

    def getCompressedChunkHeader(self):
        compressedChunkFlag = 1 if self.compressed else 0
        intHeader = (self.compressed << 15) | 0x3000 | (self.compressedChunkSize - 3)
        packSymbol = '<' if self.endian == 'little' else '>'
        format = packSymbol + 'H'
        return struct.pack(format, intHeader)

    def decompress(self, data):
        orig_data = data
        """
        Decompress a bytearray

        :param data bytes: bytes of compressed data
        :return: bytes
        :rtype: bytes
        """
        while len(data) > 0:
          #flag is one byte
          flagToken = data.pop(0)
          if len(data) == 0:
              raise Exception("There must be at least one token in each TokenSequence.")
          flagMask = 1
          for i in range(8):
              flag = flagToken & flagMask
              flagMask = flagMask << 1
              if flag == 0:
                  if len(data) > 0:
                      self.uncompressedData.append(data.pop(0))
              else:
                  if len(data) < 2:
                      raise Exception("Copy Token does not exist. FlagToken was " + str(flagToken) + " and decompressed chunk is " + self.uncompressedData + '.')
                  help = copyTokenHelp(len(self.uncompressedData))
                  copyToken = unpackCopyToken(struct.unpack("<H", data[:2])[0], help)  # Note this this will always be little endian.
                  del data[:2]
                  
                  for i in range(copyToken["length"]):
                      offset = copyToken["offset"]
                      length = len(self.uncompressedData)
                      self.uncompressedData.append(self.uncompressedData[-1 * offset])
        return self.uncompressedData
