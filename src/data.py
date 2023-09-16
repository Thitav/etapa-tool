import numpy as np
import pandas as pd


class UserData:
    data: pd.DataFrame
    filtered_data: pd.DataFrame
    mean: float
    filtered_mean: float
    row_mean: pd.Series
    filtered_row_mean: pd.Series
    column_mean: pd.Series

    def __init__(self, user_data: pd.DataFrame) -> None:
        user_mean = user_data.to_numpy().flatten()
        user_mean = user_mean[~pd.isnull(user_mean)].mean()

        self.data = user_data
        self.filtered_data = user_data
        self.mean = user_mean
        self.filtered_mean = user_mean
        self.row_mean = user_data.mean(axis=1)
        self.filtered_row_mean = self.row_mean
        self.column_mean = user_data.mean()

    def filter(self, filter: list[str]) -> None:
        regex = f"({'|'.join(filter)})"
        filtered_data = self.data.loc[:, ~self.data.columns.str.match(regex)]

        filtered_mean = filtered_data.to_numpy().flatten()
        filtered_mean = filtered_mean[~pd.isnull(filtered_mean)].mean()

        self.filtered_data = filtered_data
        self.filtered_mean = filtered_mean
        self.filtered_row_mean = filtered_data.mean(axis=1)


class GlobalData:
    data: list[UserData]
    mean: float
    filtered_mean: float
    row_mean: pd.Series
    filtered_row_mean: pd.Series
    column_mean: pd.Series

    def __init__(self, global_data: list[UserData]) -> None:
        self.data = global_data
        self.mean = pd.Series([user.mean for user in global_data]).mean()
        self.filtered_mean = self.mean
        self.row_mean = pd.DataFrame([user.row_mean for user in global_data]).mean()
        self.filtered_row_mean = self.row_mean
        self.column_mean = pd.DataFrame(
            [user.column_mean for user in global_data]
        ).mean()

    def filter(self, filter: list[str]) -> None:
        for user in self.data:
            user.filter(filter)

        self.filtered_mean = pd.Series(
            [user.filtered_mean for user in self.data]
        ).mean()
        self.filtered_row_mean = pd.DataFrame(
            [user.filtered_row_mean for user in self.data]
        ).mean()

    def get_users_attr(self, attr: str) -> pd.Series:
        return pd.Series([getattr(user, attr) for user in self.data])

    def get_users_data(self, column: str, row: str) -> pd.Series:
        return pd.Series(
            [
                user.data[column][row]
                if column in user.data and row in user.data[column]
                else np.nan
                for user in self.data
            ]
        )
