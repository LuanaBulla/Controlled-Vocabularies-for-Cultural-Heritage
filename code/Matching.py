#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Luana Bulla'


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

stemmer = SnowballStemmer(language='italian')
nlp=spacy.load('it_core_news_sm')


class Matching:
  '''
  The class provides the tools to bring the textual input data to its equivalent in the controlled vocabulary.
  '''
  def __init__(self,sent):
    self.sent = sent
    
  def cut (sent,bag_SkosPrefLabel,bag_Uri,indice):  
        '''
        Through a recursive procedure, the textual data is returned to its equivalent within the controlled vocabulary. 
        The function allows the exact classification of the term.
        - sent: string to classify.
        - bag_SkosPrefLabel: list of labels in controlled vocabolary.
        - bag_uri: list of URI in controlled vocabolary.
        - indice = True --> [:-1] matching from the particular to the general;
                 = False --> [1:] matching from the general to the particular.
        - output: equivalent of the string in the controlled vocabulary.
        '''
        if sent in bag_SkosPrefLabel:          
            category = [sent,bag_Uri[bag_SkosPrefLabel.index(sent)]]            
        else:
            if len(sent) != 0:
              if indice == True:
                category= Matching.cut(' '.join(sent.split()[:-1]),bag_SkosPrefLabel,bag_Uri,indice) 
              else: 
                category= Matching.cut(' '.join(sent.split()[1:]),bag_SkosPrefLabel,bag_Uri,indice)
            else:
              category=[""] 
        return category
 
  def comparison (sent,bag_SkosPrefLabel,bag_Uri,indice): 
      '''
      Applying the matching.cut classifier, the function can return the following results:
      - category --> corresponding label in the controlled vocabulary,
        definizione --> specific addition not attributable to the corresponding term contained in the controlled vocabulary,
        uri -->  corresponding uri in the controlled vocabulary.
      - Non presente --> result not present in the controlled vocabulary.
      - Non riconducibile --> Given the vagueness of the term taken as input, it is possible to associate the word with more than one correspondent
        in the controlled dictionary. The term is therefore not attributable.
      '''
      bag_SkosPrefLabel=[ele.lower().strip() if type(ele) != float else "" for ele in bag_SkosPrefLabel]
      bag_Uri=[ele if type(ele) != float else "" for ele in bag_Uri]
      bag_MacroCategory={(v.split()[0].lower(),pos) for pos,v in enumerate(bag_SkosPrefLabel)if bag_Uri[pos].count('.')<=3}    
     
      if len(Matching.cut(sent,bag_SkosPrefLabel,bag_Uri,indice)[0]) != 0:
        category,uri = Matching.cut(sent,bag_SkosPrefLabel,bag_Uri,indice)
        definizione=(sent.replace(category,'')).strip()
      else:
        category=', '.join([bag_SkosPrefLabel[pos] for ele,pos in bag_MacroCategory if sent.split()[0] in ele.split()])
        definizione=(sent.replace(category.split()[0],'')).strip() if len(category)!=0 else ''
        uri=', '.join(set([bag_Uri[pos] for ele,pos in bag_MacroCategory if sent.split()[0] in ele.split()]))
                      
        if len(category)==0:
             category='Non presente'
             definizione='Non presente'
             uri='Non presente'                           
        else:
             category='Non pulibile'
             definizione='Non pulibile'
             uri='Non riconducibile'
        
      return [category, definizione, uri]

  def similarity (sent,bag_SkosPrefLabel,bag_Uri,score,indice):
    '''
    The function allows you to return the text string to its syntactically closest equivalent 
    within the controlled vocabulary by applying the levensthein distance.
    - sent: string to classify.
    - bag_SkosPrefLabel: list of labels in controlled vocabolary.
    - bag_uri: list of URI in controlled vocabolary.
    - score: threshold established and associated with the similarity metric.
    '''
    sent=sent.lower()
    max=[(lev.distance(sent,ele.lower()),ele) for ele in bag_SkosPrefLabel]
    max=sorted(max)
    sim= max[0]
      
    if sim[0] > score:
      category='Non presente'
      definition='Non presente'
      uri= 'Non presente'
    else:
      category,definition,uri=Matching.comparison(sim[1],bag_SkosPrefLabel,bag_Uri,indice)
    
    return [category,definition,uri]



class Matching_tool:
  
  def __init__(self,label,transEN_model):
    self.label=label  
    self.traslationEN_model = AutoModelForSeq2SeqLM.from_pretrained (transEN_model)
    self.translationEN_tokenizer = AutoTokenizer.from_pretrained(transEN_model)  

  def DoubleMatch (label,voc1_label, voc1_uri,voc2_label,voc2_uri,divider,score,indice): 
    '''
    Taken as input two vocabularies, the DoubleMatch function allows the search and classification 
    of the given term through the application of the recursive method.
    '''
    if divider not in label.split(): #i.e. split based on italian preposition 'di' 
      category,definition,uri,step = Matching_tool.SingleMatch(label,voc1_label,voc1_uri,score,indice)
      if category == 'Non presente':
        category2, definition2, uri2,step2 = Matching_tool.SingleMatch(label,voc2_label,voc2_uri,score,indice)
      else:
        category2, definition2, uri2,step2 = ['','','','']
    else:
      category,definition,uri,step = Matching_tool.SingleMatch(label,voc1_label,voc1_uri,score,indice)
      category2, definition2, uri2,step2 = ['','','','']

      if category != label:
        SecondPart_label=' '.join(label.split()[label.split().index(divider)+1:]) #It takes the second part of the word ['borchia di cinghia' --> 'cinghia']
        category,definition,uri,step = Matching_tool.SingleMatch(SecondPart_label,voc1_label,voc1_uri,score,indice)
        
        FirstPart_label = ' '.join(label.split()[:label.split().index(divider)]) #It takes the first part of the word ['borchia di cinghia' --> 'borchia']
        category2, definition2, uri2,step2 = Matching_tool.SingleMatch(FirstPart_label,voc2_label,voc2_uri,score,indice)
      
    res_voc1= [category, definition, uri,step]
    res_voc2= [category2, definition2, uri2,step2]
    
    return [res_voc1, res_voc2]
   
  
  def SingleMatch (label,voc1_label, voc1_uri,score,indice): 
    '''
    Taken as input a single vocabulary, the SingleMatch function allows the search and classification 
    of the given term through the application of the recursive method.
    '''    
    category,definition,uri=Matching.comparison(label,voc1_label,voc1_uri,indice)
    step='Matching ricorsivo'
    if category == 'Non presente':
        sent_lemma = ' '.join([ele.lemma_ for ele in nlp(label)])
        category,definition,uri = Matching.comparison(sent_lemma,voc1_label,voc1_uri,indice)
        definition = ''
        step = 'Matching lemmatizzazione'
    
    if category == 'Non presente':
        category,definition,uri= Matching.similarity (label,voc1_label,voc1_uri,score,indice)    
        step = 'Matching similarità'
    return [category, definition, uri,step] 

    
  def translationMatch (transEN_model,label): 
      '''
      This function allows the translation of the text from Italian to English.
      '''
      nlp = spacy.load('it_core_news_sm')
      translationEN_tokenizer = transEN_model
      corpus=[str(sent) for sent in nlp(label).sents]
      translator_en = pipeline("translation_it_to_en", model=transEN_model, tokenizer=translationEN_tokenizer)#,device=0) ##device!!
      translation = translator_en(label, max_length=4000)
      label_en = ' '.join(v for ele in translation for v in ele.values())
      
      return label_en

