# Controlled-Vocabularies-for-Cultural-Heritage

### Table of contents
* [General Information](#general-information)
* [Details](#details)
* [License](#license)

### General Information
Controlled vocabularies and data models have been defined as a common and shared way to organize recurring codes and nomenclatures in a standardized and normalized way (controlled vocabolary) and an exhaustive and rigorous conceptualization in a given domain (ontology or split data model). 
One of the problems encountered in this context is the mismatch of the data with the controlled vocabularies provided by the institution.
This difficulty was also identified in the General Catalogue of Italian Cultural Heritage (GC) made available by the Institute of the General Catalogue and Documentation (ICCD) of the Italian Ministry of Cultural Heritage (MIC) and in ArCo knowledge graph (KG) on Italian Cultural Heritage (CH).
To date, ICCD has provided a standard vocabulary for cataloging works of art, namely Vocabolary of Artworks. 
However, the data is not aligned with vocabulary, but types are specified by textual descriptions. While guidelines have been provided for filling such descriptions, perfect uniformity cataloging is impossible to obtain, due to subjectivity, human error and need to deal with specific cases. As a result, we found an uncontrolled multiplication and specialization of descriptions to define cultural assets, which are difficult to validate by domain experts.
To find a functional solution, we created a method for automatic text alignment descriptions of categories with controlled vocabularies in the domain of its culture. We followed a bottom-up approach that considers textual cultural heritage descriptions from a broad knowledge base and aligns them with corresponding terms in a controlled vocabulary of works of art.
In addition to alignment, our approach has led us to extend the existing vocabulary with new terms and to create a new vocabulary for management parts of works of art.

### Details
- The [OA_new_terms_list](https://github.com/LuanaBulla/Controlled-Vocabularies-for-Cultural-Heritage/blob/main/OA_new_terms_list.xlsx) file contains 2,272 new descriptions that cannot be linked to the suggested controlled vocabularies. As a result, ICCD experts can quickly review them for inclusion in the Vocabulary of Artworks.
- The [Precision - Recall](https://github.com/LuanaBulla/Controlled-Vocabularies-for-Cultural-Heritage/blob/main/Precision%20-%20Recall.xlsx) file contains the results of our methodology and the evaluation of the tool in terms of precision and recall.
- The [Validation_alignment](https://github.com/LuanaBulla/Controlled-Vocabularies-for-Cultural-Heritage/blob/main/Validation_alignment.xlsx) file contains all the results elaborated by the tool taking into account the textual descriptions provided by the cataloguers and the terms present in the controlled vocabularies.
- The [vocabulary_of_parts](https://github.com/LuanaBulla/Controlled-Vocabularies-for-Cultural-Heritage/blob/main/vocabulary_of_parts.xlsx) represents a new controlled vocabulary proposal. It is composed of 485 terms, in a flat structure without hierarchies, referring to parts of cultural heritage extracted by ArCo Knowledge Graph.

### License
This dataset is licensed under the [Creative Commons by-sa 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The data of ArCo, the knowledge graph of the Italian cultural heritage, were extracted through SPARQL Endpoint. 
