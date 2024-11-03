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
from dotenv import load_dotenv

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

load_dotenv()


class PisteAPI:
    def __init__(self, client_id: str = None, client_secret: str = None) -> None:
        """
        Initializes an instance of the PisteAPI class for interacting with the PISTE API.

        Parameters
        ----------
        client_id : str, optional
            The client ID obtained upon registration on PISTE.

        client_secret : str, optional
            The client secret associated with the client ID.

        Returns
        -------
        None
        """
        self.client_id = client_id or os.getenv("PISTE_ID")
        self.client_secret = client_secret or os.getenv("SECRET_KEY")
        self.token = self.oauth()

    def oauth(self) -> str:
        """
        Obtains an access token for authentication with the PISTE API.

        Returns
        -------
        token : dict
            A dictionary containing the access token information.
        """
        client = BackendApplicationClient(client_id=self.client_id)

        oauth = OAuth2Session(client=client)

        token = oauth.fetch_token(
            token_url="https://oauth.piste.gouv.fr/api/oauth/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        return token

    def post(self, url: str, data: dict) -> dict:
        """
        Fetches a resource from the PISTE API using the provided URL and data.

        Parameters
        ----------
        url : str
            The URL of the resource to fetch.

        data : dict
            The data to be included in the request.

        Returns
        -------
        response : dict
            A dictionary representing the fetched resource.
        """
        piste = OAuth2Session(client_id=self.client_id, token=self.token)

        headers = headers = {"Content-Type": "application/json"}

        response = piste.post(url, data=json.dumps(data), headers=headers)

        return json.loads(response.content.decode("utf-8"))


class Code:
    def __init__(self, code: list):
        """
        Initializes an instance of the Code class to extract section information.

        Parameters
        ----------
        code : list
            The code data.

        Returns
        -------
        None
        """
        self.data = []

    def extract_section_info(self, section: dict) -> None:
        """
        Extracts information from a section and its articles.

        Parameters
        ----------
        section : dict
            A dictionary representing a section with articles.

        Returns
        -------
        None
        """
        articles = section.get("articles", [])

        for article in articles:
            if "etat" in article and article["etat"] != "ABROGE":
                article_data = {
                    "id": article.get("id", ""),
                    "num": article.get("num", ""),
                    "title": section.get("title", ""),
                }
                self.data.append(article_data)

        return None

    def extract(self, data: list) -> list:
        """
        Recursively extracts section information from a nested data structure.

        Parameters
        ----------
        data : list
            A list of dictionaries representing sections and articles.

        Returns
        -------
        self.data : list
            The code data.
        """
        for section in data:
            self.extract_section_info(section)

            if "sections" in section:
                self.extract(section["sections"])

        return self.data


class Article:
    def __init__(self, article: list):
        """
        Initializes an instance of the Article class to extract informations.

        Parameters
        ----------
        article : list
            The article data.

        Returns
        -------
        None
        """
        self.article = article
        self.data = []

    def extract(self) -> list:
        """
        Extracts information from a section and its articles.

        Parameters
        ----------
        section : dict
            A dictionary representing a section with articles.

        Returns
        -------
        self.data : list
            The article data.
        """
        try:
            if "etat" in self.article and self.article["etat"] != "ABROGE":
                article_data = {
                    "conditionDiffere": self.article.get("conditionDiffere", ""),
                    "infosComplementaires": self.article.get(
                        "infosComplementaires", ""
                    ),
                    "surtitre": self.article.get("surtitre", ""),
                    "nature": self.article.get("nature", ""),
                    "texteHtml": self.article.get("texteHtml", ""),
                    "type": self.article.get("type", ""),
                    "dateFinExtension": self.article.get("dateFinExtension", ""),
                    "versionPrecedente": self.article.get("versionPrecedente", ""),
                    "dateDebut": self.article.get("dateDebut", ""),
                    "refInjection": self.article.get("refInjection", ""),
                    "idTexte": self.article.get("idTexte", ""),
                    "idTechInjection": self.article.get("idTechInjection", ""),
                    "origine": self.article.get("origine", ""),
                    "dateDebutExtension": self.article.get("dateDebutExtension", ""),
                    "dateFin": self.article.get("dateFin", ""),
                    "idEliAlias": self.article.get("idEliAlias", ""),
                    "cidTexte": self.article.get("cidTexte", ""),
                    "sectionParentId": self.article.get("sectionParentId", ""),
                    "multipleVersions": self.article.get("multipleVersions", ""),
                    "etat": self.article.get("etat", ""),
                    "versionArticle": self.article.get("versionArticle", ""),
                    "comporteLiensSP": self.article.get("comporteLiensSP", ""),
                    "sectionParentTitre": self.article.get("sectionParentTitre", ""),
                    "ordre": self.article.get("ordre", ""),
                    "infosRestructurationBranche": self.article.get(
                        "infosRestructurationBranche", ""
                    ),
                    "idEli": self.article.get("idEli", ""),
                    "sectionParentCid": self.article.get("sectionParentCid", ""),
                    "nota": self.article.get("nota", ""),
                    "num": self.article.get("num", ""),
                    "numeroBo": self.article.get("numeroBo", ""),
                    "texte": self.article.get("texte", ""),
                    "id": self.article.get("id", ""),
                    "infosRestructurationBrancheHtml": self.article.get(
                        "infosRestructurationBrancheHtml", ""
                    ),
                    "historique": self.article.get("historique", ""),
                    "cid": self.article.get("cid", ""),
                    "infosComplementairesHtml": self.article.get(
                        "infosComplementairesHtml", ""
                    ),
                    "renvoi": self.article.get("renvoi", ""),
                    "fullSectionsTitre": self.article.get("fullSectionsTitre", ""),
                    "notaHtml": self.article.get("notaHtml", ""),
                    "inap": self.article.get("inap", ""),
                }

                self.data.append(article_data)

            return self.data

        except Exception as e:
            print(f"Error occurred: {str(e)}")
