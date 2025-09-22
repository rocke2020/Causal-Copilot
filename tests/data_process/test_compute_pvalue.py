import itertools

import numpy as np
from loguru import logger
from momentchi2 import hbe, lpb4, sw
from scipy.linalg import pinv
from scipy.spatial.distance import pdist, squareform
from scipy.stats import chi2


class RIT(object):
    """
    Python implementation of Randomized Independence Test (RIT) test.
    The original R implementation can be found at https://github.com/ericstrobl/RCIT/tree/master

    References
    ----------
    [1] Strobl, E. V., Zhang, K., and Visweswaran, S. (2019). "Approximate kernel-based conditional
    independence tests for fast non-parametric causal discovery." Journal of Causal Inference, 7(1), 20180017.
    """

    def __init__(self, approx="lpd4"):
        """
        Initialize the RIT object.

        Parameters
        ----------
        approx : str
            Method for approximating the null distribution.
            - "lpd4" for the Lindsay-Pilla-Basak method
            - "hbe" for the Hall-Buckley-Eagleson method
            - "gamma" for the Satterthwaite-Welch method
            - "chi2" for a normalized chi-squared statistic
            - "perm" for permutation testing
            Default is "lpd4".
        """
        self.approx = approx

    def compute_pvalue(self, data_x, data_y):
        """
        Compute the p value and return it together with the test statistic.

        Parameters
        ----------
        data_x: input data for x (nxd1 array)
        data_y: input data for y (nxd2 array)
        data_z: input data for z (nxd3 array)

        Returns
        -------
        p: p value
        sta: test statistic
        """
        logger.info(f"RIT compute_pvalue {data_x.shape = }, {data_y.shape = }")
        logger.info(f'data_x[:10]\n{data_x[:10]}\ndata_y[:10]\n{data_y[:10]}')
        logger.info(f'data_x[-10:]\n{data_x[-10:]}\ndata_y[-10:]\n{data_y[-10:]}')
        r = data_x.shape[0]
        r1 = 500 if (r > 500) else r

        data_x = (data_x - data_x.mean(axis=0)) / data_x.std(axis=0, ddof=1)
        data_y = (data_y - data_y.mean(axis=0)) / data_y.std(axis=0, ddof=1)

        sigma = dict()
        for key, value in [("x", data_x), ("y", data_y)]:
            distances = pdist(value[:r1, :], metric="euclidean")
            flattened_distances = squareform(distances).ravel()
            non_zero_distances = flattened_distances[flattened_distances != 0]
            sigma[key] = np.median(non_zero_distances)

        four_x = self.random_fourier_features(data_x, num_f=5, sigma=sigma["x"])
        four_y = self.random_fourier_features(data_y, num_f=5, sigma=sigma["y"])

        f_x = (four_x - four_x.mean(axis=0)) / four_x.std(axis=0, ddof=1)
        f_y = (four_y - four_y.mean(axis=0)) / four_y.std(axis=0, ddof=1)

        Cxy = self.matrix_cov(f_x, f_y)
        sta = r * np.sum(Cxy**2)

        res_x = f_x - f_x.mean(axis=0)
        res_y = f_y - f_y.mean(axis=0)

        d = list(itertools.product(range(f_x.shape[1]), range(f_y.shape[1])))
        res = np.array([res_x[:, idx_x] * res_y[:, idx_y] for idx_x, idx_y in d]).T
        Cov = 1 / r * res.T @ res

        eigenvalues, eigenvectors = np.linalg.eigh(Cov)
        eig_d = eigenvalues[eigenvalues > 0]

        if self.approx == "gamma":
            p = 1 - sw(eig_d, sta)

        elif self.approx == "hbe":
            p = 1 - hbe(eig_d, sta)

        elif self.approx == "lpd4":
            try:
                p = 1 - lpb4(eig_d, sta)
            except Exception:
                p = 1 - hbe(eig_d, sta)
            if np.isnan(p):
                p = 1 - hbe(eig_d, sta)

        if p < 0:
            p = 0

        return p, sta

    def random_fourier_features(self, x, w=None, b=None, num_f=None, sigma=None):
        """
        Generate random Fourier features.

        Parameters
        ----------
        x : np.ndarray
            Random variable x.
        w : np.ndarray
            RRandom coefficients.
        b : np.ndarray
            Random offsets.
        num_f : int
            Number of random Fourier features.
        sigma : float
            Smooth parameter of RBF kernel.

        Returns
        -------
        feat : np.ndarray
            Random Fourier features.
        """
        if num_f is None:
            num_f = 25

        r = x.shape[0]
        c = x.shape[1]

        if (sigma == 0) | (sigma is None):
            sigma = 1

        if w is None:
            w = (1 / sigma) * np.random.normal(size=(num_f, c))
            b = np.tile(2 * np.pi * np.random.uniform(size=(num_f, 1)), (1, r))

        feat = np.sqrt(2) * (np.cos(w[0:num_f, 0:c] @ x.T + b[0:num_f, :])).T

        return feat

    def matrix_cov(self, mat_a, mat_b):
        """
        Compute the covariance matrix between two matrices.
        Equivalent to ``cov()`` between two matrices in R.

        Parameters
        ----------
        mat_a : np.ndarray
            First data matrix.
        mat_b : np.ndarray
            Second data matrix.

        Returns
        -------
        mat_cov : np.ndarray
            Covariance matrix.
        """
        n_obs = mat_a.shape[0]

        assert mat_a.shape == mat_b.shape
        mat_a = mat_a - mat_a.mean(axis=0)
        mat_b = mat_b - mat_b.mean(axis=0)

        mat_cov = mat_a.T @ mat_b / (n_obs - 1)

        return mat_cov


if __name__ == "__main__":
    import pickle
    import pandas as pd

    # rit = RIT(approx="lpd4")
    # test_data_file = 'rit_input_data.pkl'
    # with open(test_data_file, 'rb') as f:
    #     test_data = pickle.load(f)
    # data_x = test_data['data_x']
    # data_y = test_data['data_y']
    # p, sta = rit.compute_pvalue(data_x, data_y)
    # logger.info(f"RIT test p-value: {p}, stat: {sta}")

    # scaled_df = pd.read_csv("test/scaled_data.csv")
    # print(f'{scaled_df.shape = }')
    # scaled_df = scaled_df.dropna().copy()
    # print(f'{scaled_df.shape = }')