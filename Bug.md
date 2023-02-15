Page 110 of [MS OVBA](https://interoperability.blob.core.windows.net/files/MS-OVBA/%5bMS-OVBA%5d.pdf) provides this as the uncompressed input:

    23 61 61 61 62 63 64 65 66 61 61 61 61 67 68 69
    6a 61 61 61 61 61 6B 6C 61 61 61 6D 6E 6F 70 71
    61 61 61 61 61 61 61 61 61 61 61 61 72 73 74 75
    76 77 78 79 7A 61 61 61

And this as the compressed output:

    01 2F B0 00 23 61 61 61 62 63 64 65 82 66 00 70
    61 67 68 69 6A 01 38 08 61 6B 6C 00 30 6D 6E 6F
    70 06 71 02 70 04 10 72 73 74 75 76 10 77 78 79
    7A 00 3C

If we split the final output into token sequences and
swap the little-endien encoded words:

    Container signature = 01
    chunk header = B0 2F

Token sequences. The two-byte copy tokens are distinguished
from literal tokens with brackets.

    1 = 00 23 61 61 61 62 63 64 65
    2 = 82 66 [70 00] 61 67 68 69 6A [38 01]
    3 = 08 61 6B 6C [30 00] 6D 6E 6F 70
    4 = 06 71 [70 02] [10 04] 72 73 74 75 76
    5 = 10 77 78 79 7A [3C 00]

The differences I’m seeing are at the copy token in the third
sequence, the second copy token in the 4th sequence, and
the final copy token.

I’ll work the 3rd token sequence by hand to demonstrate
what is expected given my understanding of the pseudo-code.

At this point in the compressing a token sequence function, we ha e the following state variables:

    index=3
    compressedcurrent=26
    decompressedCurrent=24

Running through the matching algorithm, we set candidate to
decompressedCurrent-1, so 23. Byte at 23 is 6C, while the byte
at 24 is 61, so we decrement the candidate. The same occurs until
candidate is 21. At this point the inner while loop iterates once
to give is a length of 1. We decrement candidate again and again
find a match, this time of length 2, so this is the new BestLength.
We decrement Candidate again (to 19) and find a match of length three.
We continue to decrement the candidate and find other length 3 matches,
but since the length is never greater then three, the BestCandidate
remains 19 and the BestLength three.

The offset is the difference between DecompressedCurrent and BestCandidate,
so 5, and the length is 3.

Now we call CopyTokenHelp:

    difference = 24 - 0 = 24
    BitCount = max⌈log₂(24)⌉, 4) = max(⌈4.58⌉, 4) = 5
    LengthMask = 0xFFFF >> 5 = 0x07FF
    OffsetMask = ~0x07FF = 0xF800
 
And a call to PackCopytoken:

    temp1 = Offset - 1 = 4
    temp2 = 16 - BitCount = 11
    temp3 = Length - 3 = 0
    Token = (temp1 LEFT SHIFT BY temp2) BITWISE OR temp3
          = (4 << 11) | 0 = 0x0004 << 11 = 0x2000

So we see the token should be 0x2000 instead of the 0x3000
that is published in the document. If we unpack 0x3000 we
get the same length, 3, but a different offset. For some
reason the matching algorithm is not returning the first
best candidate, but instead a different match.
