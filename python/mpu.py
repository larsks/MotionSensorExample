#!/usr/bin/python

import argparse
import time
import smbus
import math
import json
import numpy

class MPU6050(object):
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c
    gyro_x = 0x43
    gyro_y = 0x45
    gyro_z = 0x47
    accel_x = 0x3b
    accel_y = 0x3d
    accel_z = 0x3f
    temp = 0x41

    def __init__(self, bus=0, address=0x68, init=True):
        self.bus = smbus.SMBus(bus)
        self.address = address

        if init:
            self.init_device()

    def init_device(self):
        self.write_byte(self.power_mgmt_1, 0)

    def calibrate(self):
        time_start = time.time()
        accel_samples = []
        gyro_samples = []
        while True:
            if time.time() < time_start + 5:
                continue

            accel_samples.append(self.read_accel_raw())
            gyro_samples.append(self.read_gyro_raw())

            if time.time() > time_start + 6:
                break

        print 'collected %d samples' % len(accel_samples)

        accel_x_avg = sum(sample[0] for sample in accel_samples) / len(accel_samples)
        accel_x_std = numpy.std([sample[0] for sample in accel_samples])

        print 'accel x avg = %f, std = %f' % (accel_x_avg, accel_x_std)


    def write_byte(self, reg, val):
        self.bus.write_byte_data(self.address, reg, val)

    def read_byte(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_word(self, reg):
        high = self.read_byte(reg)
        low = self.read_byte(reg+1)
        val = (high << 8) + low
        
        if (val >= 0x8000):
            return -((-65535 - val) + 1)
        else:
            return val

    def read_gyro_raw(self):
        val = [
            self.read_word(self.gyro_x),
            self.read_word(self.gyro_y),
            self.read_word(self.gyro_z),
        ]

        return val
        
    def read_accel_raw(self):
        val = [
            self.read_word(self.accel_x),
            self.read_word(self.accel_y),
            self.read_word(self.accel_z),
        ]

        return val

    def read_temp(self):
        val = self.read_word(self.temp)
        return val
        

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def intish(s):
    if s.isdigit():
        return int(s)
    elif s.starts('0x'):
        return int(s, 16)
    else:
        raise ValueError(s)

def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--bus', '-b', default=0, type=int)
    p.add_argument('--address', '-a', default=0x68, type=intish)
    p.add_argument('--gyro', '-G', action='store_true')
    p.add_argument('--accel', '-A', action='store_true')
    p.add_argument('--axes', '-x', default='xyz')
    p.add_argument('--loop', '-l', action='store_true')
    p.add_argument('--calibrate', '-C', action='store_true')
    p.add_argument('--interval', '-i', default=0, type=float)

    return p.parse_args()

def main():
    args = parse_args()
    dev = MPU6050(bus=args.bus, address=args.address)

    if args.calibrate:
        dev.calibrate()
        return

    while True:
        if args.gyro:
            gyro = dev.read_gyro_raw()
            print 'GYRO %10.2f %10.2f %10.2f' % tuple(gyro),

        if args.accel:
            accel = dev.read_accel_raw()
            print 'ACCEL %10.2f %10.2f %10.2f' % tuple(accel),

        print
        if not args.loop:
            break

        if args.interval:
            time.sleep(args.interval)

if __name__ == '__main__':
    main()
