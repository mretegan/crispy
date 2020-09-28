# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The module implements fast FFT broadening."""

import numpy as np

MIN_KERNEL_SUM = 1e-8


def gaussian_kernel1d(sigma=None, truncate=6):
    size = int(2 * truncate * sigma)
    if size % 2 == 0:
        size = size + 1
    x = np.arange(size)
    # print('The size of the kernel is: {}'.format(size))
    mu = np.median(x)
    # The prefactor 1 / (sigma * np.sqrt(2 * np.pi))
    # drops in the normalization.
    kernel = np.exp(-0.5 * ((x - mu) ** 2 / sigma ** 2))
    if kernel.sum() < MIN_KERNEL_SUM:
        raise Exception(
            "The kernel can't be normalized, because its sum is close to "
            "zero. The sum of the kernel is < {0}".format(MIN_KERNEL_SUM)
        )
    kernel /= kernel.sum()
    return kernel


def gaussian_kernel2d(sigma=None, truncate=(6, 6)):
    if sigma.size != 2 or len(truncate) != 2:
        raise Exception(
            "Sigma and the truncation parameter don't have the required dimensions."
        )
    kernel_x = gaussian_kernel1d(sigma[0], truncate[0])
    kernel_y = gaussian_kernel1d(sigma[1], truncate[1])
    kernel = np.outer(kernel_y, kernel_x)
    return kernel


def convolve_fft(array, kernel):
    """Convolve an array with a kernel using FFT.
    Implementation based on the convolve_fft function from astropy.

    https://github.com/astropy/astropy/blob/master/astropy/convolution/convolve.py
    """
    # pylint: disable=too-many-locals
    array = np.asarray(array, dtype=np.complex)
    kernel = np.asarray(kernel, dtype=np.complex)

    if array.ndim != kernel.ndim:
        raise ValueError("Image and kernel must have same number of dimensions")

    array_shape = array.shape
    kernel_shape = kernel.shape
    new_shape = np.array(array_shape) + np.array(kernel_shape)

    array_slices = []
    kernel_slices = []
    for (new_dimsize, array_dimsize, kernel_dimsize) in zip(
        new_shape, array_shape, kernel_shape
    ):
        center = new_dimsize - (new_dimsize + 1) // 2
        array_slices += [
            slice(center - array_dimsize // 2, center + (array_dimsize + 1) // 2)
        ]
        kernel_slices += [
            slice(center - kernel_dimsize // 2, center + (kernel_dimsize + 1) // 2)
        ]

    array_slices = tuple(array_slices)
    kernel_slices = tuple(kernel_slices)

    if not np.all(new_shape == array_shape):
        big_array = np.zeros(new_shape, dtype=np.complex)
        big_array[array_slices] = array
    else:
        big_array = array

    if not np.all(new_shape == kernel_shape):
        big_kernel = np.zeros(new_shape, dtype=np.complex)
        big_kernel[kernel_slices] = kernel
    else:
        big_kernel = kernel

    array_fft = np.fft.fftn(big_array)
    kernel_fft = np.fft.fftn(np.fft.ifftshift(big_kernel))

    rifft = np.fft.ifftn(array_fft * kernel_fft)

    return rifft[array_slices].real


def broaden(array, fwhm=None, kind="gaussian"):
    if fwhm is None:
        return array

    fwhm = np.array(fwhm)
    if (fwhm <= 0).any():
        return array

    kernel = None
    if kind == "gaussian":
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        if fwhm.size == 1:
            kernel = gaussian_kernel1d(sigma)
        elif fwhm.size == 2:
            kernel = gaussian_kernel2d(sigma)

    if kernel is None:
        return array

    return convolve_fft(array, kernel)
