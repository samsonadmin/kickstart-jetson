#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import time
import argparse

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, LCD_FONT
from luma.core import legacy

"""
Design a bitmap using http://dotmatrixtool.com/#, then paste the generated
hex values over those at lines 21-22.
See https://github.com/rm-hull/luma.led_matrix/issues/170
"""

def demo(w, h, block_orientation, rotate):
    # create matrix device
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=w, height=h, rotate=rotate, block_orientation=block_orientation)
    print("Created device")

    MY_CUSTOM_BITMAP_FONT = [
        [
            0x10, 0x20, 0x40, 0xff, 0x40, 0x20, 0x10, 0x00
        ]
    ]    

    with canvas(device) as draw:        

        #legacy.text(draw, (0, 0), "\0", fill="white", font=MY_CUSTOM_BITMAP_FONT)

        draw.line( (0,0, 6,0), fill="white" )
        draw.line( (0,4, 3,1), fill="white" )
        draw.line( (3,1, 6,4), fill="white" )
        draw.line( (3,1, 3,7), fill="white" )

        #draw.point( (0,4), fill="white")
        #draw.point( (3,1), fill="white")
        #draw.point( (6,4), fill="white")
        #draw.point( (3,7), fill="white")

        #draw.line( (1,4, 7,4), fill="white" )
        #draw.line( (1,4, 8,4), fill="white" )
        draw.rectangle(device.bounding_box, outline="white")
        #text(draw, (2, 2), "Hello", fill="white", font=proportional(LCD_FONT))
        #text(draw, (2, 10), "World", fill="white", font=proportional(LCD_FONT))

    time.sleep(1)

    #for _ in range(2):
    #    time.sleep(0.05)
    #    device.hide()

    #    time.sleep(0.05)
    #    device.show()

    for _ in range(10):
        for level in range(255, -1, -10):
            device.contrast(level)
            time.sleep(0.001)
        time.sleep(0.5)

        for level in range(0, 255, 10):
            device.contrast(level)
            time.sleep(0.001)

        time.sleep(0.5)

    #device.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='matrix_demo arguments',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--width', type=int, default=8, help='Width')
    parser.add_argument('--height', type=int, default=8, help='height')
    parser.add_argument('--block-orientation', type=int, default=-90, choices=[0, 90, -90], help='Corrects block orientation when wired vertically')
    parser.add_argument('--rotate', type=int, default=0, choices=[0, 1, 2, 3], help='Rotation factor')

    args = parser.parse_args()

    try:
        demo(args.width, args.height, args.block_orientation, args.rotate)
    except KeyboardInterrupt:
        pass
