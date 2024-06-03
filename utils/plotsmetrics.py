import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import geopandas as gpd

class PlotsMetrics:
    """
    A class to generate various plots for visualizing metrics and distributions of a dataset.
    """

    def __init__(self, data):
        """
        Initializes the PlotsMetrics instance with the provided dataset.

        Parameters:
        data (pandas.DataFrame): The dataset to be visualized.
        """
        self.data = data

    def visualize_missing_values(self):
        """
        Visualizes the percentage of missing values for each column in the dataset.

        Returns:
        plotly.graph_objs._figure.Figure: A bar plot showing the percentage of missing values per column.
        """
        missing_percentage = (self.data.isnull().mean() * 100).sort_values(ascending=False)
        fig = px.bar(x=missing_percentage.index, y=missing_percentage.values,
                     labels={'x': 'Columns', 'y': 'Missing Values Percentage'},
                     title='Percentage of Missing Values per Column', color_discrete_sequence=['#EF553B'])
        return fig

    def visualize_zero_values(self):
        """
        Visualizes the percentage of zero values for each column in the dataset.

        Returns:
        plotly.graph_objs._figure.Figure: A bar plot showing the percentage of zero values per column.
        """
        zero_percentage = (self.data == 0).mean() * 100
        fig = px.bar(x=zero_percentage.index, y=zero_percentage.values,
                     labels={'x': 'Columns', 'y': 'Zero Values Percentage'},
                     title='Percentage of Zero Values per Column', color_discrete_sequence=['#00CC96'])
        return fig

    def visualize_unique_values(self):
        """
        Visualizes the number of unique values for each column in the dataset.

        Returns:
        plotly.graph_objs._figure.Figure: A bar plot showing the number of unique values per column.
        """
        unique_counts = self.data.nunique().sort_values(ascending=False)
        fig = px.bar(x=unique_counts.index, y=unique_counts.values,
                     labels={'x': 'Columns', 'y': 'Unique Values Count'},
                     title='Number of Unique Values per Column', color_discrete_sequence=['#AB63FA'])
        return fig

    def visualize_distribution(self, columns):
        """
        Visualizes the distribution of a specified column in the dataset.

        """
               
        figures = []
        for column in columns:
            # Calculate the average production from 'producc_n_t' column
            avg_production = self.data.groupby(column).agg({'producci_n_t':'mean'}).reset_index()
            avg_production = avg_production.sort_values(by='producci_n_t', ascending=False).head(10)  # Sort by production
            
            # Create the histogram for each column
            fig = px.bar(avg_production, x=column, y='producci_n_t', title=f'Distribution of mean production for {column}', color_discrete_sequence=['#636EFA'])
            fig.update_yaxes(title_text='Producción promedio')
            figures.append(fig)
        
        return figures
    

    def plot_histogram(self,column,range_min=None,range_max=None,bins=10):
        """
        Generates a histogram for the specified column in the data.
        If no range is specified, the entire range of the data is used.
        """
        
        # Filter the data based on the specified range
        if range_min is not None and range_max is not None:
            filtered_data = self.data[(self.data[column] >= range_min) & (self.data[column] <= range_max)][column]
        else:
            filtered_data = self.data[column]

        fig = go.Figure(data=[go.Histogram(x=filtered_data, nbinsx=bins)])
        fig.update_layout(
        title='Histograma de ' + column,
        xaxis=dict(title='Valores'),
        yaxis=dict(title='Frecuencia')
    )
        fig.show()



    def visualize_box_plot(self,columns):
        """
        Visualizes the box plot for all numeric columns in the dataset.

        Returns:
        plotly.graph_objs._figure.Figure: A box plot showing the distribution of numeric columns.
        """
        
        if columns is None:
            columns = self.data.select_dtypes(include='number').columns.tolist()
        else:
            # Ensure the specified columns exist in the dataframe
            for col in columns:
                if col not in self.data.columns:
                    raise ValueError(f"Column '{col}' not found in the dataset")
        
        figures = []
        for column in columns:
            # Create the histogram for each column
            fig = px.box(self.data, y=column, title=f'Distribution of {column}',color_discrete_sequence=['#FFA15A'])
            figures.append(fig)
        
        return figures

    def visualize_correlation(self):
        """
        Visualizes the correlation matrix for numeric columns in the dataset.

        Returns:
        plotly.graph_objs._figure.Figure: A heatmap showing the correlation matrix of numeric columns.
        """
        numeric_columns = self.data.select_dtypes(include='number').columns
        corr_matrix = self.data[numeric_columns].corr()
        
        fig = go.Figure(data=go.Heatmap(z=corr_matrix.values, x=corr_matrix.index, y=corr_matrix.columns, colorscale='Viridis'))
        fig.update_layout(title='Correlation Matrix')
        return fig

    
    def categ_var_plots(self, categ_var):
        """
        Generates and displays combined bar and line plots for categorical variables showing count and mean of 'producci_n_t'.

        Parameters:
        categ_var (list): A list of categorical column names to generate the plots for.
        """
        
        for i_col in categ_var:
            fig = make_subplots(specs=[[{'secondary_y': True}]])
            data_grouped = self.data.groupby(by=i_col).agg({i_col: ['count'], 'producci_n_t': ['mean']}).reset_index()
            data_grouped.columns = [col[0] if col[1] == '' else col[1] for col in data_grouped.columns]
            data_grouped = data_grouped.rename(columns={('producci_n_t', 'mean'): 'mean_producci_n_t'}).sort_values(by=('mean_producci_n_t', ''), ascending=True).head(10)
            fig.add_trace(go.Bar(x=data_grouped[(i_col, i_col)], y=data_grouped[(i_col, 'count')], name='Count'), secondary_y=False)
            fig.add_trace(go.Scatter(x=data_grouped[(i_col, i_col)], y=data_grouped[('producci_n_t', 'mean')],
                                     mode='lines', name='Mean producci_n_t'), secondary_y=True)
            fig.update_layout(title=f'Count of {i_col} and Mean producci_n_t',
                              xaxis=dict(title=i_col),
                              yaxis=dict(title=f'Count {i_col}', side='left'),
                              yaxis2=dict(title='Mean producci_n_t', overlaying='y', side='right'))
            fig.show()

    def generate_grouped_plots(self):
        """
        Generates grouped plots for count of crops and average production per crop,
        grouped by year and department, sorted by average production in descending order.
        """
        grouped_data = self.data.groupby(['año',  'grupo_de_cultivo']).agg(count=('grupo_de_cultivo', 'count'), avg_production=('producci_n_t', 'mean')).reset_index()
        grouped_data.columns = ['año',  'grupo_de_cultivo', 'count_grupo_de_cultivo','avg_production']
        
        # Sort the data by average production in descending order
        grouped_data = grouped_data.sort_values(by='avg_production', ascending=False)
        
        # Create subplots with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Unique groups of cultivo
        unique_groups = grouped_data['grupo_de_cultivo'].unique()
        
        # Assigning colors to unique groups of cultivo
        colors = px.colors.qualitative.Plotly[:len(unique_groups)]

        # Iterate over each group of cultivo
        for group, color in zip(unique_groups, colors):
            group_data = grouped_data[grouped_data['grupo_de_cultivo'] == group]

            # Add bars for count of cultivo (primary y-axis)
            fig.add_trace(
                go.Bar(
                    x=group_data['año'],
                    y=group_data['count_grupo_de_cultivo'],
                    name=f'{group}',
                    marker_color=color
                ),
                secondary_y=False,
            )

        # Add a single line for average production (secondary y-axis)
        
            fig.add_trace(
                go.Scatter(
                    x=group_data['año'],
                    y=group_data['avg_production'],
                    name=f'{group} - Average Production',
                    mode='markers',  # Set mode to 'markers' to show only points
                    marker=dict(color='black', size=8)
                ),
                secondary_y=True,
            )

        # Configure layout of the figure
        fig.update_layout(
            title_text='Count of group_cultivo and Average Production Grouped by Year and Department',
            xaxis_title='Year',  # x-axis title
            yaxis_title='Count of group_cultivo',  # Primary y-axis title
            yaxis2_title='Average Production',  # Secondary y-axis title
            legend=dict(
            orientation="h",  # horizontal orientation for color legend
            yanchor="bottom",
            y=-1.99,
            xanchor="center",
            x=0.5
        )
        )
        return fig