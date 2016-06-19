#!/usr/bin/python3
#Group 10 - Stan van Suijlekom, Ruben Brouwers, Leon Graumans

import os
import nltk
import wikipedia
from nltk.corpus import *
from nltk.stem.wordnet import *
from nltk import pos_tag, word_tokenize
from nltk.wsd import lesk
from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import warnings
warnings.filterwarnings("ignore")

def rawtext(filename):
	f = open(filename, "r")
	rawText = f.read()
	rawText = rawText.split("\n")
	f.close()
	words = []
	lines = []	
	for line in rawText:
		line = line.split(" ")
		lines.append(line)
	for word in lines[:-1]:
		words.append(word[3])

	return words, lines

def LOC_ORG_PERtagger(NERlist):

	TAGlist = []
	LOClist = []
	for item in NERlist:
		if item[1] == "LOCATION":
			LOClist.append(item)
		elif item[1] == "PERSON":
			TAGlist.append((item[0],"PER"))
		elif item[1] == "ORGANIZATION":
			TAGlist.append((item[0],"ORG"))

	return LOClist, TAGlist

def CIT_COUtagger(LOClist):

	TAGlist = []
	for loc in LOClist:
		synsets = wordnet.synsets(loc[0], pos="n")
		for synset in synsets:
			definition = synset.definition()
			if 'city' in definition or 'village' in definition or 'town' in definition or 'capital' in definition or 'metropolis' in definition:
				TAGlist.append((loc[0],"CIT"))
				break
			elif 'country' in definition or 'monarchy' in definition or 'republic' in definition or 'state' in definition:
				TAGlist.append((loc[0], "COU"))
				break
			else:
				break
			continue

	return TAGlist

def ANI_SPO_NAT_ENTtagger(words):

	TAGlist = []
	for word in words:
		synsets = wordnet.synsets(word)
		for synset in synsets:
			definition = synset.definition()
			if "animal" in definition or "beast" in definition or "pet" in definition:
				TAGlist.append((word,"ANI"))
				break
			elif "sport" in definition or "game" in definition or "athletics" in definition:
				TAGlist.append((word,"SPO"))
				break
			elif "forest" in definition or "vulcano" in definition or "sea" in definition or "ocean" in definition or "river" in definition or "lake" in definition or "mountain" in definition:
				TAGlist.append((word,"NAT"))
				break
			elif "book" in definition or "magazine" in definition or "film" in definition or "song" in definition or "concert" in definition:
				TAGlist.append((word,"ENT")) 
			else:
				break

	return TAGlist

def writeout(ALLlist, filesource, lines):

	ENDlist = []
	for item in ALLlist:
		for tag in item:
			ENDlist.append(tag)
	outfile = open(filesource + ".ner", "w")
	for line in lines[:-1]:
		for tag in ENDlist:
			if line[3] == tag[0] and len(line) != 6:
				line.append(tag[1])
		sentence = " ".join(line) 
		outfile.write("{}\n".format(sentence))
	print(filesource," is tagged.") 
	outfile.close()

def read_data(filename):
	''' Read the data from the provided file '''
	with open(filename + ".ner", "r") as f:
		nnp_list = []
		for line in f:
			line = line.split()
			if line[4] in ["NNP"] and len(line) > 5:
				# If the word is a NNP the word_id and word are stored in nnp_list
					if line[3] not in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:    
						nnp_list.append((line[2], line[3])) 
	f.close()  
	return nnp_list
				
