#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Luana Bulla'


import spacy
import string
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer(language='italian')
nlp=spacy.load('it_core_news_sm')


class Cleaning:
   def __init__(self,sent):
    self.sent=sent
       
   def elimination_of_repetitions (sent):
      '''
      If present, the function eliminates duplicates present in textual data.
      - sent: string to validate. 
      - output: validated string.

      Example: 'Borchia Borchia "stellare"' --> 'borchia "stellare"'
      '''
      sent=''.join(char for char in sent if char !=',')
      #indexing of repetitions    
      diz = defaultdict(list)
      for pos,word in enumerate (sent.split()):
          diz[word].append(pos)
            
      diz={k:max(v) for k,v in diz.items()}
      res=(" ".join([k for k, v in sorted(diz.items(), key=lambda item: item[1])])).strip()
     
      if type(res)!= float and len(res) != 0:
          if [word.pos_ for word in nlp(res.split()[0])][0] == 'ADP':
              if res.split()[0] in ['di','da']:
                  res=sent
              elif res.split()[0] == 'con' and 'di' in sent:
                  res=" ".join(sent.split()[:sent.split().index('di')])
              else:
                  res=res    
      return res


   def specification (sent,bag_SkosPrefLabel):  
      '''
      If present, the function normalizes the textual data by replacing the slash (/) contained within it. 
      The transformation rules include:
          - First case: elimination of the slash ['ciotola/' --> 'ciotola']  
          - Second case: elimination of the bar and repetition ['piatto/ piatto su piede' --> 'piatto su piede']
          - Third case: elimination of the slash and modification of the string with complement of specification ['ciotola/ ansa' --> 'ansa di ciotola']
          - Fourth case: presence of multiple slashes               
          - Fifth case: inversion of elements ['pendaglio (elemento di)' --> 'elemento di pendaglio']

      If present, any duplicates are also deleted at the end of the process.
      
      ###
      - sent: string to validate. 
      - bag_SkosPrefLabel: list of labels in controlled vocabulary. 
      - output: validated string.
      ###
      '''  
      bag_SkosPrefLabel=[ele if type(ele) != float else "" for ele in bag_SkosPrefLabel]
                                                 
      if '/' in sent and sent.count('/')==1: 
          norm=sent.strip().split('/') 
          #First case     
          if norm[-1] == "": 
              res=norm[0]       
          #Second case
          elif norm[1]!="" and norm[0]==norm[1].strip().split()[0]: 
              res=norm[1].strip()
          #Third case
          else:           
              if [ele.pos_ for ele in nlp((norm[-1]+'.').split()[0].strip())][0] in ['ADJ','ADP']:  
                  if norm[-1].split()[0].strip() in set(["".join(ele.split()[0]) for ele in bag_SkosPrefLabel if '/' not in ele]): 
                      res= f"{norm[-1]} di {norm[0]}".strip()
                  else:
                      res="".join(norm).strip()    
              else: 
                  res=(f"{norm[-1]} di {norm[0]}").strip()
      #Fourth case         
      elif '/' in sent and sent.count('/')>1: 
          norm=sent.split('/')
          res=(f'{norm[1]} di{norm[2]} di {norm[0]}').strip()
      
      #Fifth case
      elif 'di)' in sent and '?' not in sent:
          norm=[ele for ele in sent.split('(')]
          norm=[(ele.replace('di)',"").strip()) if 'di)' in ele else ele for ele in norm]
          res= f"{norm[-1]} di {norm[0]}"    
      else:
          res=sent

      norm2=Cleaning.elimination_of_repetitions(res) #elimination of any duplicates
      return norm2


   def partially_rebuildable_form (sent,list_of_terms): 
      '''
      If present, the function removes the words in the list of terms from the text string.
      if the sentence is composed only of a term contained within the list, the function will not make any changes. (?? da considerare)
      - sent: string to validate.
      - list_of_terms: list of terms to delete.
      - output: validated string.

      Example: 'bicchiere/ frammenti' --> 'bicchiere'
      '''
      sent_raw = sent
      check = [word for word in list_of_terms if stemmer.stem(word) in sent]
      if len(check) > 0 and stemmer.stem(sent) != check[0]: 
              sent=' '.join(' /'.join(ele.split('/')) for ele in sent.split())
              sent=' '.join(ele for ele in sent.split() if stemmer.stem(ele) not in stemmer.stem(check[-1]))    
              sent=' '.join(ele for ele in sent.split() if ele not in ['di)','/'])     
              for pos,ele in enumerate(sent.split()):
                if ele[0]=='/':
                  sent=sent.replace(ele,ele[1:])
                  sent=sent.replace(sent.split()[pos-1],sent.split()[pos-1]+'/')    
                if sent.split('/')[-1] == '':
                    sent=sent.replace('/','')   
              label = sent.strip().lower()
      else:
          label = sent_raw
     
      if len(label) == 0:
         label = sent_raw
     
      return label
    
   def lemmatizzazione(sent):
      return' '.join([ele.lemma_ for ele in nlp(sent)])

   def final_processing (sent):
       '''
       if present, this function takes care of eliminating punctuation from the input string.
       '''
       sent = ''.join(char for char in sent if char not in string.punctuation) 

       

       
   

       
       
       
       
       
       
       