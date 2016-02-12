from __future__ import division
import numpy as np
import numpy.random as npr
from skimage.measure import label, regionprops
from util import rotate
import cPickle as pickle
import operator as op

def load_training_data(filename, augmentation=0):
    print 'loading training data...'

    with open(filename, 'r') as infile:
        train_tuples, _ = pickle.load(infile)

    def clean_image(im):
        props = sorted(regionprops(label(im > 15.)), key=op.attrgetter('area'))[-1]
        min_row, min_col, max_row, max_col = props.bbox
        out = np.zeros_like(im)
        out[min_row:max_row,min_col:max_col] = im[min_row:max_row,min_col:max_col]
        return out

    wrap_angle = lambda angle: angle % (2*np.pi)
    flip = lambda angle, label: angle if label == 'u' else (np.pi + angle)
    unpack = lambda (im, angle, label): (clean_image(im), flip(angle, label))

    images, angles = map(np.array, zip(*map(unpack, train_tuples)))

    if augmentation > 0:
        random_rotations = lambda size: npr.uniform(0, 2*np.pi, size=size)

        def augment(images, angles):
            def rot(pair, rotation):
                im, angle = pair
                return rotate(im, rotation), wrap_angle(angle - rotation)

            return zip(*map(rot, zip(images, angles), random_rotations(len(angles))))

        aug_images, aug_angles = zip(*[augment(images, angles) for _ in xrange(augmentation)])
        images = np.concatenate((images,) + aug_images)
        angles = np.concatenate((angles,) + aug_angles)

    assert np.all(angles >= 0.) and np.all(angles < 2*np.pi)
    perm = npr.permutation(images.shape[0])
    images, angles = images[perm], angles[perm]

    print '...done loading {} frames ({} raw, augmented {}x)'.format(
        images.shape[0], len(train_tuples), 1+augmentation)
    return images.reshape(images.shape[0], -1), angles
