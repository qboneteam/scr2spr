import os
import argparse
import sys
from array import array


__version__: str = "20190209"


def xytoaddr(xcoord, ycoord):
    return ((ycoord & 0x18) << 8) | ((ycoord & 7) << 5) | (xcoord & 31)


def nextline(someaddr):
    if someaddr & 0x700 != 0x700:
        someaddr += 0x100
    elif someaddr & 0xe0 == 0xe0:
            someaddr += 0x20
    else:
        someaddr -= 0x6e0
    return someaddr


def binary2array(nameoffile):
    data = array('B')
    with open(nameoffile, 'rb') as f:
        data.fromfile(f, os.stat(nameoffile).st_size)
    return data


def savebin2file(perem, nameoffile):
    f = open(nameoffile, 'w+b')
    f.write(bytearray(perem))
    f.close()


def takeonesprite(temp_x, temp_y, temp_w, temp_h, temp_a):
    k = bytearray()
    offset = xytoaddr(temp_x, temp_y)
    for l in range(temp_h * 8):
        k += temp_a[offset:offset + temp_w]
        offset = nextline(offset)
    return k


def takespriteattr(temp_x, temp_y, temp_w, temp_h, temp_a):
    k = bytearray()
    offset = temp_y*32 + temp_x + 6144
    for l in range(temp_h):
        k += temp_a[offset:offset + temp_w]
        offset += 32
    return k


def createparser():
    myparser = argparse.ArgumentParser()
    myparser.add_argument('-x', '--x', default=0, type=int)
    myparser.add_argument('-y', '--y', default=0, type=int)
    myparser.add_argument('-wide', '--width', type=int)
    myparser.add_argument('-high', '--height', type=int)
    myparser.add_argument('-c', '--count', default=1, type=int)
    myparser.add_argument('-col', '--color', default=False, type=bool)
    myparser.add_argument('-i', '--input', type=str)
    myparser.add_argument('-o', '--output', default='sprite.bin', type=str)
    return myparser


def error(message):
    print(message, file=sys.stderr)
    exit(1)


def main():
    parser = createparser()
    namespace = parser.parse_args(sys.argv[1:])
    x = namespace.x
    y = namespace.y
    count = namespace.count
    width = namespace.width
    height = namespace.height
    color = namespace.color

    if width is None or height is None:
        error("Please set width and height of sprite(s)")

    if 32 / width * 24 / height < count:
        error("You want too many sprites....")

    d = bytearray()

    a = binary2array(namespace.input)

    if len(a) not in (6144, 6912):
        error("Strange size of input file. 6144 or 6912 bytes only!")
    if color is True and len(a) == 6144:
        error("You want colors sprites, but you haven't color screen!")
    for j in range(count):
        d += takeonesprite(x, y, width, height, a)
        if color is True:
            d += takespriteattr(x, y, width, height, a)
        if x + width * 2 < 33:
            x += width
        else:
            x = 0
            y += height
            if j != count and y > 23:
                error("The screen ended unexpectedly :(")

    savebin2file(d, namespace.output)


if __name__ == '__main__':
    main()
