from __future__ import division
import autograd.numpy as np
from autograd.scipy.misc import logsumexp

from nnet import gmlp, init_gmlp, sigmoid

def gaussian_loglike(x, mu, log_sigmasq):
    return np.mean(logsumexp(
        -0.5*((np.log(2*np.pi) + log_sigmasq) + (x - mu)**2. / np.exp(log_sigmasq)),
        axis=0))

def make_regression(L2_reg, unflatten):
    def predict(im, params):
        mu, log_sigmasq = gmlp(im, params)
        return np.squeeze(2*np.pi*sigmoid(mu)), np.squeeze(log_sigmasq)

    def loglike(theta, prediction):
        theta_hat, log_sigmasq_hat = prediction
        effective_thetas = theta + np.array([-2*np.pi, 0., 2*np.pi])[:,None]
        return gaussian_loglike(effective_thetas, theta_hat, log_sigmasq_hat)

    def logprior(paramvec):
        return -L2_reg * np.dot(paramvec, paramvec)

    def loss(paramvec, im, angle):
        return - logprior(paramvec) - loglike(angle, predict(im, unflatten(paramvec)))

    return loss
