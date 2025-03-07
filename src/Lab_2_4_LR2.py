import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

# import seaborn as sns


class LinearRegressor:
    """
    Extended Linear Regression model with support for categorical variables and gradient descent fitting.
    """

    def __init__(self):
        self.coefficients = None
        self.intercept = None

    """
    This next "fit" function is a general function that either calls the *fit_multiple* code that
    you wrote last week, or calls a new method, called *fit_gradient_descent*, not implemented (yet)
    """

    def fit(self, X, y, method="least_squares", learning_rate=0.01, iterations=1000):
        """
        Fit the model using either normal equation or gradient descent.

        Args:
            X (np.ndarray): Independent variable data (2D array).
            y (np.ndarray): Dependent variable data (1D array).
            method (str): method to train linear regression coefficients.
                          It may be "least_squares" or "gradient_descent".
            learning_rate (float): Learning rate for gradient descent.
            iterations (int): Number of iterations for gradient descent.

        Returns:
            None: Modifies the model's coefficients and intercept in-place.
        """
        if method not in ["least_squares", "gradient_descent"]:
            raise ValueError(
                f"Method {method} not available for training linear regression."
            )
        if np.ndim(X) == 1:
            X = X.reshape(-1, 1)

        X_with_bias = np.insert(
            X, 0, 1, axis=1
        )  # Adding a column of ones for intercept

        if method == "least_squares":
            self.fit_multiple(X_with_bias, y)
        elif method == "gradient_descent":
            mse_list, coefficients, intercepts = self.fit_gradient_descent(
                X_with_bias, y, learning_rate, iterations
            )
            return mse_list, coefficients, intercepts

    def fit_multiple(self, X, y):
        """
        Fit the model using multiple linear regression (more than one independent variable).

        This method applies the matrix approach to calculate the coefficients for
        multiple linear regression.

        Args:
            X (np.ndarray): Independent variable data (2D array), with bias.
            y (np.ndarray): Dependent variable data (1D array).

        Returns:
            None: Modifies the model's coefficients and intercept in-place.
        """
        X_t = np.transpose(X)

        w1 = np.linalg.inv(np.dot(X_t, X))
        w2 = np.dot(w1, X_t)
        w = np.dot(w2, y)

        # Store the coefficients
        self.intercept = w[0]
        self.coefficients = w[1:]

    def fit_gradient_descent(self, X, y, learning_rate=0.01, iterations=1000):
        """
        Fit the model using either normal equation or gradient descent.

        Args:
            X (np.ndarray): Independent variable data (2D array), with bias.
            y (np.ndarray): Dependent variable data (1D array).
            learning_rate (float): Learning rate for gradient descent.
            iterations (int): Number of iterations for gradient descent.

        Returns:
            None: Modifies the model's coefficients and intercept in-place.
        """

        # Initialize the parameters to very small values (close to 0)
        m = len(y)
        self.coefficients = (
            np.random.rand(X.shape[1] - 1) * 0.01
        )  # Small random numbers
        self.intercept = np.random.rand() * 0.01

        mse_list = []
        coefficients = []
        intercepts = []

        for epoch in range(iterations):
            predictions = self.predict(X[:, 1:])
            error = predictions - y

            gradient = 1 / m * np.dot(error, X)
            self.intercept -= learning_rate * gradient[0]
            self.coefficients -= learning_rate * gradient[1:]

            if epoch % (iterations // 10) == 0:
                mse = np.mean((error) ** 2)
                print(f"Epoch {epoch}: MSE = {mse}")

            if epoch % (iterations // 100) == 0 and iterations > 1000:
                mse_list.append(1 / m * np.sum((error) ** 2))
                coefficients.append(self.coefficients.copy())
                intercepts.append(self.intercept)
            else:
                mse_list.append(1 / m * np.sum((error) ** 2))
                coefficients.append(self.coefficients.copy())
                intercepts.append(self.intercept)

        return mse_list, coefficients, intercepts

    def predict(self, X):
        """
        Predict the dependent variable values using the fitted model.

        Args:
            X (np.ndarray): Independent variable data (1D or 2D array).
            fit (bool): Flag to indicate if fit was done.

        Returns:
            np.ndarray: Predicted values of the dependent variable.

        Raises:
            ValueError: If the model is not yet fitted.
        """

        if self.coefficients is None or self.intercept is None:
            raise ValueError("Model is not yet fitted")

        if np.ndim(X) == 1:
            predictions = self.coefficients * X + self.intercept
        else:
            predictions = np.dot(X, self.coefficients) + self.intercept
        return predictions


def evaluate_regression(y_true, y_pred):
    """
    Evaluates the performance of a regression model by calculating R^2, RMSE, and MAE.

    Args:
        y_true (np.ndarray): True values of the dependent variable.
        y_pred (np.ndarray): Predicted values by the regression model.

    Returns:
        dict: A dictionary containing the R^2, RMSE, and MAE values.
    """

    # R^2 Score
    rss = np.sum((y_true - y_pred) ** 2)
    y_mean = np.mean(y_true)
    tss = np.sum((y_true - y_mean) ** 2)
    r_squared = 1 - (rss / tss)

    N = y_true.shape[0]

    # Root Mean Squared Error
    mse = np.sum((y_true - y_pred) ** 2)
    rmse = np.sqrt(1 / N * mse)

    # Mean Absolute Error
    mae_sum = np.sum(abs(y_true - y_pred))
    mae = 1 / N * mae_sum

    return {"R2": r_squared, "RMSE": rmse, "MAE": mae}


def one_hot_encode(X, categorical_indices, drop_first=False):
    """
    One-hot encode the categorical columns specified in categorical_indices. This function
    shall support string variables.

    Args:
        X (np.ndarray): 2D data array.
        categorical_indices (list of int): Indices of columns to be one-hot encoded.
        drop_first (bool): Whether to drop the first level of one-hot encoding to avoid multicollinearity.

    Returns:
        np.ndarray: Transformed array with one-hot encoded columns.
    """
    X_transformed = X.copy()

    for index in sorted(categorical_indices, reverse=True):
        X_transformed = np.delete(X_transformed, index, 1)

    for index in sorted(categorical_indices, reverse=True):
        # Extract the categorical column
        categorical_column = X[:, index]

        # Find the unique categories (works with strings)
        unique_values = np.unique(categorical_column)

        # Create a one-hot encoded matrix (np.array) for the current categorical column
        values = [
            [1 if categorical_column[i] == value else 0 for value in unique_values]
            for i in range(len(categorical_column))
        ]
        one_hot = np.array(values)

        # ===== Other code I used =====
        # for i in range(categorical_column.shape[0]):
        #     row = []
        #     for value in unique_values:
        #         if categorical_column[i] == value:
        #             row.append(1)
        #         else:
        #             row.append(0)
        #     values.append(row)

        # Optionally drop the first level of one-hot encoding
        if drop_first:
            one_hot = one_hot[:, 1:]

        # Insert new one-hot encoded columns
        X_transformed = np.concatenate((one_hot, X_transformed), axis=1)

    return X_transformed
