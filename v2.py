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
import json
from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import ast
import en

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
 'ought', 'shall', 'should', 'will', 'would'] #Add some stuff to aux list

#List to hold all input sentences
sentences= []


contradictory_sentences= []
additive_sentences= []
concluding_sentences= []
emphasis_sentences= []
illustrate_sentences= []
why_sentences= []
when_sentences= []
others= []

qterms= []

sentences_map= {0: contradictory_sentences, 1: additive_sentences, 2: concluding_sentences, 3: emphasis_sentences,
 4: illustrate_sentences, 5: why_sentences, 6: when_sentences}

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


class StanfordNLP:
    def __init__(self):
        self.server = ServerProxy(JsonRpc20(),
                                  TransportTcpIp(addr=("127.0.0.1", 8080)))
    
    def parse(self, text):
        return json.loads(self.server.parse(text))

def coreference():

	global sentences
	global result

	text= ' '.join(sentences)

	nlp = StanfordNLP()
	result = nlp.parse(text)

	# for i in result['coref']:
	# 	for j in i:
	# 		sentences[j[0][1]]= sentences[j[0][1]].replace(j[0][0], j[1][0])

	# # tree= Tree("root", sentences)
	# # t= Tree.fromstring(result['sentences'][0]['parsetree'][0])

	# print sentences


def regex(s):
	return re.compile(s, re.I)

def genRegex():

	global all_discourse
	all_discourse= []
	fp= open("discourse.txt", "r")

	for line in fp:
		line= line.strip("\n").split(".")
		all_discourse.append(line)
	# print all_discourse
	#List of list of regex patterns
	all_discourse= [[regex(k) for k in j] for j in all_discourse]



################################################ Sentensify ########################################################################
#This function is used to tokenize and split into sentences
####################################################################################################################################

def sentensify():
	global sentences

	tokenizer = nltk.data.load('corpora/punkt/english.pickle')
	fp = open("input.txt")
	data = fp.read()
	sentences= tokenizer.tokenize(data)

	coreference()
	cluster()
	#discourse()


def cluster():

	for s in range(len(sentences)):
		for i in range(len(all_discourse)):
			for j in range(len(all_discourse[i])):			
				res= all_discourse[i][j].search(sentences[s])
				if(res):
					try:
						if(res.group()[0] >= 'A' and res.group()[0] <= 'Z'):
							if(all_discourse[i][j].search('Finally,')):
								count= 0
								for k in sentences[s-4:s+1]:
									if(re.search("\bFirst*\b", k, re.I)):
										temp= sentences[s-4-count:s+1]

								count+= 1

							elif(all_discourse[i][j].search('Furthermore,')):
								if(re.search("Further", sentences[s-1], re.I)):
									temp= sentences[s-2: s+1]
								else:
									temp= sentences[s-1: s+1]

							elif(all_discourse[i][j].search('Although')):
								temp= [sentences[s]]

							elif(i <= 4):
								temp= sentences[s-1: s+1]

							else:
								temp= [sentences[s]]

						else:
							temp= [sentences[s]]

						# init= []
						# while(init != temp):
						# 	init= temp
						# 	temp= pronoun(temp, s-len(temp)+1, res.group())

						sentences_map[i].append(temp)

					except:
						print "Exception"

					

	curr= contradictory_sentences+ additive_sentences+ concluding_sentences+ emphasis_sentences+ illustrate_sentences+ why_sentences+ when_sentences
	tmp= []
	for i in curr:
		for j in i:
			tmp.append(j)
	others= list(set(sentences)- set(tmp))

	print "contradictory_sentences= ", contradictory_sentences ,"\n\n"
	print "additive_sentences= ", additive_sentences ,"\n\n"
	print "concluding_sentences= ", concluding_sentences ,"\n\n"
	print "emphasis_sentences= ", emphasis_sentences ,"\n\n"
	print "illustrate_sentences= ", illustrate_sentences ,"\n\n"
	print "why_sentences= ", why_sentences ,"\n\n"
	print "when_sentences= ", when_sentences ,"\n\n"
	print "others= ", others ,"\n\n"

	genContQuestionTerms()
	genContQuestion()
	genConcludingQuestions()
	genwhyQuestions()


def genwhyQuestions():

	qphrase= "Why "

	for line in why_sentences:

		line= ' '.join(line)
		for disc in all_discourse[5]:
			
			res= disc.search(line)
			s= ""
			if(res):

				if("," in line):
					i1= line.index(",")
				else:
					i1= -1

				i2= line.index(res.group())

				if(i1<i2):
					s+= line[i1+1:i2]
				else: 
					s+= line[i2+6: i1]
				
				allw= s.split(" ")
				for i in range(len(allw)): 
					if(allw[i] in aux_list):
						s= allw[i]+ " " +' '.join(allw[:i])+ " " +' '.join(allw[i+1:])
						question= qphrase+ s+ "?"
						print question
						break



def genConcludingQuestions():

	qphrase= "How was it concluded that \""

	for line in concluding_sentences:
		s= ' '.join(line)

		for disc in all_discourse[2]:
			res= disc.search(s)
			if(res):
				q= s.split(res.group())[1]
				break

		print qphrase+ q+ "\"?"

