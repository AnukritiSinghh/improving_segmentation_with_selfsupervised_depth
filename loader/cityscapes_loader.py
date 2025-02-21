# Based on https://github.com/meetshah1995/pytorch-semseg/blob/master/ptsemseg/loader/cityscapes_loader.py

import os

import numpy as np

from loader.sequence_segmentation_loader import SequenceSegmentationLoader
from utils.utils import recursive_glob


class Cityscapes:
    n_classes = 20
    ignore_index = 250

    colors = [  [  0,   0,   0],
        [0, 102, 0],
        [255, 153, 204],
        [99, 66, 34],
        [0, 255, 0],
        [0, 0, 255],
        [134, 255, 239],
        [102, 0, 204],
        [255, 0, 127],
        [255, 255, 0],  
        [170, 170, 170],
        [99, 66, 34],
        [204, 153, 255],
        [110, 22, 138],
        [41, 121, 255],
        [0, 153, 153],
        [0, 128, 255],
        [64, 64, 64],         
        [255, 0, 0],
        [102, 0, 0],
    ]

    label_colours = dict(zip(range(n_classes), colors))

    void_classes = [-1]
    valid_classes = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
    ]
    class_names = [
        "unlabelled",
        "grass",
        "bush",
        "dirt",
        "tree",
        "sky",
        "puddle",
        "fence",
        "object",
        "vehicle",  
        "concrete",
        "mud",
        "person",
        "rubble",
        "barrier",
        "pole",
        "water",
        "asphalt",         
        "building",
        "log",
    ]

    class_map = dict(zip(valid_classes, range(n_classes)))
    decode_class_map = dict(zip(range(n_classes), valid_classes))

    @staticmethod
    def decode_segmap_tocolor(temp):
        r = temp.copy()
        g = temp.copy()
        b = temp.copy()
        for l in range(0, Cityscapes.n_classes):
            r[temp == l] = Cityscapes.label_colours[l][0]
            g[temp == l] = Cityscapes.label_colours[l][1]
            b[temp == l] = Cityscapes.label_colours[l][2]

        rgb = np.zeros((temp.shape[0], temp.shape[1], 3))
        rgb[:, :, 0] = r / 255.0
        rgb[:, :, 1] = g / 255.0
        rgb[:, :, 2] = b / 255.0
        return rgb

    @staticmethod
    def encode_segmap(mask):
        # Put all void classes to zero
        for _voidc in Cityscapes.void_classes:
            mask[mask == _voidc] = Cityscapes.ignore_index
        for _validc in Cityscapes.valid_classes:
            mask[mask == _validc] = Cityscapes.class_map[_validc]
        return mask

class CityscapesLoader(SequenceSegmentationLoader):
    def __init__(self, **kwargs):
        super(CityscapesLoader, self).__init__(**kwargs)

        self.n_classes = Cityscapes.n_classes
        self.ignore_index = Cityscapes.ignore_index
        self.void_classes = Cityscapes.void_classes
        self.valid_classes = Cityscapes.valid_classes
        self.label_colors = Cityscapes.label_colours
        self.class_names = Cityscapes.class_names
        self.class_map = Cityscapes.class_map
        self.decode_class_map = Cityscapes.decode_class_map

        self.full_res_shape = (2048, 1024)
        # See https://www.cityscapes-dataset.com/file-handling/?packageID=8
        self.fx = 2262.52
        self.fy = 2265.3017905988554
        self.u0 = 1096.98
        self.v0 = 513.137

    def _prepare_filenames(self):
        if self.img_size == (512, 1024):
            self.images_base = os.path.join(self.root, "leftImg8bit_small", self.split)
            self.sequence_base = os.path.join(self.root, "leftImg8bit_sequence_small", self.split)
        elif self.img_size == (256, 512):
            self.images_base = os.path.join(self.root, "leftImg8bit_tiny", self.split)
            self.sequence_base = os.path.join(self.root, "leftImg8bit_sequence_tiny", self.split)
        else:
            raise NotImplementedError(f"Unexpected image size {self.img_size}")
        self.annotations_base = os.path.join(self.root, "gtFine", self.split)

        if self.only_sequences_with_segmentation:
            self.files = sorted(recursive_glob(rootdir=self.images_base))
        else:
            self.files = sorted(recursive_glob(rootdir=self.sequence_base))

    def get_image_path(self, index, offset=0):
        img_path = self.files[index]["name"].rstrip()
        if offset != 0:
            img_path = img_path.replace(self.images_base, self.sequence_base)
            prefix, frame_number, suffix = img_path.rsplit('_', 2)
            frame_number = int(frame_number)
            img_path = f"{prefix}_{frame_number + offset:06d}_{suffix}"
        return img_path

    def get_segmentation_path(self, index):
        img_path = self.files[index]["name"].rstrip()
        segmentation_path = os.path.join(
            self.annotations_base,
            img_path.split(os.sep)[-2],
            os.path.basename(img_path)[:-15] + "gtFine_labelIds.png",
        )
        return segmentation_path

    def decode_segmap_tocolor(self, temp):
        return Cityscapes.decode_segmap_tocolor(temp)

    def encode_segmap(self, mask):
        return Cityscapes.encode_segmap(mask)
