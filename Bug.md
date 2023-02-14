Page 110 provides This as the uncompressed input:

    23 61 61 61 62 63 64 65 66 61 61 61 61 67 68 69
    6a 61 61 61 61 61 6B 6C 61 61 61 6D 6E 6F 70 71
    61 61 61 61 61 61 61 61 61 61 61 61 72 73 74 75 76
    77 78 79 7A 61 61 61

And this as the compressed output:

    01 2F B0 00 23 61 61 61 62 63 64 65 82 66 00 70 61 67 68 69 6A 01 38 08 61 6B 6C 00 30 6D 6E 6F 70 06 71 02 70 04 10 72 73 74 75 76 10 77 78 79
    7A 00 3C

If we split the final output into token sequences we get;

Container signature = 01
chunk header = 2F B0
Token sequences. The two-byte copy tokens are distinguished from literal tokens with brackets.
1 = 00 23 61 61 61 62 63 64 65
2 = 82 66 [00 70] 61 67 68 69 6A [01 38]
3 = 08 61 6B 6C [00 30] 6D 6E 6F 70
4 = 06 71 [02 70] [04 10] 72 73 74 75 76
5 = 10 77 78 79 7A [00 3C]

The differences I’m seeing are at the copy token in the third sequence, the second copy token in the 4th sequence, and the final copy token.

I’ll work the 3rd token sequence by hand to demonstrate what is expected given my understanding of the pseudo-code.
