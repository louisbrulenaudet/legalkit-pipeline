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
import concurrent.futures
import datetime

import dotenv
from tqdm import tqdm

from ._register import ArticleWorkflow, BofipWorkflow, DatasetWorkflow

from utils.documents import read_json_file

dotenv.load_dotenv()


def push_to_hub(dataset, template_path: str) -> None:
    """
    Pushes a dataset to the Hugging Face Hub.

    This function generates a README.md file for the dataset using a template, pushes the dataset to the Hugging Face Hub,
    and removes the generated README.md file.

    Parameters
    ----------
    dataset : datasets.Dataset
        The dataset to be pushed to the Hub.

    template_path : str
        The path to the Jinja template file for generating the README.md.

    Returns
    -------
    None
    """
    try:
        dataset.generate_readme(template_path=template)

        # Dataset pushing to the hub.
        dataset.push_to_hub()
        dataset.remove_readme()

    except Exception as exc:
        print(f"Error pushing dataset : {exc}")

        return None


def push_datasets_to_hub(datasets: list, template_path: str) -> None:
    """
    Pushes a list of datasets to the Hugging Face Hub.

    This function pushes multiple datasets to the Hugging Face Hub concurrently using ThreadPoolExecutor.
    It logs errors encountered during the process.

    Parameters
    ----------
    datasets : List[datasets.Dataset]
        The list of datasets to be pushed to the Hub.

    template_path : str
        The path to the Jinja template file for generating the README.md.

    Returns
    -------
    None
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_dataset = {
            executor.submit(push_to_hub, dataset, template_path): dataset
            for dataset in datasets
        }

        for future in tqdm(
            concurrent.futures.as_completed(future_to_dataset), total=len(datasets)
        ):
            name = future_to_dataset[future]

            try:
                future.result()

            except Exception as exc:
                print(f"Error processing datasets : {exc}")

    return None


if __name__ == "__main__":
    codes = read_json_file(file_path="./experiments/config/legitext.config.json")

    template = "../config/README.template.md"
    readme_filepath = "../config/README.md"

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    datasets = []

    for code in tqdm(codes):
        try:
            workflow = ArticleWorkflow()

            data = {
                "textId": code["textId"],
                "nature": code["nature"],
                "date": current_date,
            }

            dataset = workflow.create_dataset(
                code=data,
                base=code["base"],
            )

            metadata = {"date": current_date, "base": code["base"]}

            datasets.append(
                DatasetWorkflow(
                    dataset=dataset, instance=code["instance"], metadata=metadata
                )
            )

        except Exception as e:
            print(f"Error occurred: {str(e)}")

    try:
        push_datasets_to_hub(datasets=datasets, template_path=template)

    except Exception as e:
        print(f"Error occurred: {str(e)}")

    url: str = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/bofip-vigueur/exports/json"
    token: str = os.getenv("HF_TOKEN")
    dataset_name: str = "bofip"

    workflow = BofipWorkflow(url, token, dataset_name)
    workflow.fetch_and_convert()
    workflow.create_dataset()
    workflow.push_to_hub()
    workflow.cleanup()
