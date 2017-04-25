import numpy as np
import pandas as pd
from time import time


class MLAT:
    @staticmethod
    def __d(p1, p2):
        return np.linalg.norm(p1 - p2)

    @staticmethod
    def gdescent(anchors_in, ranges_in, bounds_in=((0, 0, 0),),
                 n_trial=100, alpha=0.001, time_threshold=None):
        anchors = np.array(anchors_in, dtype=float)
        n, dim = anchors.shape
        bounds_temp = anchors
        if bounds_in is not None:
            bounds_temp = np.append(bounds_temp, bounds_in, axis=0)
        bounds = np.empty((2, dim))
        for i in range(dim):
            bounds[0, i] = np.min(bounds_temp[:, i])
            bounds[1, i] = np.max(bounds_temp[:, i])

        if time_threshold is None:
            time_threshold = 1.0 / n_trial

        ranges = np.empty(n)
        result = pd.DataFrame(columns=['estimator', 'error'],
                              index=np.arange(n_trial))
        for i in range(n_trial):
            estimator0 = np.empty(dim)
            for j in range(dim):
                estimator0[j] = np.random.uniform(bounds[0, j], bounds[1, j])
            estimator = np.copy(estimator0)

            t0 = time()
            while True:
                for j in range(n):
                    ranges[j] = MLAT.__d(anchors[j, :], estimator)
                error = MLAT.__d(ranges_in, ranges)

                delta = np.zeros(dim)
                for j in range(n):
                    delta += (ranges_in[j] - ranges[j]) / ranges[j] * \
                             (estimator - anchors[j, :])
                delta *= 2 * alpha

                estimator_next = estimator - delta
                for j in range(n):
                    ranges[j] = MLAT.__d(anchors[j, :], estimator_next)
                error_next = MLAT.__d(ranges_in, ranges)
                if error_next < error:
                    estimator = estimator_next
                else:
                    result['estimator'][i] = estimator
                    result['error'][i] = error
                    break
                if time() - t0 > time_threshold:
                    break
        return result

    @staticmethod
    def mlat(anchors_in, ranges_in, bounds_in=((0, 0, 0),),
             n_trial=100, alpha=0.001, time_threshold=None):
        ret = MLAT.gdescent(anchors_in, ranges_in, bounds_in,
                            n_trial, alpha, time_threshold)

        idx = np.nanargmin(ret['error'])
        estimator = ret['estimator'][idx]
        return estimator, ret

    @staticmethod
    def demo():
        W = 9
        L = 9
        H = 3
        anchors = np.array([[0, 0, H],
                            [W, 0, H],
                            [W, L, H],
                            [0, L, H]])
        node = np.array([W * np.random.rand(),
                         L * np.random.rand(),
                         H * np.random.rand()])
        ranges = np.empty(anchors.shape[0])
        error = 0.5
        ranges_with_error = np.empty(anchors.shape[0])
        for i in range(anchors.shape[0]):
            ranges[i] = np.linalg.norm(anchors[i, :] - node)
            ranges_with_error[i] = ranges[i] + np.random.uniform(-error, error)

        estimator, result = MLAT.mlat(anchors, ranges_with_error)

        print('Anchors')
        print(anchors)
        print('Node:', node)
        print('Ranges:')
        print('   ', ranges)
        print('Ranges with error:')
        print('   ', ranges_with_error)
        print('Estimator')
        print(estimator)
        print('Full result')
        print(result)

if __name__ == "__main__":
    MLAT.demo()
