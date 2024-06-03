import pandas as pd
import requests
import unicodedata
from unidecode import unidecode
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


class DataGovAPI:
    """
    A class to interact with a Colombia goverment data endpoint and load the data into a pandas DataFrame.
    """

    def __init__(self):
        """
        Initializes the DataGovAPI instance with the provided endpoint URL.
        
        Parameters:
        endpoint (str): The URL of the data endpoint.
        """
        self.dataframe = None
        return


    def load_data(self, endpoint):
        """
        Loads data from the endpoint URL into a pandas DataFrame.
        
        This method sends a GET request to the endpoint URL, checks for a successful response,
        and converts the JSON content of the response into a pandas DataFrame. If an error occurs,
        it catches the exception and prints an error message.
        """
        try:
            response = requests.get(endpoint)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Convert downloaded content to a pandas DataFrame
            self.dataframe = pd.read_json(response.text)
            print('Data loaded successfully.')
        except Exception as e:
            print('Error loading data: ', e)
        return


    def get_dataframe(self):
        """
        Returns the loaded pandas DataFrame.
        
        Returns:
        pandas.DataFrame: The DataFrame containing the loaded data.
        """
        return self.dataframe



class DataManager:
    """
    A class to manage a pandas DataFrame, including saving it to a CSV file.
    """
    def __init__(self):
        self.dataframe = None
        self.geolocator = Nominatim(user_agent="geoapiExercises_2")
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)


    def get_dataframe(self):
        """
        Returns the managed pandas DataFrame.
        
        Returns:
        pandas.DataFrame: The DataFrame being managed.
        """
        return self.dataframe
    

    def fix_string_case(self, dataframe):
        """
        This function corrects the case (lowercase and capitalize) of all values in all columns of a DataFrame and removes accents.

        Parameters:
        dataframe (DataFrame): The DataFrame to be corrected.

        Returns:
        DataFrame: The corrected DataFrame.
        """
        def remove_accents(text):
            """
            Remove accents from a given string using the unidecode library.
            
            Parameters:
            text (str): The string to be processed.
            
            Returns:
            str: The processed string without accents.
            """
            if isinstance(text, str):
                return unidecode(text)
            else:
                return text
        
        # Iterate over each column in the DataFrame
        for column in dataframe.columns:
            # Check if the column contains string values
            if dataframe[column].dtype == 'object':
                # Remove accents from all string values in the column
                dataframe[column] = dataframe[column].apply(remove_accents)
                # Convert all string values to lowercase
                dataframe[column] = dataframe[column].str.lower()
                # Capitalize the first letter of each string value in the column
                dataframe[column] = dataframe[column].str.capitalize()
        
        return dataframe
    
    def geocode_dataframe(self, dataframe=None):
        """
        Adds geolocation data to the DataFrame based on 'municipio' and 'departamento' columns.
        
        This method creates a new column 'geolocalizacion' and populates it with location names.
        It then uses the geopy library to obtain the geographical coordinates of each unique location.
        
        Parameters:
        dataframe (pandas.DataFrame, optional): The DataFrame to add geolocation data to. If not provided,
                                                the method uses the DataFrame managed by the instance.
        
        Returns:
        pandas.DataFrame: The DataFrame with added geolocation data.
        """
        if dataframe is None:
            dataframe = self.dataframe

       
        if 'municipio' in dataframe.columns and 'departamento' in dataframe.columns:
            # Create a new column for geolocation strings
            dataframe['geolocalizacion'] = dataframe['municipio'] + ", " + dataframe['departamento'] + ", Colombia"
            
            # Get unique locations
            location_list = list(dataframe['geolocalizacion'].unique())

            # List to store coordinates
            out_coordinates = []

            # Geocode each location
            for location in location_list:
                geocode_result = self.geocode(location)
                out_coordinates.append(geocode_result)
            
            # Create a list of dictionaries to store location and coordinates
            location_data = []
            for i_pos, i_coordinate in enumerate(out_coordinates):
                dict_value = {}
                dict_value["location"] = location_list[i_pos]
                dict_value["latitude"] = i_coordinate.latitude if i_coordinate else None
                dict_value["longitude"] = i_coordinate.longitude if i_coordinate else None
                location_data.append(dict_value)

            # Convert list of dictionaries to DataFrame
            location_df = pd.DataFrame(location_data)

            # Merge coordinates back to the original DataFrame
            dataframe = dataframe.merge(location_df, left_on='geolocalizacion', right_on='location', how='left')
            
            if dataframe is self.dataframe:
                self.dataframe = dataframe  # Update the managed DataFrame if the input was the managed DataFrame

            return dataframe
        
        else:
            print('DataFrame does not contain required columns: municipio and departamento')

            return dataframe

    def save_to_csv(self, dataframe, filename):
        """
        Saves the managed DataFrame to a CSV file.
        
        This method attempts to save the DataFrame to a CSV file with the given filename.
        If an error occurs, it catches the exception and prints an error message.
        
        Parameters:
        filename (str): The name of the file to save the DataFrame to.
        """
        try:
            dataframe.to_csv(filename, index=False)
            print(f"Data saved to {filename} successfully.")
        except Exception as e:
            print('Error saving data:', e)
        return


