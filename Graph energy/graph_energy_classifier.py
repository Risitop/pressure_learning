import math
from numpy import array, concatenate

class GraphEnergyClassifier:
    """ Classifies a sample set by minimizing graph global energy. """

    def __init__(self, similarity='rbf', loss='sqloss', eps=1e-3, l1=1, l2=1):
        """
        similarity : Function X.X -> R+ describing similarity between points
        loss : Punishment function X.X -> R+ for relabeling labeled points
        eps : Used to determine convergence of GD
        l1 : Punishment coef for predictor when outputting too high values
        l2 : Punishment coef for predictor when energy is high
        """

        # Weights between vertices, dict of (i, j)
        self.weights = {}

        # Convex loss function parameters
        self.similarity, self.loss, self.eps, self.l1, self.l2 = (
            lambda x_1, x_2: math.exp(-linalg.norm(x_1 - x_2)**2/0.01) if similarity == 'rbf' else similarity,
            (lambda i, j: (i - j)**2) if loss == 'sqloss' else loss,
            eps, l1, l2
        )

        # Learning values
        self.X_fit, self.y_fit = None, None
        self.predictions = None

        # Amount of labeled/unlabeled data
        self.l, self.u = 0, 0
        self.selector_l = None

    def __len__(self):
        """ __len(self)__ -> number of samples """
        assert self.l + self.u > 0, "Model must be fit."

        return self.l + self.u

    def _weight_(self, i, j):
        """ _weight_(int, int) -> float """
        assert self.X_fit is not None and self.y_fit is not None, "Model must be fit."

        i, j = min(i, j), max(i, j)
        if (i, j) not in self.weights:
            self.weights[(i, j)] = self.similarity( self.X_fit[i], self.X_fit[j] )
        return self.weights[(i, j)]

    def _label_(self, i):
        """ _label_(i) -> {-1, 0, 1} """
        assert self.y_fit is not None, "Model must be fit."
        assert i < len(self.y_fit), "Index out of range : " + str(i)

        return self.y_fit[i]

    def _energy_(self, f):
        """ _energy_(self, f) -> energy necessary to affectation f """
        return (
            1 / self.l * sum( (f[i] - self.y_fit[i])**2 for i in range(self.l) ) +
            self.l1 * linalg.norm(f)**2 +
            self.l2 * sum(
                (f[i] - f[j])**2 * self._weight_(i, j)
                for j in range(len(self)) for i in range(len(self))
            )
        )

    def _gradient_(self, f):
        """ _gradient_(self, f) -> partial derivatives of energy at point f """

        def subgradient(i):
            return 2 * (
                (1 / self.l * (f[i] - self.y_fit[i]) if i < self.l else 0) +
                self.l1 * f[i] +
                2 * self.l2 * (
                    sum( (f[i] - f[j])*self._weight_(i, j) for j in range(len(self)) )
                )
            )

        return array([
            subgradient(i) for i in range(len(self))
        ])

    def fit(self, X, y, learning_rate=1e-2, max_iter=30, starting_point=None, log=False):
        """
            IMPORTANT : LABELED DATA MUST BE BEFORE UNLABELED DATA
            X : design matrix
            y : label vector, 0 for unlabeled and -1/+1 for known classes
            learning_rate : Gradient descent parameter
            max_iter : Safety counter for gradient descent
            starting_point : Starting GD point, initialized as y by default
            log : Toogles console outputs
            ======================================
            returns : a label vector with an affectation for each sample
        """
        assert len(X) == len(y), "Design matrix and class vector must have same length."

        # Data loading, putting unlabeled at the end
        labeled_selector = y != 0
        self.X_fit = array(X, copy=True)
        self.y_fit = array(y, copy=True)

        # Labeled and unlabeled data size
        self.l, self.u = sum(labeled_selector), len(labeled_selector) - sum(labeled_selector)
        self.selector_l = diag(array([i < self.l for i in range(self.l + self.u)]))

        if log:
            print('#'*20)
            print('Beginning of fitting.')

        # Gradient descent parameters

        # y : initial value of y
        y = array(self.y_fit, copy=True).astype(float) if starting_point is None else starting_point

        # From https://github.com/GRYE/Nesterov-accelerated-gradient-descent/blob/master/nesterov_method.py

        lambda_prev, lambda_curr, gamma, y_prev = 0, 1, 1, y

        # Accelerated gradient descent loop
        for i in range(max_iter):

            gradient = self._gradient_(y)

            # Convergence condition
            if linalg.norm(gradient) < self.eps:
                break

            y_curr = y - learning_rate * gradient
            y = (1 - gamma) * y_curr + gamma * y_prev
            y_prev = y_curr

            lambda_tmp = lambda_curr
            lambda_curr = (1 + math.sqrt(1 + 4 * lambda_prev * lambda_prev)) / 2
            lambda_prev = lambda_tmp

            gamma = (1 - lambda_prev) / lambda_curr

            if log:
                print("Round :", i, "Magnitude :", linalg.norm(gradient), "Energy :", self._energy_(y))

        return y

    def leaveOneGroupOutValidation(self, X, y, groups, learning_rate=1e-2, max_iter=30, starting_point=None, log=False):
        """
            X : design matrix
            y : label vector, 0 for unlabeled and -1/+1 for known classes
            groups : group vector assigning each sample to a particular group
            learning_rate : Gradient descent parameter
            max_iter : Safety counter for gradient descent
            starting_point : Starting GD point, initialized as y by default
            log : Toogles console outputs
            ======================================
            Runs a leave one group out cross validation analysis
        """

        def make_selector(group_name):
            return (groups == group_name) *  (y != 0)

        errors, normalizer = 0, 0

        for group in set(groups):

            selector = make_selector(group)
            group_size = sum(selector)

            if group_size == 0:
                continue

            X_tmp, y_tmp = array(X, copy=True), array(y, copy=True)
            y_tmp[selector] = 0.

            X_in = concatenate( (X_tmp[y_tmp != 0], X_tmp[(y_tmp == 0) * (selector == False)], X_tmp[selector]) )
            y_in = concatenate( (y_tmp[y_tmp != 0], y_tmp[(y_tmp == 0) * (selector == False)], y_tmp[selector]) )

            print("#"*20)
            print("Beginning group", group, "of size", group_size)

            y_pred = self.fit(X_in, y_in, learning_rate, max_iter, starting_point, log=log)
            step_errors = sum(y[selector] != ((y_pred[-group_size:] >= 0) * 2 - 1))

            errors += step_errors
            normalizer += group_size

            print(step_errors, "error(s) at this step.")
            print("Truth :", y[selector])
            print("Prediction on left out group :", y_pred[-group_size:])
            print("Error on training set :", sum(y_in[:self.l] != ((y_pred[:self.l] >= 0) * 2 - 1)) / self.l)

        print("Global error :", errors/normalizer)
