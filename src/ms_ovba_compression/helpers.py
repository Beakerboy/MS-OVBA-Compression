def copyTokenHelp(difference):
    """
    Calculate a lengthMask, offsetMask, and bitCount from the length of the
    uncompressedData.
    """
    bitCount = ceilLog2(difference)
    lengthMask = 0xFFFF >> bitCount
    offsetMask = ~lengthMask & 0xFFFF
    maxLength = 0xFFFF << bitCount + 3
    return {
        "lengthMask": lengthMask,
        "offsetMask": offsetMask,
        "bitCount": bitCount,
        "maxLength": maxLength
    }


def unpackCopyToken(copyToken, help):
    """
    calculate an offset and length from a 16 bit copytoken
    """
    length = (copyToken & help["lengthMask"]) + 3
    temp1 = copyToken & help["offsetMask"]
    temp2 = 16 - help["bitCount"]
    offset = (temp1 >> temp2) + 1
    return {
        "length": length,
        "offset": offset
    }


def packCopyToken(length, offset, help):
    """
    Create the copy token from the length, offset, and currect position

    return bytes
    """
    temp1 = offset - 1
    temp2 = 16 - help["bitCount"]
    temp3 = length - 3
    return (temp1 << temp2) | temp3


def ceilLog2(int):
    i = 4
    while 2 ** i < int:
        i += 1
    return i
