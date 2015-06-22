import os
import stanford
from nltk.tree import Tree
import ast

os.environ['STANFORD_PARSER'] = '/home/anirudh/jars'
os.environ['STANFORD_MODELS'] = '/home/anirudh/jars'

parser = stanford.StanfordParser(model_path="/home/anirudh/englishPCFG.ser.gz")
sentences = parser.raw_parse_sents(("Increase of pavement area not only lessens the amount of water vapour that transpires back from the vegetation.", ""))

# Increase of pavement area not lonely lessens the amount of water vapour that transpires back from the vegetation
# Tension is an external force and if it did do work upon the pendulum bob it would indeed serve to change the total mechanical energy of the bob.
# All these not only affect the soil ecology,
# The force of gravity acts in a downward direction and does work upon the pendulum bob.

for line in sentences:
    for sentence in line:
        sentence.draw()


tree= Tree("root", sentences)
curr= ""

def treegen(parent):
	for node in parent:
		n1= node
		break

	# for node in n1:
	# 	n2= node
	# 	break	
	
	recursive(n1)

def recursive(n2):

	global curr

	fp= open("targetarg.txt", "r")
	d= fp.read().strip("\n")

	d= ast.literal_eval(d)

	

	for node in n2:
		s= ""
		if(node.label()== "S"):
			for n in node:
				if(n.label()== 'NP'):
					s+= ' '.join(n.leaves())+ " "
				if(n.label()== "VP"):
					s+= ' '.join(n.leaves())+ "."

				curr= s
		curr= curr.encode("utf-8")

treegen(tree[0])

print curr

# docs = []

# for subtree in tree.subtrees(filter=lambda t: t.label() == 'Proper'):
#     docs.append(" ".join([a for (a,b) in subtree.leaves()]))

# # print docs

# l= tree.leaves()

# for i in l[0]:
# 	print i[1]


# for k in tree.subtrees():
# 	for i in k:
# 		for j in i:
# 			print j



