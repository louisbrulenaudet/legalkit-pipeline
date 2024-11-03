# LegalKit Pipeline: Open Access to French Legal Codes on 🤗 Datasets

[![Python](https://img.shields.io/pypi/pyversions/tensorflow.svg)](https://badge.fury.io/py/tensorflow)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Maintainer](https://img.shields.io/badge/maintainer-@louisbrulenaudet-blue)

The LegalKit Pipeline project aims to provide open access to French legal codes on the 🤗 Datasets platform, thereby democratizing access to legal information and promoting transparency and understanding of the French legal system. Our mission is to compile and publish a comprehensive collection of French legal codes, spanning civil law, criminal law, and administrative regulations among other areas, to cater to the diverse needs of legal professionals, researchers, students, and enthusiasts alike.

With LegalKit Pipeline, individuals have the opportunity to explore, analyze, and leverage French legal texts for various purposes, empowering them to navigate and interpret the law with ease. By facilitating access to this valuable resource, we aim to foster greater transparency and knowledge accessibility in the legal domain, enabling stakeholders to make informed decisions and advance legal scholarship and practice.

Join us in our commitment to advancing legal transparency and knowledge accessibility through the LegalKit Pipeline project, as we strive to make French legal codes accessible to everyone on the 🤗 Datasets platform.

## Inspiration and Ideas

The LegalKit Pipeline project draws inspiration for cutting-edge techniques such as fine-tuning and the use of Retrieval-Augmented Generation (RAG) to create efficient and accurate language models tailored for legal practice.

## Tech Stack

**Language:** Python +3.9.0

## Installation

Clone the repo
```sh
git clone https://github.com/louisbrulenaudet/legalkit-pipeline.git
```

## Concurrent reading of the LegalKit

To use all the legal data published on LegalKit, you can use this code snippet:
```python
# -*- coding: utf-8 -*-
import concurrent.futures
import os

import datasets
from tqdm.notebook import tqdm

def dataset_loader(
    name:str,
    streaming:bool=True
) -> datasets.Dataset:
    """
    Helper function to load a single dataset in parallel.

    Parameters
    ----------
    name : str
        Name of the dataset to be loaded.

    streaming : bool, optional
        Determines if datasets are streamed. Default is True.

    Returns
    -------
    dataset : datasets.Dataset
        Loaded dataset object.

    Raises
    ------
    Exception
        If an error occurs during dataset loading.
    """
    try:
        return datasets.load_dataset(
            name,
            split="train",
            streaming=streaming
        )

    except Exception as exc:
        logging.error(f"Error loading dataset {name}: {exc}")

        return None


def load_datasets(
    req:list,
    streaming:bool=True
) -> list:
    """
    Downloads datasets specified in a list and creates a list of loaded datasets.

    Parameters
    ----------
    req : list
        A list containing the names of datasets to be downloaded.

    streaming : bool, optional
        Determines if datasets are streamed. Default is True.

    Returns
    -------
    datasets_list : list
        A list containing loaded datasets as per the requested names provided in 'req'.

    Raises
    ------
    Exception
        If an error occurs during dataset loading or processing.

    Examples
    --------
    >>> datasets = load_datasets(["dataset1", "dataset2"], streaming=False)
    """
    datasets_list = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_dataset = {executor.submit(dataset_loader, name): name for name in req}

        for future in tqdm(concurrent.futures.as_completed(future_to_dataset), total=len(req)):
            name = future_to_dataset[future]

            try:
                dataset = future.result()

                if dataset:
                    datasets_list.append(dataset)

            except Exception as exc:
                logging.error(f"Error processing dataset {name}: {exc}")

    return datasets_list


req = [
    "louisbrulenaudet/code-artisanat",
    "louisbrulenaudet/code-action-sociale-familles",
    # ...
]

datasets_list = load_datasets(
    req=req,
    streaming=True
)

dataset = datasets.concatenate_datasets(
    datasets_list
)
```

## Citing this project

If you use this code in your research, please use the following BibTeX entry.

```BibTeX
@misc{louisbrulenaudet2024,
  author =       {Louis Brulé Naudet},
  title =        {LegalKit Pipeline: Open Access to French Legal Codes on 🤗 Datasets},
  howpublished = {\url{https://github.com/louisbrulenaudet/legalkit-pipeline}},
  year =         {2024}
}
```

## Feedback

If you have any feedback, please reach out at [louisbrulenaudet@icloud.com](mailto:louisbrulenaudet@icloud.com).