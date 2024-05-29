#hamming.py
def hamming_encode(data):
    d = [int(bit) for bit in data]
    p1 = d[0] ^ d[1] ^ d[3]
    p2 = d[0] ^ d[2] ^ d[3]
    p4 = d[1] ^ d[2] ^ d[3]
    encoded_data = [p1, p2, d[0], p4, d[1], d[2], d[3]]
    return ''.join(map(str, encoded_data))

def hamming_decode(data):
    d = [int(bit) for bit in data]
    p1 = d[0] ^ d[2] ^ d[4] ^ d[6]
    p2 = d[1] ^ d[2] ^ d[5] ^ d[6]
    p4 = d[3] ^ d[4] ^ d[5] ^ d[6]
    error_pos = p1 * 1 + p2 * 2 + p4 * 4
    if error_pos != 0:
        d[error_pos - 1] ^= 1
    decoded_data = [d[2], d[4], d[5], d[6]]
    return ''.join(map(str, decoded_data))
