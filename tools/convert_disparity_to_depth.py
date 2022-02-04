import argparse
import numpy as np
import cv2
import csv
import re

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--pfmPath', dest='pfmPath',
                        help='input .pfm depth map path')
    parser.add_argument('--calibPath', dest='calibPath',
                        help='input .txt calib file path')
    parser.add_argument('--exrPath', dest='exrPath',
                        help='output path of .exr file')
    args = parser.parse_args()
    return args

def read_calib(calib_file_path):
    with open(calib_file_path, 'r') as calib_file:
        calib = {}
        csv_reader = csv.reader(calib_file, delimiter='=')
        for attr, value in csv_reader:
            calib.setdefault(attr, value)
    return calib

def read_pfm(pfm_file_path):
    with open(pfm_file_path, 'rb') as pfm_file:
        header = pfm_file.readline().decode().rstrip()
        channels = 3 if header == 'PF' else 1

        dim_match = re.match(r'^(\d+)\s(\d+)\s$', pfm_file.readline().decode('utf-8'))
        if dim_match:
            width, height = map(int, dim_match.groups())
        else:
            raise Exception("Malformed PFM header.")

        scale = float(pfm_file.readline().decode().rstrip())
        if scale < 0:
            endian = '<' # littel endian
            scale = -scale
        else:
            endian = '>' # big endian

        dispariy = np.fromfile(pfm_file, endian + 'f')
    #
    img = np.reshape(dispariy, newshape=(height, width, channels))
    img = np.flipud(img).astype('float32')
    return dispariy, [(height, width, channels), scale]

def create_depth_map(pfm_file_path, calib=None):

    dispariy, [shape,scale] = read_pfm(pfm_file_path)

    if calib is None:
        raise Exception("Loss calibration information.")
    else:
        fx = float(calib['cam0'].split(' ')[0].lstrip('['))
        base_line = float(calib['baseline'])
        doffs = float(calib['doffs'])

		# scale factor is used here
        depth_map = fx*base_line / (dispariy + doffs) / 1000.0
        print(doffs)
        depth_map = np.reshape(depth_map, newshape=shape)
        depth_map = np.flipud(depth_map).astype('float32')
        return depth_map

if __name__ == '__main__':
    print("Convert started.")
    args = parse_args()
#    depthimg = cv2.imread(args.pfmPath, cv2.IMREAD_UNCHANGED)
#    cv2.imwrite(args.exrPath, depthimg)

    calib = read_calib(args.calibPath)
    depthimg = create_depth_map(args.pfmPath, calib)
    cv2.imwrite(args.exrPath, depthimg)
    print("Convert finished.")
