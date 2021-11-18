
def maskToInt(mask: int) -> int:
    '''Convert a mask length (e.g., 24) into the 32-bit value (e.g., 24 1 bits
    followed by 8 0 bits.'''
    return ((2 ** mask) - 1) << (32 - mask)


def maskToHostMask(mask_numbits: int) -> int:
    '''Convert a network mask (e.g., 24) into the 32-bit value where only the
    host part has 1 bits.'''
    # Top (32 - mask_numbits) bits are 0, followed by all 1.
    return 2 ** (32 - mask_numbits) - 1


# ref: https://stackoverflow.com/questions/5619685/conversion-from-ip-string-to-integer-and-backward-in-python
def ipToInt(ip):
    '''Convert an IP address (e.g. 10.11.12.13) into an integer.'''
    ip = [int(part) for part in ip.split('.')]
    return (16777216 * ip[0]) + (65536 * ip[1]) + (256 * ip[2]) + ip[3]


if __name__ == "__main__":
    assert maskToHostMask(24) == 0b11111111
    assert maskToHostMask(8) == 0b11111111_11111111_11111111
    print("Utils: all tests passed")