def nnp_checker(nnp_list):
	''' Checks 'nnp_list' for NNP's containing multiple words to combine them ''' 
	#Incompleet, nog niet werkend gekregen
	final_nnp_list = []
	print(nnp_list)
	while len(nnp_list) > 0:  
		first_el = nnp_list.pop(0)	#('1001', 'China')
		n_gram = (first_el[1])		#China
		word_ids = [first_el[0]] 	#['1001']
		counter = 1
		if len(nnp_list) == 0:
		    word_ids.append(n_gram)
		    final_nnp_list.append(word_ids)		
		else:
		    for nnp in nnp_list:
			    if nnp[0] == str(int(first_el[0])+counter):
				    n_gram += " " + nnp[1]
				    word_ids.append(nnp[0])
				    counter += 1
				    if len(nnp_list) == 1:
				        word_ids.append(n_gram)
				        final_nnp_list.append(word_ids)	
				        nnp_list.pop()
				        break			        
			    else:			        
				    word_ids.append(n_gram)
				    final_nnp_list.append(word_ids)
				    if counter > 1:
				        for i in range(counter-1):
					        nnp_list.pop(0)
				    break
        print(final_nnp_list)
	return final_nnp_list 
 
def link_checker(ngram):
	''' Checks if the word gives a valid wikipedia link '''
	try:
		page = wikipedia.page(ngram)
		link = page.url
		return link
	except wikipedia.exceptions.DisambiguationError: 
		#link = ngram.split(" ") 
		#newlink = "_".join(ngram)
		link = 'http://en.wikipedia.org/wiki/' + ngram + '_(disambiguation)'
		return link
	except wikipedia.exceptions.PageError:
		wordlist = ngram.split()
		counter = 0
		for word in wordlist:
			word.lower()
			if word in ["prime","minister","president"]:
				wordlist.pop(counter)
			counter += 1  
		ngram.join(wordlist)
		try:
			page = wikipedia.page(ngram)
			link = page.url
			return link 
		except wikipedia.exceptions.PageError:
			return -1
		except wikipedia.exceptions.DisambiguationError:  
			return -1


def wiki_writeout(FINAL_NNPlist, lines, filesource):

	infile = open(filesource + ".ner", "r")
	outfile = open(filesource + ".wiki", "w")
	for line in infile:
		line = line.rstrip()
		line = line.split(" ")
		for i in line[:-1]:
			for nnp in FINAL_NNPlist:
				if line[2] in nnp[:-2]:
					line.append(nnp[-1])
			break
		sentence = " ".join(line)
		#print(sentence) 
		outfile.write("{}\n".format(sentence))
	print(filesource," is wikified.")
	infile.close()
	outfile.close()

def bigram_creator():
	tokens = nltk.word_tokenize(all_words)
	bi_grams = nltk.bigrams(tokens)

	fdist = nltk.FreqDist(bi_grams)
	fdist = fdist.items()
	fdist = sorted(fdist)
	for k,v in fdist.items():
		if v > 1:
			print (k,v)
	

def main():

	file_paths = []

	for root, directories, files in os.walk("training"):
		for filename in files:
			if filename == "en.tok.off.pos":
				filepath = os.path.join(root, filename)
				file_paths.append(filepath) 

	classifier = "stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz"
	jar = "stanford-ner-2014-06-16/stanford-ner-3.4.jar"
	NERTagger = StanfordNERTagger(classifier, jar)
	for filesource in file_paths:
		words, lines = rawtext(filesource)
		NERlist = NERTagger.tag(words)
		LOClist, TAG1list = LOC_ORG_PERtagger(NERlist)
		TAG2list = CIT_COUtagger(LOClist)
		TAG3list = ANI_SPO_NAT_ENTtagger(words)
		
		ALLlist = [TAG1list,TAG2list,TAG3list]

		writeout(ALLlist, filesource, lines)
		
		NNPlist = read_data(filesource)
		#print(filesource," ",NNPlist)
		FINAL_NNPlist = nnp_checker(NNPlist)
		#print(FINAL_NNPlist,"\n")

		WIKIlinks = []
		for nnp in FINAL_NNPlist:
			ngram = nnp[-1]
			link = link_checker(ngram)
			if link != -1:
				nnp.append(link)
		wiki_writeout(FINAL_NNPlist, lines, filesource)		
		#print(FINAL_NNPlist)
	    

if __name__ == "__main__":
	main()

