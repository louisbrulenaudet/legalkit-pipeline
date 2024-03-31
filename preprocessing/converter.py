# -*- coding: utf-8 -*-
# Copyright (c) Louis Brulé Naudet. All Rights Reserved.
# This software may be used and distributed according to the terms of License Agreement.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import datetime

class JSONConverter:
    def __init__(
        self, 
        input_file_path: str, 
        output_file_path: str
    ):
        """
        Initialize a JSONConverter instance.

        Parameters
        ----------
        input_file_path : str
            The file path of the input JSON file with ASCII-encoded data.

        output_file_path : str
            The file path for the output JSON file with UTF-8 encoded data.

        data : any
            The data to be checked. It can be text, a list of dictionaries, or any valid JSON structure.
        """
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.data = None


    def open_input_file(
        self
    ):
        """
        Open and read the input JSON file.

        This method opens and reads the data from the input file.

        Returns
        -------
        data : any
            The data read from the input file.
        """
        with open(self.input_file_path, "r", encoding="ascii") as input_file:
            data = json.load(input_file)

        self.data = data

        return data


    def save_output_file(
        self
    ):
        """
        Save the data to the output JSON file with UTF-8 encoding.

        This method saves the provided data to the output file with UTF-8 encoding.

        Returns
        -------
        None
        """
        with open(self.output_file_path, "w", encoding="utf-8") as output_file:
            data = json.dumps(self.data, ensure_ascii=False, indent=2)
            output_file.write(data)


    def convert_ascii_to_utf8(
        self
    ):
        """
        Convert the input JSON data to UTF-8 encoding if it is ASCII encoded.

        This method checks if the input data is ASCII encoded before conversion. If the data is ASCII encoded,
        it converts the data to UTF-8 encoding and saves it to the output file.

        Returns
        -------
        None
        """
        self.open_input_file()

        if self.data:
            self.save_output_file()
        else:
            print("The data is not loaded and does not need conversion.")


class DateConverter:
    @staticmethod
    def unix_to_bson(
        timestamp:int
    ) -> str:
        """
        Converts a Unix timestamp in milliseconds to BSON format.

        Parameters
        ----------
        timestamp : int or float
            The Unix timestamp in milliseconds to be converted.

        Returns
        -------
        bson_date : str
            A string representing the input timestamp in ISO 8601 format with milliseconds and UTC timezone information.

        Example
        -------
        To convert a Unix timestamp to BSON format:
        >>> timestamp = 1577664000000
        >>> iso_converter = DateConverter()
        >>> bson_date = DateConverter.unix_to_bson(timestamp)
        '2023-11-01T01:48:02.567+00:00'
        """
        # Convert the Unix timestamp to seconds (divide by 1000)
        seconds = timestamp / 1000

        # Create a datetime object
        dt = datetime.datetime.utcfromtimestamp(seconds)

        bson_date = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond * 1000)

        return bson_date


    @staticmethod
    def ISO8601_to_bson(
        timestamp:str
    ) -> str:
        """
        Converts a ISO 8601 timestamp to BSON format.

        Parameters
        ----------
        timestamp : str
            The ISO 8601 timestamp to be converted.

        Returns
        -------
        bson_date : str
            A string representing the input timestamp in ISO 8601 format with milliseconds and UTC timezone information.

        Example
        -------
        To convert a ISO 8601 to bson format:
        >>> timestamp = 1577664000000
        >>> iso_converter = DateConverter()
        >>> bson_date = DateConverter.unix_to_bson(timestamp)
        '2023-11-01T01:48:02.567+00:00'
        """
        # Parse the date string into a Python datetime object
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%d")

        # Convert the datetime object to BSON date format
        bson_date = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond * 1000)

        return bson_date