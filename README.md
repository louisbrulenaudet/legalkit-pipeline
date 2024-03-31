# LegalKit Pipeline: Open Access to French Legal Codes on 🤗 Datasets

[![Python](https://img.shields.io/pypi/pyversions/tensorflow.svg)](https://badge.fury.io/py/tensorflow)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Maintainer](https://img.shields.io/badge/maintainer-@louisbrulenaudet-blue)

The LegalKit Pipeline project aims to provide open access to French legal codes on the 🤗 Datasets platform, thereby democratizing access to legal information and promoting transparency and understanding of the French legal system. Our mission is to compile and publish a comprehensive collection of French legal codes, spanning civil law, criminal law, and administrative regulations among other areas, to cater to the diverse needs of legal professionals, researchers, students, and enthusiasts alike.

With LegalKit Pipeline, individuals have the opportunity to explore, analyze, and leverage French legal texts for various purposes, empowering them to navigate and interpret the law with ease. By facilitating access to this valuable resource, we aim to foster greater transparency and knowledge accessibility in the legal domain, enabling stakeholders to make informed decisions and advance legal scholarship and practice.

Join us in our commitment to advancing legal transparency and knowledge accessibility through the LegalKit Pipeline project, as we strive to make French legal codes accessible to everyone on the 🤗 Datasets platform.

## Inspiration and Ideas

The LegalKit Pipeline project draws inspiration for cutting-edge techniques such as fine-tuning and the use of Retrieval-Augmented Generation (RAG) to create efficient and accurate language models tailored for legal practice.

### Fine-Tuning for Legal Practice

Fine-tuning plays a pivotal role in adapting pre-trained language models (LLMs) to the intricacies of legal practice. It involves adjusting the parameters of a pre-trained model through additional training on task-specific or domain-specific data. By fine-tuning LLMs with specific instructions, we aim to enhance their adaptability to diverse legal tasks, such as translation, summarization, and question-answering.

Instruction-based fine-tuning is particularly noteworthy for its structured and interpretable approach. By leveraging human-provided instructions, such as text prompts or explicit task descriptions, we can guide the behavior of LLMs in a controlled and context-aware manner. This approach not only enhances the performance of LLMs but also improves their interpretability and adaptability to specialized legal tasks.

**Key Benefits of Instruction-Based Fine-Tuning**

Instruction-based fine-tuning offers several key benefits for legal practitioners and researchers:

- **Task-Specific Adaptation:** LLMs fine-tuned with specific instructions demonstrate remarkable adaptability to a wide range of legal tasks, from legal document analysis to case summarization, guided by task-specific instructions.
- **Reduced Ambiguity:** Traditional LLMs may produce ambiguous or contextually inappropriate responses. Instruction-based fine-tuning reduces ambiguity by providing clearer and more context-aware model outputs, thereby enhancing the quality of legal analysis and decision-making.
- **Efficient Knowledge Transfer:** Instructions can encapsulate domain-specific knowledge, facilitating efficient knowledge transfer to LLMs. This enables LLMs to benefit from expert guidance in specialized legal domains such as tax law, contract analysis, and regulatory compliance.
- **Interpretability:** Instruction-based fine-tuning enhances the interpretability of LLM behavior. Human-readable instructions make it easier to understand and control model outputs, enabling legal practitioners to trust and effectively utilize LLM-generated insights.
- **Adaptive Behavior:** LLMs, post instruction-based fine-tuning, exhibit adaptive behavior that is responsive to both explicit task descriptions and implicit cues within the provided legal text. This adaptability enables LLMs to generate contextually relevant and accurate legal analyses, enhancing their utility in real-world legal applications.

### Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) introduces a novel approach to language model fine-tuning, offering several key benefits for legal practitioners and researchers:

- **Enhanced Contextual Understanding:** RAG leverages retriever models to augment generation with relevant context from external knowledge sources. This enables LLMs to generate responses that are more contextually grounded and relevant to the task at hand, improving the quality and accuracy of legal analyses.
- **Broader Knowledge Integration:** By incorporating external knowledge sources into the generation process, RAG expands the scope of information accessible to LLMs. This facilitates more comprehensive legal analyses, allowing practitioners to consider a wider range of legal and regulations when generating responses.
- **Improved Response Coherence:** RAG helps mitigate the issue of response ambiguity by providing additional context from external knowledge sources. This leads to more coherent and logically consistent responses, reducing the likelihood of generating nonsensical or contextually inappropriate outputs.
- **Efficient Information Retrieval:** RAG streamlines the process of accessing relevant information by leveraging retriever models to efficiently retrieve contextually relevant passages from external knowledge sources. This enhances the efficiency of legal research and analysis, enabling practitioners to access pertinent information more quickly and accurately.
- **Scalability and Adaptability:** RAG's modular architecture allows for easy integration with existing LLMs and retrieval models, making it scalable and adaptable to different legal domains and tasks. This flexibility enables practitioners to tailor RAG-based solutions to their specific needs, enhancing their utility in real-world legal applications.

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