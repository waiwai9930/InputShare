import ctypes

def to_uint32(value: int) -> int:
    """
    Convert an integer to a 32-bit unsigned integer using ctypes.

    :param value: The integer to convert.
    :return: The 32-bit unsigned integer.
    """
    return ctypes.c_uint32(value).value

def write32be(buf, offset, value):
    """
    Write a 32-bit unsigned integer in big-endian format to a uint8 array.

    :param buf: The target array where the value will be written.
    :param offset: The starting index in the array where the value will be written.
    :param value: The 32-bit unsigned integer to write.
    """
    # Ensure that the value is within the range of a 32-bit unsigned integer
    if not (0 <= value < 2**32):
        raise ValueError("Value must be a 32-bit unsigned integer")

    # Write the 32-bit value in big-endian format
    buf[offset] = (value >> 24) & 0xFF
    buf[offset + 1] = (value >> 16) & 0xFF
    buf[offset + 2] = (value >> 8) & 0xFF
    buf[offset + 3] = value & 0xFF
