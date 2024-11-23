'''Process entire PubMed and Grid datasets'''
import logging
from os import environ as ENV
import re
import xml.etree.ElementTree as ET
import pandas as pd
import spacy
import pycountry
from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from dotenv import load_dotenv


def load_xml(path: str) -> ET.Element:
    '''Load an XML file and return its root element'''
    tree = ET.parse(path)
    return tree.getroot()


def extract_article_data(article: ET.Element) -> dict[str]:
    '''Extract article data from an XML element'''
    return {
        "Article Title": article.findtext(".//ArticleTitle"),
        "Article Year": article.findtext(".//PubDate/Year"),
        "Article PMID": article.findtext(".//PMID"),
        "Keywords": [kw.text for kw in article.findall(".//KeywordList/Keyword")],
        "MESH Identifiers": [mesh.get("UI") for mesh in article.findall(".//DescriptorName")]
    }


def extract_author_data(author: ET.Element) -> dict[str]:
    '''Extract author data from an XML element'''
    fore_name = author.findtext('ForeName') or ''
    last_name = author.findtext('LastName') or ''
    affiliations = [aff.text for aff in author.findall(
        ".//AffiliationInfo/Affiliation")]
    grid_id = next(
        (
            aff.findtext("Identifier[@Source='GRID']")
            for aff in author.findall(".//AffiliationInfo")
            if aff.find("Identifier[@Source='GRID']") is not None
        ),
        None,
    )
    return {
        "First Name": author.findtext("ForeName"),
        "Last Name": author.findtext("LastName"),
        "Initials": author.findtext("Initials"),
        "Full Name": f"{fore_name} {last_name}".strip(),
        "Affiliations": ", ".join(affiliations),
        "GRID ID": grid_id
    }


def process_affiliation(doc: spacy.tokens.Doc) -> dict[str]:
    '''Find extra information with regex (email and zipcode)'''
    countries = {country.name for country in pycountry.countries}
    email = re.search(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", doc.text)
    zipcode = re.search(
        r"\b\d{5}(?:-\d{4})?\b|\b[A-Z]\d[A-Z] ?\d[A-Z]\d\b|\b[A-Z]{1,2}\d{1,2}[A-Z]? ?\d[A-Z]{2}\b",
        doc.text
    )
    country = next((ent.text for ent in doc.ents if ent.label_ ==
                    "GPE" and ent.text in countries), None)
    return {
        "Email": email.group(0) if email else None,
        "Zipcode": zipcode.group(0) if zipcode else None,
        "Country": country
    }


def extract_affiliation_details(article_data: pd.DataFrame, col_name: str, nlp) -> pd.DataFrame:
    '''Extract affiliation details such as email, zipcode, and country from a DataFrame column.'''
    docs = nlp.pipe(article_data[col_name],  # pylint: disable=E0606
                    batch_size=50)
    details = [process_affiliation(doc) for doc in docs]
    article_data["Email"] = [detail["Email"] for detail in details]
    article_data["Zipcode"] = [detail["Zipcode"] for detail in details]
    article_data["Country"] = [detail["Country"] for detail in details]
    return article_data


def extract_org_entities(text: str, nlp) -> list[str]:
    """Extract ORG entities from text using spaCy"""
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "ORG"]


def match_affiliations_with_grid(article_data: pd.DataFrame,
                                 col_name: str, grid_data: pd.DataFrame, nlp) -> pd.DataFrame:
    '''Match affiliations in a DataFrame column with GRID data'''
    unique_affiliations = article_data[col_name].dropna().unique()
    matches = {}

    for affiliation in unique_affiliations:
        org_entities = extract_org_entities(affiliation, nlp)
        if not org_entities:
            matches[affiliation] = (None, None)
            continue

        best_match = None
        best_score = 0
        best_grid_id = None

        for org in org_entities:
            match = process.extractOne(
                org, grid_data['name'], scorer=Levenshtein.normalized_similarity, score_cutoff=0.6)
            if match and match[1] > best_score:
                best_match = match[0]
                best_score = match[1]
                best_grid_id = grid_data.loc[
                    grid_data['name'] == best_match, 'grid_id'
                ].values[0]

        matches[affiliation] = (best_match, best_grid_id)

    article_data["GRID Affiliation Name"] = article_data[col_name].map(
        lambda x: matches.get(x, (None, None))[0])
    article_data["GRID ID"] = article_data[col_name].map(
        lambda x: matches.get(x, (None, None))[1])
    return article_data


def process_articles(root: ET.Element, grid_data: pd.DataFrame, nlp) -> pd.DataFrame:
    '''Process articles from an XML root and match affiliations with GRID data'''
    rows = []

    for article in root.findall(".//PubmedArticle"):
        article_data = extract_article_data(article)

        for author in article.findall(".//Author"):
            author_data = extract_author_data(author)

            rows.append({
                **article_data,
                **author_data
            })

    converted_pubmed_data = pd.DataFrame(rows)
    unmatched_article_data = extract_affiliation_details(
        converted_pubmed_data, "Affiliations", nlp)
    logging.info("Affiliations extraction complete.")
    matched_article_data = match_affiliations_with_grid(
        unmatched_article_data, "Affiliations", grid_data, nlp)
    return matched_article_data


def set_logging():
    '''Set the logging configuration'''
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")


def main(file_name):
    '''Main function to match pubmed and grid datasets and return dataframe'''
    set_logging()
    nlp = spacy.load("en_core_web_sm")

    logging.info("Loading XML data...")
    tree_root = load_xml(file_name)

    logging.info("Loading GRID data...")
    grid_dataset = pd.read_csv("institutes.csv")

    logging.info("Processing articles...")
    final_article_data = process_articles(tree_root, grid_dataset, nlp)

    return final_article_data


if __name__ == "__main__":
    load_dotenv()
    file = ENV["FILE_NAME"]
    print(main(file))
