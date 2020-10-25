# initializer.py is part of MattFlow
#
# MattFlow is free software; you may redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. You should have received a copy of the GNU
# General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.
#
# (C) 2019 Athanasios Mattas
# ======================================================================
"""Handles the initialization of the simulation"""

#                  x
#          0 1 2 3 4 5 6 7 8 9
#        0 G G G G G G G G G G
#        1 G G G G G G G G G G
#        2 G G - - - - - - G G
#        3 G G - - - - - - G G
#      y 4 G G - - - - - - G G
#        5 G G - - - - - - G G
#        6 G G - - - - - - G G
#        7 G G - - - - - - G G
#        8 G G G G G G G G G G
#        9 G G G G G G G G G G


from random import uniform

import numpy as np

from mattflow import config as conf, dat_writer


def _variance(mode):
    """use small variance to make the distribution steep and sharp, for a
    better representation of a drop"""
    variance = {
        "single drop": 0.0009,
        "drops": 0.0009,
        "rain": 0.0001
    }
    return variance[mode]


def _gaussian(variance, drops_count):
    '''produces a bivariate gaussian distribution of a certain variance

    formula: amplitude * np.exp(-exponent)

    Args:
        variance (float) :  target variance of the distribution
        drops_count(int) :  drop counter

    Returs:
        gaussian_distribution (2D array)
    '''
    # random pick of drop center coordinates
    # (mean or expectation of the gaussian distribution)
    if conf.RANDOM_DROP_CENTERS:
        drop_cx = uniform(conf.MIN_X, conf.MAX_X)
        drop_cy = uniform(conf.MIN_Y, conf.MAX_Y)
    else:
        drop_cx = conf.DROPS_CX[drops_count % 10]
        drop_cy = conf.DROPS_CY[drops_count % 10]

    # grid of the cell centers
    CX, CY = np.meshgrid(conf.CX, conf.CY)

    amplitude = 1 / np.sqrt(2 * np.pi * variance)
    exponent = \
        ((CX - drop_cx)**2 + (CY - drop_cy)**2) / (2 * variance)

    gaussian_distribution = amplitude * np.exp(-exponent)
    return gaussian_distribution


def drop(heights_list, drops_count=None):
    """Generates a drop

    Drop is modeled as a gaussian distribution

    Args:
        heights_list (array)   :  the 0th state variable, U[0, :, :]
        drops_count(int)       :  drop counter

    Returns:
        heights_list(2D array) : drop is added to the input heights_list
    """
    # multiply with 3 / 2 for a small stone droping
    #          with 1 / 5 for a water drop with a considerable momentum build
    #          with 1 / 8 for a soft water drop
    if conf.MODE == 'single drop' or conf.MODE == 'drops':
        variance = _variance("single drop")
        heights_list += 3 / 2 * _gaussian(variance, drops_count)
    elif conf.MODE == 'rain':
        variance = _variance("rain")
        heights_list += 1 / 8 * _gaussian(variance, drops_count)
    else:
        print("Configure MODE | options: 'single drop', 'drops', 'rain'")
    return heights_list


def initialize():
    """creates and initializes the state-variables-3D-matrix, U

    U[0]:  state varables [h, hu, hv], populating the x,y grid
    U[1]:  y dimention (rows)
    U[2]:  x dimention (columns)

    Returns
        U (3D array) :  state-variables-3D-matrix
    """

    U = np.zeros(((3,
                   conf.Ny + 2 * conf.Ng,
                   conf.Nx + 2 * conf.Ng)))

    # 1st drop
    U[0, :, :] = conf.SURFACE_LEVEL + drop(U[0, :, :], drops_count=1)

    # write dat | default: False
    if conf.DAT_WRITING_MODE:
        dat_writer.writeDat(U[0, conf.Ng: -conf.Ng, conf.Ng: -conf.Ng],
                            time=0, it=0)
        from mattflow import mattflow_post
        mattflow_post.plotFromDat(time=0, it=0)
    elif not conf.DAT_WRITING_MODE:
        pass
    else:
        print("Configure DAT_WRITING_MODE | Options: True, False")
    return U
