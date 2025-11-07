
import numpy as np
from scipy.interpolate import Rbf
from scipy.spatial import cKDTree
import plotly.graph_objects as go
from ivMatrix import IvMatrix as IVM

class IvSurface:
    def __init__(self,ticker,api_key,side):
        self.api_key = api_key
        self.ticker = ticker
        self.matrix = IVM(ticker,api_key,side).get_IV_matrix()
        self.surface = self.rbf_surface(self.matrix)


    def rbf_surface(self, matrix, *, kernel="multiquadric", epsilon=None, smooth=1e-3):
        xs, ys, zs = [], [], []
        for x, row in matrix.items():
            for y, z in row.items():
                xs.append(float(x)); ys.append(float(y)); zs.append(float(z))
        xs = np.array(xs); ys = np.array(ys); zs = np.array(zs)

        if epsilon is None and len(xs) > 6:
            from scipy.spatial import cKDTree
            X = np.column_stack([xs, ys])
            dists, _ = cKDTree(X).query(X, k=min(6, len(xs)))
            idx = min(dists.shape[1]-1, 5)
            eps = np.median(dists[:, idx])
            epsilon = float(eps if np.isfinite(eps) and eps > 0 else 1.0)
        elif epsilon is None:
            epsilon = 1.0

        rbf = Rbf(xs, ys, zs, function=kernel, epsilon=epsilon, smooth=smooth)

        def f(x, y):
            return rbf(x, y)
        return f

    def get_plot(self):
        xs = sorted(self.matrix.keys())
        ys = sorted({y for x in self.matrix for y in self.matrix[x].keys()})

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        X, Y = np.meshgrid(
            np.linspace(x_min, x_max, 100),
            np.linspace(y_min, y_max, 100)
        )

        Z = self.surface(X, Y)

        fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
        fig.update_layout(
            title='Smoothed RBF Surface',
            scene=dict(
                xaxis_title='days to expiry',
                yaxis_title='strike',
                zaxis_title='implied vol'
            ),
        )
        return fig
