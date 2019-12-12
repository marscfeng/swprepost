"""Tests for Parameter class."""

import swipp
import unittest
import os
import logging
logging.basicConfig(level=logging.ERROR)


class TestParameter(unittest.TestCase):

    def assertListAlmostEqual(self, list1, list2, places=None, delta=None):
        for a, b in zip(list1, list2):
            self.assertAlmostEqual(a, b, places=None, delta=None)

    def test_init(self):
        # Define parameterization in terms of depths
        par_type = "CD"
        lay_min = [1, 5]
        lay_max = [3, 16]
        par_min = [200, 400]
        par_max = [400, 600]
        par_rev = [True, False]
        mypar = swipp.Parameter(par_type, lay_min, lay_max,
                                par_min, par_max, par_rev)
        self.assertEqual(par_type, mypar.par_type)
        self.assertListEqual(lay_min, mypar.lay_min)
        self.assertListEqual(lay_max, mypar.lay_max)
        self.assertListEqual(par_min, mypar.par_min)
        self.assertListEqual(par_max, mypar.par_max)
        self.assertListEqual(par_rev, mypar.par_rev)

        # Define parameters in terms of thicknesses
        par_type = "CT"
        lay_min = [1, 5]
        lay_max = [3, 16]
        par_min = [200, 400]
        par_max = [400, 600]
        par_rev = [True, False]
        mypar = swipp.Parameter(par_type, lay_min, lay_max,
                                par_min, par_max, par_rev)
        self.assertEqual(par_type, mypar.par_type)
        self.assertListEqual(lay_min, mypar.lay_min)
        self.assertListEqual(lay_max, mypar.lay_max)
        self.assertListEqual(par_min, mypar.par_min)
        self.assertListEqual(par_max, mypar.par_max)
        self.assertListEqual(par_rev, mypar.par_rev)

    def test_check_wavelengths(self):
        wmin, wmax = (1, 100)
        # Proper Order
        self.assertTupleEqual((wmin, wmax,),
                              swipp.Parameter.check_wavelengths(wmin, wmax))
        # Reverse Order
        self.assertTupleEqual((wmin, wmax,),
                              swipp.Parameter.check_wavelengths(wmax, wmin))
        # Raise TypeError
        for val in ['1', True, (1, 2)]:
            self.assertRaises(
                TypeError, swipp.Parameter.check_wavelengths, wmin, val)
        # Raise ValueError
        for val in [0, -1, -0.01]:
            self.assertRaises(
                ValueError, swipp.Parameter.check_wavelengths, wmin, val)

    def test_check_depth_factor(self):
        # Raise TypeError
        for factor in ['2', True, [2.0]]:
            self.assertRaises(TypeError,
                              swipp.Parameter.check_depth_factor, factor)

    def test_from_fx(self):
        # Raise TypeError
        for val in ["1", True, [1], (1,)]:
            self.assertRaises(TypeError, swipp.Parameter.from_fx, val)
        # Raise ValueError
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.from_fx, val)

    def test_depth_ftl(self):
        # TypeError - nlayers
        for val in ["1", True, [1], (1,), 1.1]:
            self.assertRaises(TypeError, swipp.Parameter.depth_ftl, val, 1.)
        # ValueError - nlayers
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.depth_ftl, val, 1.)
        # TypeError - thickness
        for val in ["1", True, [1], (1,)]:
            self.assertRaises(TypeError, swipp.Parameter.depth_ftl, 1, val)
        # ValueError - thickness.
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.depth_ftl, 1, val)

    def test_depth_ln_thickness(self):
        wmin, wmax = 1, 100
        # TypeError - nlayers
        for val in ["5", True, 0.5, 2.2]:
            self.assertRaises(TypeError, swipp.Parameter.depth_ln_thickness,
                              wmin, wmax, val)
        # ValueError - nlayers
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.depth_ln_thickness,
                              wmin, wmax, val)

    def test_depth_ln_depth(self):
        wmin, wmax = 1, 100
        # TypeError - nlayers
        for val in ["5", True, 0.5, 2.2]:
            self.assertRaises(TypeError, swipp.Parameter.depth_ln_depth,
                              wmin, wmax, val)
        # ValueError - nlayers
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.depth_ln_depth,
                              wmin, wmax, val)
        # Simple example
        nlayers = 5
        lay_min, lay_max = swipp.Parameter.depth_ln_depth(wmin=wmin, wmax=wmax,
                                                          nlayers=nlayers,
                                                          depth_factor=2)
        expected_lay_min = [1/3, 2/3, 3/3, 4/3, 5/3]
        expected_lay_max = [wmax/2]*nlayers
        self.assertListAlmostEqual(expected_lay_min, lay_min)
        self.assertListAlmostEqual(expected_lay_max, lay_max)

    def test_from_ln_thickness(self):
        wmin, wmax = 1, 100
        par_min, par_max, par_rev = 100, 200, True
        # TypeError - nlayers
        for val in ["5", True, 0.5, 2.2]:
            self.assertRaises(TypeError, swipp.Parameter.from_ln_thickness, wmin, wmax,
                              val, par_min, par_max, par_rev)
        # ValueError - nlayers
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.from_ln_thickness, wmin, wmax,
                              val, par_min, par_max, par_rev)
        # TypeError - increasing_factor
        for val in ["5", True]:
            self.assertRaises(TypeError, swipp.Parameter.from_ln_thickness, wmin, wmax,
                              3, par_min, par_max, par_rev, increasing=True,
                              increasing_factor=val)
        # ValueError - increasing_factor
        for val in [-1, 0, 1]:
            self.assertRaises(ValueError, swipp.Parameter.from_ln_thickness, wmin, wmax,
                              3, par_min, par_max, par_rev, increasing=True,
                              increasing_factor=val)

    def test_from_ln_depth(self):
        wmin, wmax = 1, 100
        par_min, par_max, par_rev = 100, 200, True
        # TypeError - nlayers
        for val in ["5", True, 0.5, 2.2]:
            self.assertRaises(TypeError, swipp.Parameter.from_ln_depth, wmin, wmax,
                              val, par_min, par_max, par_rev)
        # ValueError - nlayers
        for val in [-1, 0]:
            self.assertRaises(ValueError, swipp.Parameter.from_ln_depth, wmin, wmax,
                              val, par_min, par_max, par_rev)

    def test_depth_lr(self):
        wmin, wmax = 1, 100
        # TypeError - lr
        for val in ["5", True]:
            self.assertRaises(TypeError, swipp.Parameter.depth_lr, wmin, wmax,
                              val)
        # ValueError - lr
        for val in [-1, 0, 0.5, 0.9, 1, 1.0]:
            self.assertRaises(ValueError, swipp.Parameter.depth_lr, wmin, wmax,
                              val)
        # Test Calculation
        known_lr = {'1.4':
                    [[0.3, 0.5, 1.2, 2.2, 3.6, 5.5, 8.2, 11.9, 17.2, 24.6, 34.9, 50],
                     [0.5, 1.2, 2.2, 3.6, 5.5, 8.2, 11.9, 17.2, 24.6, 34.9, 50, 51]],
                    '1.5':
                    [[0.3, 0.5, 1.3, 2.4, 4.1, 6.6, 10.4, 16.1, 24.6, 50],
                     [0.5, 1.3, 2.4, 4.1, 6.6, 10.4, 16.1, 24.6, 50, 51]],
                    '2.0':
                    [[0.3, 0.5, 1.5, 3.5, 7.5, 15.5, 31.5, 50],
                     [0.5, 1.5, 3.5, 7.5, 15.5, 31.5, 50, 51]],
                    '3.0':
                    [[0.3, 0.5, 2.0, 6.5, 20, 50],
                     [0.5, 2.0, 6.5, 20, 50, 51]],
                    '5.0':
                    [[0.3, 0.5, 3.0, 15.5, 50],
                     [0.5, 3.0, 15.5, 50, 51]]}
        for key in known_lr.keys():
            mindepth, maxdepth = swipp.Parameter.depth_lr(wmin, wmax,
                                                          lr=float(key),
                                                          depth_factor=2)
            for known1, test1, known2, test2 in zip(mindepth, known_lr[key][0], maxdepth, known_lr[key][1]):
                self.assertAlmostEqual(known1, test1, delta=0.051)
                self.assertAlmostEqual(known2, test2, delta=0.051)

    # def test_plot(self):
    #     import matplotlib.pyplot as plt
    #     # par = swipp.Parameter.from_lr(2, 50, 5, 100, 500, False)
    #     par = swipp.Parameter.from_ln_depth(2, 50, 5, 100, 500, False)

    #     par.plot(show_example=True)
    #     # par.plot(show_example=False)
    #     plt.show()


if __name__ == '__main__':
    unittest.main()