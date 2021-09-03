#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Luana Bulla'

from  Matching import Matching_tool, Matching
from  Cleaning import Cleaning

import transformers
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from transformers import AutoModelForSeq2SeqLM
from transformers import pipeline
import pandas as pd
import spacy
import os
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
import re
import Levenshtein as lev
import string


def scrittura_file(df, path, nome_file, header):
    if not os.path.isfile(nome_file):
        df.to_csv(nome_file, index=False, header=header)
    else:
        df.to_csv(nome_file, mode='a', index=False, header=False)


vocabolario=pd.read_csv('OA.csv') #
termini_estratti=pd.read_csv('OA_termini estratti (rdf_type).csv') #Description written by catalogers
vocabolario_parti = pd.read_csv('vocabolario delle Parti.csv') #

list_of_sentences = termini_estratti['entityLabel'] #list of words to analyze

#First vocabolary:
list_of_label=[ele.strip() for ele in vocabolario['skos:prefLabel']] #label of controlled vocabolary (OA)
list_of_uri=[ele.strip() for ele in vocabolario['uri']] #uri of controlled vocabolary (OA)

#Second vocabolary:
list_of_label2 = [ele.strip() for ele in vocabolario_parti['Cultural_Part']] #label of controlled vocabolary (vocabolario delle parti)
list_of_uri2 = [ele.strip() for ele in vocabolario_parti['Uri']] #uri of controlled vocabolary (vocabolario delle parti)

botton_up = True #[:-1]
top_down = False #[1:]
score= 3
divider = ['di','dello','del','della','dell','dei','degli','delle'] #list of possible preposition to split the string

altLabel = {row['skos:prefLabel'].strip():[row['skos:altLabel'].strip(),row['skos:altLabel.1']] for index,row in vocabolario.iterrows() if type(row['skos:altLabel']) != float }
altLabel = {k:[ele.strip() for ele in v if type(ele)!=float] for k,v in altLabel.items()}


list_of_deleted_terms = ['forma parzialmente ricostruibile','calco','modello','modellino','frammento']



if __name__ == "__main__":   
    
  for index,sent in enumerate(list_of_sentences): ##fai prova generale anche con solo 'frammento'

    raw_label=sent.lower().strip()

    label=Cleaning.partially_rebuildable_form(raw_label,list_of_deleted_terms)
    label=Cleaning.specification(label,list_of_label)
    label=Cleaning.elimination_of_repetitions(label)
    
    label = 'None '+ label if label.split()[0]=='di' else label #'di ...'
    label = ' '.join(label.split()[:-1]) if label.split()[-1]=='di' else label #'... di'
    label = ''.join(char for char in label if char not in string.punctuation) #togli punteggiatura
    
    alt_label = ''.join([k for k,v in altLabel.items() if label in v]) #altLabel
    label = alt_label.strip() if len(alt_label) > 0 else label

    #check DI --> PER:
    lista = ['fodero di','custodia di','veste di', 'corredo di','mantello di statua', 'mantelletto di statua',
         'sandalo di statua', 'velo di statua','vestiario di statua', 'cintura di statua',
         'conio di', 'conopeo di', 'coperta di'] 

    check_per = [ele for ele in lista if ele in label ]
    label = ' '.join('per' if ele == 'di'else ele for ele in label.split()) if len(check_per) >0 else label
    print(label)

    div = [ele for ele in divider if ele in label.split()]
    if len(div) == 0:
      category,definition,uri,step = Matching_tool.SingleMatch(label,list_of_label,list_of_uri,score,botton_up)
      parte, definition_parte, uri_parte,step2 = ['','','',''] ##da togliere il quarto

    else:
      risultati_vocabolario, risultato_parti = Matching_tool.DoubleMatch(label,list_of_label,list_of_uri,list_of_label2,list_of_uri2,div[0],score,botton_up)
      category,definition,uri,step = risultati_vocabolario
      parte, definition_parte, uri_parte,step2 = risultato_parti
      

    if category == 'Non presente':
        category,definition,uri,step = Matching_tool.SingleMatch(label,list_of_label,list_of_uri,score,top_down)
        step = 'Match inverso'

    print(index)
    print(f"label --> {category} \n def --> {definition} \n uri --> {uri} \n step --> {step} \n")
    print(f"part_label --> {parte} \n def --> {definition_parte} \n uri --> {uri_parte} \n step --> {step2} \n")

    
    output=pd.DataFrame([[uri,category, uri_parte, parte, raw_label,step,step2]])

    scrittura_file(output,
                  "", #name of path
                  'Results.csv',
                  ['URI', 'rdfs:label', 'URI_CulturalPart','Cultural_Part', 'old_label','step','step_per_parte'])
        
    
    
    
