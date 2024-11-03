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


def read_json_file(file_path: str):
    """
    Read JSON data from a file.

    Parameters
    ----------
    file_path : str
        The path to the JSON file to be read.

    Returns
    -------
    dict
        A dictionary containing the JSON data read from the file.

    Raises
    ------
    FileNotFoundError
        If the specified file cannot be found.

    json.JSONDecodeError
        If the JSON data in the file is invalid or cannot be decoded.

    Examples
    --------
    >>> data = read_json_file("example.json")
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        return data

    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")

    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON format in '{file_path}'.")
