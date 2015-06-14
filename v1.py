''' 
Automatic Question Generation 

'''


############################################ Imports #############################################################################

import nltk
import nltk.data
from nltk.tree import Tree
import os
import stanford
from nltk.stem.snowball import SnowballStemmer
import re

#################################################################################################################################


#Setting stanford environment variables

os.environ['STANFORD_PARSER'] = '/home/anirudh/jars'
os.environ['STANFORD_MODELS'] = '/home/anirudh/jars'


############################################# Class initializations ############################################################

stemmer = SnowballStemmer("english")
parser = stanford.StanfordParser(model_path="/home/anirudh/englishPCFG.ser.gz")

################################################################################################################################



############################################ Global Initializations #############################################################


#List of auxiliary verbs
aux_list= ['am', 'are', 'is', 'was', 'were', 'can', 'could', 'does', 'do', 'did', 'has', 'had', 'may', 'might', 'must', 'need',
 'ought', 'shall', 'should', 'will', 'would']

#List to hold all input sentences
sentences= []

#List of all discourse markers
discourse_markers= ['because', 'as a result', 'since', 'when', 'although', 'for example', 'for instance']

#Dictionary to hold sentences corresponding to respective discourse markers
disc_sentences= {}

#Remaining sentences which do not have discourse markers (To be used later to generate other kinds of questions)
nondisc_sentences= []

#Different question types possible for each discourse marker
qtype= {'because': ['Why'], 'since': ['When', 'Why'], 'when': ['When'], 'although': ['Yes/No'], 'as a result': ['Why'], 
'for example': ['Give an example where'], 'for instance': ['Give an instance where'], 'to': ['Why']}

#The argument which forms a question
target_arg= {'because': 1, 'since': 1, 'when': 1, 'although': 1, 'as a result': 2, 'for example': 1, 'for instance': 1, 'to': 1}

##################################################################################################################################




################################################ Sentensify ########################################################################
#This function is used to tokenize and split into sentences
####################################################################################################################################

def sentensify():
	global sentences
	tokenizer = nltk.data.load('corpora/punkt/english.pickle')
	fp = open("input.txt")
	data = fp.read()
	sentences= tokenizer.tokenize(data)

	discourse()


################################################# generate_question ################################################################
#Function used to generate the questions from sentences which have already been pre-processed.
####################################################################################################################################

def generate_question(tree, question_part, type):

	''' Tree -> Input tree
		question_part -> Part of input sentence which forms a question
		type-> The type of question (why, where, etc)
	'''

	#Remove full stop and make first letter lower case
	question_part= question_part[0].lower()+ question_part[1:]
	if(question_part[-1]== '.'):
		question_part= question_part[:-1]

	question= ""
	aux_verb= False
	res= None

	#Find out if auxiliary verb already exists
	for i in range(len(aux_list)):
		if(aux_list[i] in question_part.split()):
			aux_verb= True
			pos= i
			break

	#If it exists
	if(aux_verb):

		text = nltk.word_tokenize(question_part)
		tags= nltk.pos_tag(text)
		question_part= ""

		for word, tag in tags:
			#Break the sentence after the first non-auxiliary verb

			if(re.match("VB*", tag) and word not in aux_list):
				question_part+= word
				break
			question_part+= word+ " "

		question= question_part.split(" "+ aux_list[pos])
		question= [aux_list[pos]+ " "]+ question


		#If Yes/No, no need to introduce question phrase
		if(type== 'Yes/No'):
			question+= ['?']

		else:
			question= [type+ " "]+ question + ["?"]

		question= ''.join(question)

	#If auxilary verb does ot exist, it can only be some form of verb 'do'
	else:

		aux= None
		text = nltk.word_tokenize(question_part)
		tags= nltk.pos_tag(text)

		comb= ""

		'''There can be following combinations of nouns and verbs:
			NN and VBZ  -> Does
			NNS(plural) and VBP -> Do
			NN and VBN -> Did
			NNS(plural) and VBN -> Did
		'''
		
		for tag in tags:
			if(tag[1]== 'NN'):
				comb= 'NN'

			elif(tag[1]== 'NNS'):
				comb= 'NNS'

			if(res== None):
				res= re.match(r"VB*", tag[1])
				if(res):

					#Break the sentence after the first non-auxiliary verb
					question_part= question_part[:question_part.index(tag[0])+len(tag[0])]

					#Stem the verb
					question_part= question_part.replace(tag[0],stemmer.stem(tag[0]))

				res= re.match(r"VBN", tag[1])

		if(comb== 'NN'):
			aux= 'does'
		elif(comb== 'NNS'):
			aux= 'do'

		if(res and res.group()== 'VBN'):
			aux= 'did'

		if(aux):

			if(type== 'Yes/NO'):
				question= aux+ " "+ question_part+ "?"

			else:
				question= type+" "+ aux+ " "+ question_part+ "?"

	print question 



######################################################### discourse ################################################################
#Function used to pre-process sentences which have discourse markers in them
####################################################################################################################################

def discourse():

	temp= []
	target= ""

	for i in range(len(sentences)):
		maxLen= 9999999
		val= -1
		for j in discourse_markers:
			tmp= len(sentences[i].split(j)[0].split(' '))	

			#To get valid, first discourse marker.		
			if((j in sentences[i].split()) and tmp>= 3 and tmp< maxLen):
				maxLen= tmp
				val= j

		if(val!= -1):

			#To initialize a list for every new key
			if(disc_sentences.get(val, 'empty')== 'empty'):
				disc_sentences[val]= []

			disc_sentences[val].append(sentences[i])
			temp.append(sentences[i])


	nondisc_sentences= list(set(sentences)- set(temp))

	# dependencies = self.parser.parseToStanfordDependencies(disc_sentences[0])
	# print dependencies

	#parser = stanford.StanfordParser(model_path="/home/anirudh/jars/englishPCFG.ser.gz")

	#print disc_sentences['when'][0]

	for k, v in disc_sentences.items():
		for val in range(len(v)):

			#Parse each sentence which converts it into a tree along with its POS
			sent = parser.raw_parse_sents((disc_sentences[k][val], ""))
			t= []
			for line in sent:
				for s in line:
					t.append(s)

			#Get the tree
			tree= Tree("root", t)

			#Split the sentence on discourse marker and identify the question part
			question_part= disc_sentences[k][val].split(k)[target_arg[k]-1]

			generate_question(tree, question_part, qtype[k][0])

	# for k, v in disc_sentences.items():
	# 	arg= target_arg[k]-1
	# 	for val in v:
	# 		target= val.split(k)[arg]

	# 		text = nltk.word_tokenize(target)

	# 		print nltk.pos_tag(text)

sentensify()