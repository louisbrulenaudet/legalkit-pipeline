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
import random
import re
import uuid

from dotenv import load_dotenv
from datetime import date, datetime

from data.api.piste import PisteAPI, Code, Article

from tqdm import tqdm
from datasets import Dataset
from huggingface_hub import HfApi
from jinja2 import Environment, FileSystemLoader

from preprocessing.converter import JSONConverter, DateConverter

load_dotenv()


class ArticleWorkflow:
    def __init__(
        self
    ) -> None:
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


    def get_api_client(
        self
    ) -> any:
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

        return PisteAPI(
            client_id=client_id, 
            client_secret=secret_key
        )


    def fetch(
        self, 
        data:dict, 
        url:str
    ) -> dict:
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
        return self.fetcher.post(
            url=url, 
            data=data
        )

    
    def process(
        self, 
        element:dict
    ) -> list:
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
                url="https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle"
            )["article"]

            article = Article(response)
            article.extract()

            return article

        except Exception as e:
            print(f"Error fetching article: {e}")


    def create_dataset(
        self, 
        code:dict, 
        base:str, 
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
                url="https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/legi/tableMatieres"
            )
        ]

        toc = Code(
            code=content
        )
        
        toc.extract(
            data=content
        )

        list_of_dicts = []
        instructions_file_path ="./experiments/config/instructions.static.txt"

        try:
            with open(instructions_file_path, "r", encoding="utf-8") as file:
                instructions = [line.strip() for line in file if line.strip()]
        
        except FileNotFoundError:
            print(f"File '{instructions_file_path}' not found.")
            instructions = []

        for element in tqdm(toc.data, desc="Fetching articles"):
            try:
                article = self.process(
                    element=element
                )

                instruction = random.choice(instructions)

                item = {
                    "instruction" : instruction,
                    "input" : f"{base.capitalize()}, art. {article.data[0]['num']}",
                    "output" : article.data[0]["text"],
                    "start" : str(
                        DateConverter.unix_to_bson(
                            timestamp=article.data[0]["date"]
                            )
                        ),
                    "expiration" : str(
                        DateConverter.unix_to_bson(
                            timestamp=article.data[0]["expiration"]
                            )
                        ),
                    "num" : article.data[0]["num"],
                }

                list_of_dicts.append(item)

            except Exception as e:
                print(f"Error processing Article workflow: {e}")

        dataset = Dataset.from_list(list_of_dicts)

        return dataset


class DatasetWorkflow:
    def __init__(
        self,
        dataset:Dataset,
        instance:str,
        metadata:dict
    ):
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


    def generate_readme(
        self,
        template_path: str
    ) -> None:
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
            env = Environment(
                loader=FileSystemLoader(".")
            )

            template = env.get_template(template_path)
            rendered = template.render(**self.metadata)

            unique_id = uuid.uuid4().hex
            self.readme_filename = f"README_{unique_id}.md"
            self.readme_filepath = os.path.join("./experiments/config/readme", self.readme_filename)

            with open(self.readme_filepath, "w") as readme_file:
                readme_file.write(rendered)

        except Exception as e:
            print(f"Error generating README.md : {e}")

        return None


    def remove_readme(
        self
    ) -> None:
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
        api = HfApi(
            token=os.getenv("HUGGINGFACE_ACCESS_TOKEN")
        )

        try:
            if len(self.dataset) > 0:
                self.dataset.push_to_hub(
                    self.instance,
                    token=os.getenv("HUGGINGFACE_ACCESS_TOKEN")
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