# -*- coding: utf-8 -*-
# Copyright (c) Louis Brulé Naudet. All Rights Reserved.
# This software may be used and distributed according to the terms of License Agreement.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import tempfile
import requests

import uuid

from dotenv import load_dotenv

from ._piste import PisteAPI, Code, Article

from tqdm import tqdm
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi, HfFolder
from jinja2 import Environment, FileSystemLoader

load_dotenv()


class ArticleWorkflow:
    def __init__(self) -> None:
        """
        Initializes a LegalDataExtractor instance.

        This constructor sets up the API client and database client for
        extracting and registering legal data.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.fetcher = self.get_api_client()

    def get_api_client(self) -> any:
        """
        Initializes and returns an API client for data retrieval.

        This method retrieves client ID and secret key from environment variables and creates an API client.

        Parameters
        ----------
        None

        Returns
        -------
        api_client : PisteAPI
            An API client for data retrieval.
        """
        client_id = os.getenv("PISTE_ID")
        secret_key = os.getenv("SECRET_KEY")

        return PisteAPI(client_id=client_id, client_secret=secret_key)

    def fetch(self, data: dict, url: str) -> dict:
        """
        Fetches legal data using the provided API client and data parameters.

        This method sends a POST request to the specified URL with the provided data.

        Parameters
        ----------
        data : dict
            The data parameters for the request.

        url : str
            The URL of the API endpoint.

        Returns
        -------
        data : dict
            The retrieved legal data.
        """
        return self.fetcher.post(url=url, data=data)

    def process(self, element: dict) -> list:
        """
        Processes a legal article.

        This method processes a specific legal article obtained from the API.

        Parameters
        ----------
        element : dict
            The legal article to be processed.

        Returns
        -------
        article : list
            The article data.
        """
        try:
            data = {
                "id": element["id"],
            }

            response = self.fetch(
                data=data,
                url="https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle",
            )["article"]

            article = Article(response)
            article.extract()

            return article

        except Exception as e:
            print(f"Error fetching article: {e}")

    def create_dataset(
        self,
        code: dict,
        base: str,
    ):
        """
        Extracts and registers legal articles from an external API source.

        This method retrieves legal data, processes it, and registers it in a database collection.

        Parameters
        ----------
        code : dict
            The code id and date for data retrieval.

        base : str
            The name of the legal base.

        Returns
        -------
        dataset : Dataset
            The Dataset containing articles to push.
        """
        content = [
            self.fetch(
                data=code,
                url="https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legi/tableMatieres",
            )
        ]

        toc = Code(code=content)

        toc.extract(data=content)

        list_of_dicts = []

        for element in tqdm(toc.data, desc="Fetching articles"):
            try:
                article = self.process(element=element)

                item = {
                    "ref": f"{base.capitalize()}, art. {article.data[0]['num']}",
                    "title_main": f"{base.capitalize()}",
                    "texte": article.data[0]["texte"],
                    "dateDebut": article.data[0]["dateDebut"],
                    "dateFin": article.data[0]["dateFin"],
                    "num": article.data[0]["num"],
                    "id": article.data[0]["id"],
                    "cid": article.data[0]["cid"],
                    "type": article.data[0]["type"],
                    "etat": article.data[0]["etat"],
                    "nota": article.data[0]["nota"],
                    "version_article": article.data[0]["versionArticle"],
                    "ordre": article.data[0]["ordre"],
                    "conditionDiffere": article.data[0]["conditionDiffere"],
                    "infosComplementaires": article.data[0]["infosComplementaires"],
                    "surtitre": article.data[0]["surtitre"],
                    "nature": article.data[0]["nature"],
                    "texteHtml": article.data[0]["texteHtml"],
                    "dateFinExtension": article.data[0]["dateFinExtension"],
                    "versionPrecedente": article.data[0]["versionPrecedente"],
                    "refInjection": article.data[0]["refInjection"],
                    "idTexte": article.data[0]["idTexte"],
                    "idTechInjection": article.data[0]["idTechInjection"],
                    "origine": article.data[0]["origine"],
                    "dateDebutExtension": article.data[0]["dateDebutExtension"],
                    "idEliAlias": article.data[0]["idEliAlias"],
                    "cidTexte": article.data[0]["cidTexte"],
                    "sectionParentId": article.data[0]["sectionParentId"],
                    "multipleVersions": article.data[0]["multipleVersions"],
                    "comporteLiensSP": article.data[0]["comporteLiensSP"],
                    "sectionParentTitre": article.data[0]["sectionParentTitre"],
                    "infosRestructurationBranche": article.data[0][
                        "infosRestructurationBranche"
                    ],
                    "idEli": article.data[0]["idEli"],
                    "sectionParentCid": article.data[0]["sectionParentCid"],
                    "numeroBo": article.data[0]["numeroBo"],
                    "infosRestructurationBrancheHtml": article.data[0][
                        "infosRestructurationBrancheHtml"
                    ],
                    "historique": article.data[0]["historique"],
                    "infosComplementairesHtml": article.data[0][
                        "infosComplementairesHtml"
                    ],
                    "renvoi": article.data[0]["renvoi"],
                    "fullSectionsTitre": article.data[0]["fullSectionsTitre"],
                    "notaHtml": article.data[0]["notaHtml"],
                    "inap": article.data[0]["inap"],
                }

                list_of_dicts.append(item)

            except Exception as e:
                print(f"Error processing Article workflow: {e}")

        dataset = Dataset.from_list(list_of_dicts)

        return dataset


class BofipWorkflow:
    """
    A class to fetch JSON data from a URL, convert it to a French-compatible format (UTF-8 encoding),
    store it in a Hugging Face dataset, and share it to the Hugging Face Hub.

    Parameters
    ----------
    url : str
        The URL of the JSON file to be fetched.

    token : str
        The authentication token for the Hugging Face Hub.

    dataset_name : str
        The name of the dataset to be shared on the Hugging Face Hub.

    Attributes
    ----------
    data : any
        The data fetched and converted from the JSON file.

    dataset : datasets.DatasetDict
        The Hugging Face Dataset object containing the processed data.

    temp_file : str
        Path to the temporary file used for storing the JSON data.

    Methods
    -------
    fetch_and_convert():
        Fetch the JSON data from the URL and convert it to UTF-8 encoding.

    create_dataset():
        Create a Hugging Face dataset from the converted JSON data.

    push_to_hub():
        Push the created dataset to the Hugging Face Hub.

    cleanup():
        Remove temporary files and clear dataset from memory.
    """

    def __init__(self, url: str, token: str, dataset_name: str):
        assert isinstance(url, str), "url must be a string"
        assert isinstance(token, str), "token must be a string"
        assert isinstance(dataset_name, str), "dataset_name must be a string"

        self.url = url
        self.token = token
        self.dataset_name = dataset_name
        self.data = None
        self.dataset = None
        self.temp_file = None

    def fetch_and_convert(self):
        """
        Fetch the JSON data from the specified URL and convert it to UTF-8 encoding.

        This method retrieves the JSON data from the URL, ensuring that it is properly encoded
        in UTF-8, which is compatible with the French language.

        Returns
        -------
        data : any
            The JSON data converted to UTF-8 encoding.
        """
        response = requests.get(self.url, stream=True)
        response.raise_for_status()  # Raise an error for bad HTTP responses

        assert (
            response.status_code == 200
        ), f"Failed to fetch data. HTTP Status Code: {response.status_code}"

        # Create a temporary file to store the large JSON content
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="w+", encoding="utf-8"
        ) as tmp_file:
            self.temp_file = tmp_file.name
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    tmp_file.write(chunk.decode("ascii"))

        # Read from the temporary file and convert the data
        with open(self.temp_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        assert self.data is not None, "Failed to load data from the URL."
        return self.data

    def create_dataset(self):
        """
        Create a Hugging Face Dataset from the converted JSON data.

        This method processes the converted JSON data and structures it into a Hugging Face
        Dataset, ready for further use and sharing.

        Returns
        -------
        dataset : datasets.DatasetDict
            The Hugging Face Dataset object containing the processed data.
        """
        assert (
            self.data is not None
        ), "No data available. Fetch and convert the JSON data first."
        assert isinstance(
            self.data, (list, dict)
        ), "Data must be a list or dictionary to create a dataset."

        # Transform the list of dictionaries into a dictionary of lists
        if isinstance(self.data, list):
            transformed_data = {
                key: [d[key] for d in self.data] for key in self.data[0]
            }

        else:  # If it's a dictionary, we assume it needs to be converted to a list of dicts
            transformed_data = {key: [self.data[key]] for key in self.data}

        self.dataset = DatasetDict({"train": Dataset.from_dict(transformed_data)})

        assert self.dataset is not None, "Failed to create a dataset from the data."
        return self.dataset

    def push_to_hub(self):
        """
        Push the created Hugging Face Dataset to the Hugging Face Hub.

        This method uploads the dataset to the Hugging Face Hub under the provided dataset name,
        using the provided authentication token.

        Returns
        -------
        None
        """
        assert self.dataset is not None, "No dataset created. Create the dataset first."
        assert (
            isinstance(self.dataset_name, str) and len(self.dataset_name) > 0
        ), "Dataset name must be a valid string."

        # Authenticate and push to the hub
        api = HfApi()
        assert api is not None, "Failed to initialize HfApi."

        HfFolder.save_token(self.token)
        self.dataset.push_to_hub(self.dataset_name, token=self.token)

        print(
            f"Dataset '{self.dataset_name}' has been successfully pushed to the Hugging Face Hub."
        )

    def cleanup(self):
        """
        Clean up temporary files and clear dataset from memory.

        This method deletes the temporary file used to store the JSON data and clears the dataset
        object from memory.

        Returns
        -------
        None
        """
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            print(f"Temporary file '{self.temp_file}' has been removed.")

        self.data = None
        self.dataset = None
        print("Dataset and data have been cleared from memory.")


class DatasetWorkflow:
    def __init__(self, dataset: Dataset, instance: str, metadata: dict):
        """
        Class for managing the workflow of dataset updates and uploads to Hugging Face Hub.

        Attributes
        ----------
        dataset : Dataset
            The Dataset containing articles to push.

        instance : str
            The identifier of the dataset.

        metadata : dict
            A dictionary containing data for generating the README.md.

        Methods
        -------
        update_readme(content, template_path, rendered_readme_path)
            Update the content of the README.md file using Jinja templates.

        push_to_hub(instance)
            Push the dataset to the Hugging Face Hub.

        process(instance, content, template_path)
            Process the dataset workflow.

        generate_readme(content, template_path)
            Generate the README.md file with a random UUID name and store it in the class variable.

        remove_readme()
            Remove the README.md file if it exists.
        """
        self.dataset = dataset
        self.instance = instance
        self.metadata = metadata
        self.readme_filename = None
        self.readme_filepath = None

    def generate_readme(self, template_path: str) -> None:
        """
        Update the content of the README.md file using Jinja templates and generate it with a random UUID name.

        Parameters
        ----------
        template_path : str
            The path to the Jinja template file.

        Returns
        -------
        None
        """
        try:
            env = Environment(loader=FileSystemLoader("."))

            template = env.get_template(template_path)
            rendered = template.render(**self.metadata)

            unique_id = uuid.uuid4().hex
            self.readme_filename = f"README_{unique_id}.md"
            self.readme_filepath = os.path.join(
                "./experiments/config/readme", self.readme_filename
            )

            with open(self.readme_filepath, "w") as readme_file:
                readme_file.write(rendered)

        except Exception as e:
            print(f"Error generating README.md : {e}")

        return None

    def remove_readme(self) -> None:
        """
        Remove the README.md file if it exists.

        Returns
        -------
        None
        """
        if self.readme_filepath:
            try:
                os.remove(self.readme_filepath)

            except Exception as e:
                print(f"Error removing README.md: {e}")

            finally:
                self.readme_filepath = None

        return None

    def push_to_hub(
        self,
    ) -> None:
        """
        Push the dataset to the Hugging Face Hub.

        Returns
        -------
        None
        """
        api = HfApi(token=os.getenv("HUGGINGFACE_ACCESS_TOKEN"))

        try:
            if len(self.dataset) > 0:
                self.dataset.push_to_hub(
                    self.instance, token=os.getenv("HUGGINGFACE_ACCESS_TOKEN")
                )

                api.upload_file(
                    path_or_fileobj=self.readme_filepath,
                    path_in_repo="README.md",
                    repo_type="dataset",
                    repo_id=self.instance,
                )

            else:
                print(f"Cannot push empty Dataset to the Hub")

        except Exception as e:
            print(f"Error pushing dataset to Hub: {e}")

        return None