def tokenize(s):

	s= parser.raw_parse_sents((s, ""))
	tree= Tree("root", s)

	for node in tree[0]:
		n= node
		break

	return [(word, tag) for word, tag in n.pos()]

def genContQuestion():

	qphrase= "What contradicts "

	for qt in qterms:
		
		qt= qt.replace(".", "")
		temp= ""

		if("|" in qt):
			temporary= qt.split("|")
			if(len(temporary)== 2):
				np= temporary[0]
				vp= temporary[1]
			else:
				np= temporary[0]
				vp= ""
		else:
			np=""
			vp= qt

		tags= tokenize(np+ " "+vp+ ".")
		# print tags

		flag= 0
		flag2= 0
		for word, tag in tags:


			if(flag== 1 and tag not in "," and tag not in "."):
				temp+= word+ " "

			# # if(flag== 1 and re.search("VB*", tag)):
			# # 	temp+= en.verb.present_participle(word)+ " "
			# # 	flag= 2

			# # elif(flag== 1):
			# # 	temp+= tmp+ " "
			# # 	flag= 2

			# # elif(re.search("DT", tag)):
			# # 	temp+= word+ " "

			# if((re.search("NN*", tag) or re.search("PR*", tag)) and flag2== 0):
			# 	temp+= word+ " "
			# 	flag2= 1

			if(re.search("VB*", tag) and (word not in aux_list or word== "does" or word== "did" or word== "do")and flag==0):
				try:
					temp= en.verb.present_participle(word)+ " "
					flag= 1
				except KeyError as k:
					flag= 0
			
		print qphrase+ np+" " +temp+"?"

def genContQuestionTerms():

	fp= open("targetarg.txt", "r")
	d= fp.read().strip("\n")

	d= ast.literal_eval(d)

	global curr
	for s in contradictory_sentences:		
		for dm in all_discourse[0]:
			res= dm.search(' '.join(s))
			if(res):
				discmark= res.group()
				break
		l= len(s)

		discmark= discmark.replace("\b", "")
		discmark= discmark.replace(",", "")

		details= d[discmark]

		if(l== 1):
			sen= s[0].split(discmark)[details[0]-1]

		else:
			sen= s[details[0]-1]


		#lensen= len(sen.split(' '))

		#sen= parser.raw_parse_sents((' '.join(s), ""))

		sen= sen+ "."
		sen= parser.raw_parse_sents((sen, ""))

		tree= Tree("root", sen)
		curr= ""

		# parent= nodes(tree[0], lensen)
		# print parent

		treegen(tree[0], details[1])


def nodes(tree, l):
	for node in tree:
		if(type(node) is nltk.tree.Tree):
			
			if(len(node.leaves())== l):
				print l, len(node.leaves())
				print node.pos()
				return [(word, tag) for word, tag in node.pos()]
			nodes(node, l)


def treegen(parent, dm):
	for node in parent:
		n1= node
		break

	for node in n1:
		n2= node
		break	
	
	recursive(n2, dm)

def recursive(n2, dm):

	global curr

	if(dm== 2):
		flag= 0
		for node in n2:
			s= ""
			if(node.label()== "S"):
				flag= 1
				for n in node:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()
								break


						tp= ' '.join(n.leaves())+ " "

						if(flag2):
							tp= tp.split(cc)[-1]+ " "

						s+= tp
						

					curr= s

		if(flag== 0):
			if(n2.label()== "S"):
				flag= 1
				for n in n2:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()[0]
								cc= cc.encode("utf-8")
								break

						tp= ' '.join(n.leaves())+ " "
						if(flag2):
							tp= tp.split(cc)[-1]+ " "							

						s+= tp

					curr= s

		curr= curr.encode("utf-8")

		qterms.append(curr)

	else:
		flag= 0
		for node in n2:
			s= ""
			if(node.label()== "S"):
				flag= 1
				for n in node:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()
								break

						tp= ' '.join(n.leaves())+ " "

						if(flag2):
							tp= tp.split(cc)[0]+ " "

						s+= tp

					curr= s
				break

		if(flag== 0):
			if(n2.label()== "S"):
				flag= 1
				for n in n2:
					if(n.label()== 'NP'):
						s+= ' '.join(n.leaves())+ "|"
					if(n.label()== "VP"):
						flag2= 0
						for no in n:
							if(no.label()== 'CC'):
								flag2= 1
								cc= no.leaves()
								break

						tp= ' '.join(n.leaves())+ " "

						if(flag2):
							tp= tp.split(cc)[0]+ " "

						s+= tp

					curr= s

	
		curr= curr.encode("utf-8")

		qterms.append(curr)

def pronoun(sent, i, sw):

	text = nltk.word_tokenize(sent[0])
	tags= nltk.pos_tag(text)

	if(tags[0][1]== "PRP" or (tags[0][1]== "DT" and not (tags[0][1]== "DT" and re.search("NN*", tag[1][1])))):
		sent= [sentences[i-1]]+ sent
		return sent

	return sent

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

genRegex()
sentensify()