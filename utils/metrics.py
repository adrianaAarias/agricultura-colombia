import pandas as pd
from IPython.display import display, HTML


class MetricsComputation:
    """
    A class to perform various metrics computations on a dataset loaded from a CSV file.
    """

    def __init__(self, file_path):
        """
        Initializes the MetricsComputation instance by loading the data from a CSV file.

        Parameters:
        file_path (str): The file path of the CSV file to be loaded.
        """
        self.data = pd.read_csv(file_path)
        self.data.reset_index(drop=True, inplace=True) 
        return

    def update_dataframe(self, df):
        self.data = df
        return


    def display_head(self, n=5):
        """
        Displays the first n records of the dataset.

        Parameters:
        n (int): The number of records to display. Default is 5.
        """
        print(f'First {n} records:')
        display(self.data.head(n))
        print('\n')
        return


    def display_info(self):
        """
        Displays the information of the dataset, including the index dtype and column dtypes, non-null values, and memory usage.
        """
        print('Dataset information:')
        display(self.data.info())
        print('\n')
        return


    def describe_numeric(self):
        """
        Displays descriptive statistics of numeric variables in the dataset.
        """
        numeric_columns = self.data.select_dtypes(include='number').columns
        print('Descriptive statistics of numeric variables:')
        display(self.data[numeric_columns].describe())
        print('\n')
        return


    def duplicate_rows(self):
        """
        Displays the duplicated rows in the dataset.
        """
        duplicate_rows = self.data[self.data.duplicated()]
        print('Total of duplicated rows:')
        display(duplicate_rows)
        print('\n')
        return


    def missing_values(self):
        """
        Displays the percentage of missing values per column in the dataset.
        """
        print('Percentage missing values per column (%):')
        display(((self.data.isnull().mean() * 100).round(2)).astype(str) + '%')
        print('\n')
        return


    def zero_values(self):
        """
        Displays the percentage of zero values per column in the dataset.
        """
        print('Percentage zero values per column (%):')
        zero_percentage = (self.data == 0).mean() * 100
        display(((zero_percentage).round(2)).astype(str) + '%')
        print('\n')
        return


    def unique_values(self):
        """
        Displays the count of unique values per column in the dataset.
        """
        unique_counts = {}
        for column in self.data.columns:
            unique_counts[column] = self.data[column].nunique()
        print('Unique values per column:')
        display(unique_counts)
        return
    

    def grouped_table(self,group_by_columns,aggregation_columns, sort_by_column,top_n=10):
        """
        Generates grouped table based on user-defined columns to group by, aggregation functions,
        and column to sort by. Returns the top n records based on the sorted column.
        """
        # Grouping the data based on user-defined columns 
        grouped_data = self.data.groupby(group_by_columns).agg(**aggregation_columns).reset_index()
        
        # Get the names of the aggregation columns from the dictionary
        aggregation_column_names = [key for key in aggregation_columns.keys()]

        # Rename the columns of the grouped DataFrame
        grouped_data.columns = group_by_columns + aggregation_column_names
        
        # Sorting the data based on the specified column
        grouped_data = grouped_data.sort_values(by=sort_by_column, ascending=False).reset_index().drop(columns=['index'])
        
        # Returning only the top n records
        top_records = grouped_data.head(top_n)
        
        return top_records
    
   

    
