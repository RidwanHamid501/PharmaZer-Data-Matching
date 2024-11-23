# PharmaZer Data Matching Project

<img src="https://user-images.githubusercontent.com/5181870/187668128-902f4710-e088-4da5-a207-97e3930c5fa5.png" style="width: 400px;" />

## Overview
PharmaZer is a pharmaceutical company focused on improving the understanding and treatment of diseases. Currently, the company is studying Sjogren Syndrome, a condition affecting tear and saliva glands. By collecting and analyzing research papers, PharmaZer aims to develop innovative treatments and advance the understanding of this disease.

PharmaZer's methodology involves collating research papers from various sources to build a comprehensive knowledge base. This approach can also be applied to other diseases, such as cancer or neurological disorders, to develop safe and effective treatments. To achieve these goals, PharmaZer requires a scalable, repeatable tool to organize and analyze research data efficiently.

## Problem Statement
One significant challenge in collating research papers is the inconsistency in how institutions are named across different publications. For example:

- \"Harvard University\" vs. \"Harvard Medical School\"

These inconsistencies complicate the accurate aggregation and analysis of data. Resolving this issue involves standardizing the naming of organizations and institutions using the Global Research Identifier Database (GRID) as a \"source of truth.\" This process ensures that research papers are correctly matched and analyzed, providing reliable and trustworthy results.

PharmaZer has provided two key datasets:

1. **PubMed**: Contains information about medical research papers, including article metadata and author affiliations.
2. **GRID**: Standardized information about research institutions, including aliases and relationships.

The primary objective is to match the institutions listed in the PubMed dataset with their standardized names in the GRID dataset.

## Inputs
The project uses the following datasets:

### PubMed Dataset
- A single XML file: `pubmed_result_sjogren.xml`
- Contains the following fields:
  - **Article Title**
  - **Article Text**
  - **Journal Name**
  - **List of Authors with Affiliations**
  - **Keywords**

### GRID Dataset
- Four CSV files linked by `grid_id`:
  - `institutes.csv`: Contains institution names, URLs, and contact details.
  - `addresses.csv`: Provides institution addresses and geolocation data.
  - `aliases.csv`: Lists alternative names for institutions.
  - `relationships.csv`: Shows relationships between institutions.

## Outputs
The output is a single CSV file with the following columns:

- Article PMID
- Article Title
- Article Keywords
- Article MESH Identifiers
- Article Year
- Author First Name
- Author Last Name
- Author Initials
- Author Full Name
- Author Email
- Affiliation Name (from PubMed)
- Affiliation Name (from GRID)
- Affiliation Zipcode
- Affiliation Country
- Affiliation GRID Identifier

The resulting file should present a flattened structure, with one row per affiliation.

## Approach

### Data Processing Steps

1. **Parsing PubMed XML Data**
   - Extract relevant fields from the XML file using utility functions.
   - Flatten nested data structures to handle multiple authors and affiliations.

2. **Data Wrangling with Pandas**
   - Clean and enrich affiliations from PubMed.
   - Standardize typos, remove blank spaces, and extract additional information like author emails.

3. **Text Enrichment with spaCy**
   - Use Named Entity Recognition (NER) to extract organization and location data from affiliations.

4. **Data Matching**
   - Match PubMed affiliations with GRID standard names using string similarity metrics.
   - Employ tools like RapidFuzz for accurate matching.

### Automation Requirements

- Listen for new XML files added to an S3 bucket.
- Trigger the pipeline upon file upload.
- Store the resulting CSV in an output S3 bucket.
- Notify users when tasks begin and end.

### Infrastructure

- **Input S3 Bucket**: `sigma-pharmazer-input`
  - Configured to send event notifications to AWS EventBridge.
- **Output S3 Bucket**: `sigma-pharmazer-output`
  - Stores the final CSV output.
- Additional infrastructure can be determined based on the project’s requirements.

## Tools
- **Python**: For data processing and analysis.
- **Pandas**: For data wrangling and cleaning.
- **spaCy**: For natural language processing and entity recognition.
- **RapidFuzz**: For string similarity and matching.
- **AWS**: For cloud-based storage and pipeline automation.

## Background Information
- [Global Research Identifier Database (GRID)](https://en.wikipedia.org/wiki/Global_Research_Identifier_Database)
- [PubMed](https://en.wikipedia.org/wiki/PubMed)
- [Sjogren Syndrome](https://pubmed.ncbi.nlm.nih.gov/?term=sjogren+syndrome)
- [Medical Subject Headings (MeSH)](https://en.wikipedia.org/wiki/Medical_Subject_Headings)

## Conclusion
This project provides PharmaZer with a robust and scalable system for organizing and analyzing research data. By resolving inconsistencies in institutional names and automating data processing, PharmaZer can accelerate its research efforts and contribute to the development of innovative treatments.
