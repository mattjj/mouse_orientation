from __future__ import division
import numpy as np
import cPickle as pickle
import os
import sys
import gzip

from mouse_orientation.canonicalize import reorient_video
from mouse_orientation.util import make_movie

def open_pkl_or_pklgz(filename, mode):
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    return open(filename, mode)

def iteritems(datadict):
    for name, frames in datadict.iteritems():
        print '  processing {}...'.format(name)
        yield name, frames

if __name__ == "__main__":
    if not 4 <= len(sys.argv) <= 5:
        print '{} nnet_params.pkl input_dict.pkl output_dict.pkl [moviedir]'.format(sys.argv[0])
        sys.exit(1)

    nnet_params_filename, input_filename, output_filename = sys.argv[1:4]
    moviedir = sys.argv[4] if len(sys.argv) == 5 else None
    sigmasq_states = 0.1**2

    with open(nnet_params_filename, 'r') as infile:
        nnet_params = pickle.load(infile)

    print 'loading from {}...'.format(input_filename)
    with open_pkl_or_pklgz(input_filename, 'r') as infile:
        datadict = pickle.load(infile)
    print '...done!'

    # reorient each video
    print 're-orienting video sequences...'
    reoriented_datadict = \
        {name: reorient_video(nnet_params, frames, sigmasq_states, inflate_vars=1.)
         for name, frames in iteritems(datadict)}
    print '...done!'

    # save the result
    print 'saving to {}...'.format(output_filename)
    with open(output_filename, 'w') as outfile:
        pickle.dump(reoriented_datadict, outfile, protocol=-1)
    print '...done!'

    # make some movies
    if moviedir:
        print 'making movies...'
        for name, frames in reoriented_datadict.iteritems():
            name = os.path.split(name)[-1] + '.mp4'
            make_movie(frames, os.path.join(moviedir, name))
        print '...done!'
