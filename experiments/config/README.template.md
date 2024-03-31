---
license: apache-2.0
language:
- fr
multilinguality:
- monolingual
tags:
- finetuning
- legal
- french law
- droit français
- {{ base }}
source_datasets:
- original
pretty_name: {{ base }}
task_categories:
- text-generation
- table-question-answering
- summarization
- text-retrieval
- question-answering
- text-classification
size_categories:
- 1K<n<10K
---
# {{ base }}, non-instruct ({{ date }})

This project focuses on fine-tuning pre-trained language models to create efficient and accurate models for legal practice. 

Fine-tuning is the process of adapting a pre-trained model to perform specific tasks or cater to particular domains. It involves adjusting the model's parameters through a further round of training on task-specific or domain-specific data. While conventional fine-tuning strategies involve supervised learning with labeled data, instruction-based fine-tuning introduces a more structured and interpretable approach.

Instruction-based fine-tuning leverages the power of human-provided instructions to guide the model's behavior. These instructions can be in the form of text prompts, prompts with explicit task descriptions, or a combination of both. This approach allows for a more controlled and context-aware interaction with the LLM, making it adaptable to a multitude of specialized tasks.

Instruction-based fine-tuning significantly enhances the performance of LLMs in the following ways:

- Task-Specific Adaptation: LLMs, when fine-tuned with specific instructions, exhibit remarkable adaptability to diverse tasks. They can switch seamlessly between translation, summarization, and question-answering, guided by the provided instructions.
- Reduced Ambiguity: Traditional LLMs might generate ambiguous or contextually inappropriate responses. Instruction-based fine-tuning allows for a clearer and more context-aware generation, reducing the likelihood of nonsensical outputs.
- Efficient Knowledge Transfer: Instructions can encapsulate domain-specific knowledge, enabling LLMs to benefit from expert guidance. This knowledge transfer is particularly valuable in fields like tax practice, law, medicine, and more.
- Interpretability: Instruction-based fine-tuning also makes LLM behavior more interpretable. Since the instructions are human-readable, it becomes easier to understand and control model outputs.
- Adaptive Behavior: LLMs, post instruction-based fine-tuning, exhibit adaptive behavior that is responsive to both explicit task descriptions and implicit cues within the provided text.

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

## Dataset generation

This JSON file is a list of dictionaries, each dictionary contains the following fields:

- `instruction`: `string`, presenting the instruction linked to the element.
- `input`: `string`, signifying the input details for the element.
- `output`: `string`, indicating the output information for the element.
- `start`: `string`, the date of entry into force of the article. 
- `expiration`: `string`, the date of expiration of the article. 
- `num`: `string`, the id of the article.

We used the following list of instructions for generating the dataset:
```python
instructions = [
    "Compose l'intégralité de l'article sous forme écrite.",
    "Écris la totalité du contenu de l'article.",
    "Formule la totalité du texte présent dans l'article.",
    "Produis l'intégralité de l'article en écriture.",
    "Développe l'article dans son ensemble par écrit.",
    "Génère l'ensemble du texte contenu dans l'article.",
    "Formule le contenu intégral de l'article en entier.",
    "Rédige la totalité du texte de l'article en entier.",
    "Compose l'intégralité du contenu textuel de l'article.",
    "Rédige l'ensemble du texte qui constitue l'article.",
    "Formule l'article entier dans son contenu écrit.",
    "Composez l'intégralité de l'article sous forme écrite.",
    "Écrivez la totalité du contenu de l'article.",
    "Formulez la totalité du texte présent dans l'article.",
    "Développez l'article dans son ensemble par écrit.",
    "Générez l'ensemble du texte contenu dans l'article.",
    "Formulez le contenu intégral de l'article en entier.",
    "Rédigez la totalité du texte de l'article en entier.",
    "Composez l'intégralité du contenu textuel de l'article.",
    "Écrivez l'article dans son intégralité en termes de texte.",
    "Rédigez l'ensemble du texte qui constitue l'article.",
    "Formulez l'article entier dans son contenu écrit.",
    "Composer l'intégralité de l'article sous forme écrite.",
    "Écrire la totalité du contenu de l'article.",
    "Formuler la totalité du texte présent dans l'article.",
    "Produire l'intégralité de l'article en écriture.",
    "Développer l'article dans son ensemble par écrit.",
    "Générer l'ensemble du texte contenu dans l'article.",
    "Formuler le contenu intégral de l'article en entier.",
    "Rédiger la totalité du texte de l'article en entier.",
    "Composer l'intégralité du contenu textuel de l'article.",
    "Rédiger l'ensemble du texte qui constitue l'article.",
    "Formuler l'article entier dans son contenu écrit.",
    "Quelles sont les dispositions de l'article ?",
    "Quelles dispositions sont incluses dans l'article ?",
    "Quelles sont les dispositions énoncées dans l'article ?",
    "Quel est le texte intégral de l'article ?",
    "Quelle est la lettre de l'article ?"
]
```

## Feedback

If you have any feedback, please reach out at [louisbrulenaudet@icloud.com](mailto:louisbrulenaudet@icloud.com).