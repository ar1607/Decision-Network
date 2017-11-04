from decimal import Decimal, ROUND_HALF_UP
import copy, random
jointProbDict = {}
query = []
nodesDict = {}
nodesDict_Copy = None
utilityNode = None
def readFromFile(fname):
	inputArray=[]
	with open(fname) as f:
		inputArray = f.readlines()
	return inputArray

def writeToFile(fname, outputArr):
	x = len(outputArr)-1
	with open(fname, 'w+') as file:
		for i in range(0,x):
			file.write(outputArr[i]+'\n')
		file.write(outputArr[x])

class Node:

	def __init__(self, name, nodeType, parents, children, probMatrix):
		self.name = name #name of the node
		self.nodeType = nodeType  #node type : decision node, chance node or utility node
		self.parents = parents #list of parents of this node in sorted order
		self.children = children #list of children of this node in sorted order
		self.probMatrix = probMatrix #probability matrix of this node; design it as a dicitionary

def hiddenVariablesCalc(varDictList):
	global jointProbDict, nodesDict
	varDictList_Local = copy.deepcopy(varDictList)
	for i in varDictList_Local:
		parentsList = nodesDict[i].parents
		if parentsList==None or len(parentsList)==0:
			continue
		for p in parentsList:
			if p not in varDictList_Local:
				varDictList_Local.append(p)
	varDictList_Local = sorted(varDictList_Local)
	if varDictList_Local==varDictList:
		return varDictList_Local
	else:
		return hiddenVariablesCalc(varDictList_Local)

def hiddenVariablesCalcLocal(varDictList):
	global jointProbDict, nodesDict_Copy
	varDictList_Local = copy.deepcopy(varDictList)
	for i in varDictList_Local:
		parentsList = nodesDict_Copy[i].parents
		if parentsList==None or len(parentsList)==0:
			continue
		for p in parentsList:
			if p not in varDictList_Local:
				varDictList_Local.append(p)
	varDictList_Local = sorted(varDictList_Local)
	if varDictList_Local==varDictList:
		return varDictList_Local
	else:
		return hiddenVariablesCalcLocal(varDictList_Local)

varsLocal = []
pGlobal = []
cGlobal = []
def getLCA(var):
    global nodesDict, varsLocal, pGlobal, cGlobal
    if nodesDict[var].parents==None and nodesDict[var].nodeType=='decision':
		return 1
    if nodesDict[var].parents==None and nodesDict[var].nodeType=='chance':
		return 0
    parentsList = nodesDict[var].parents
    tmp = 0
    for j in range(len(parentsList)):
        if parentsList[j] in varsLocal: return 1
        pGlobal.append(parentsList[j])
        cGlobal.extend(nodesDict[parentsList[j]].children)
        if not set(cGlobal).issubset(set(pGlobal)): return 1
        tmp += getLCA(parentsList[j])
    if tmp == 0:    return 0
    else: return 1

def jointProbabilityCalculator(varDict):
	global jointProbDict, nodesDict, nodesDict_Copy
	if nodesDict_Copy == None:
		nodesDict_Copy = copy.deepcopy(nodesDict)
	res = 1.0
	for key in sorted(varDict.iterkeys()):
		probMatrixDict = nodesDict_Copy[key].probMatrix
		if nodesDict_Copy[key].parents==None or nodesDict_Copy[key].parents==[]:
			if not nodesDict_Copy[key].nodeType=='decision':
				if varDict[key]=='+':
					res*=probMatrixDict['s']
				else:
					res*=(1-probMatrixDict['s'])
		else:
			parentsList = nodesDict_Copy[key].parents
			signStr = ''
			for i in parentsList:
				signStr+=varDict[i]
			if varDict[key]=='+':
				res*=probMatrixDict[signStr]
			else:
				res*=(1-probMatrixDict[signStr])
	return res

def list_difference(a,b):
	b = set(b)
	return [x for x in a if x not in b]

def enumJointProbWithHV(varDict, hiddenVars):
	global nodesDict
	hiddenVars_Local = copy.deepcopy(hiddenVars)
	if len(hiddenVars_Local)==0:
		return jointProbabilityCalculator(varDict)
	varDict_True = copy.deepcopy(varDict)
	varDict_False = copy.deepcopy(varDict)
	current = hiddenVars_Local.pop(0)
 	varDict_True[current] = '+'
	varDict_False[current] = '-'
	return enumJointProbWithHV(varDict_True, hiddenVars_Local) + enumJointProbWithHV(varDict_False, hiddenVars_Local)

def jointProbabilityCalculatorWithHiddenVariables(varDict, hiddenVars=None):
	global nodesDict, nodesDict_Copy, varsLocal, pGlobal, cGlobal
	varsLocal = varDict.keys()
	var = varDict.keys()
	queue = []
	for i in range(len(var)):
		v = var[i]
		if nodesDict[v].parents==None:
			continue
		pGlobal = [v]
		cGlobal = []
		if getLCA(v)==1:
			continue
		else:
			queue.append(v)
	for i in range(len(queue)):
		v = queue[i]
		hvLocal = list_difference(hiddenVariablesCalc(list(v)), list(v))
		nodesDict_Copy[v].probMatrix['s'] = enumJointProbWithHV({str(v):'+'}, hvLocal)
		nodesDict_Copy[v].parents = None
	hv = list_difference(hiddenVariablesCalcLocal(varDict.keys()), varDict.keys())
	return enumJointProbWithHV(varDict, hv)

s_add=0
def expectedUtility(parentDict, varDict, parentDictList):
	global jointProbDict, nodesDict, s_add, utilityNode
	parentDictList_Local = copy.deepcopy(parentDictList)
	if len(parentDictList_Local)==0:
		signStr = ''
		parentsList = utilityNode.parents
		for i in parentsList:
			if i in parentDict:
				signStr+=parentDict[i]
			elif i in varDict:
				signStr+=varDict[i]
		consDict = {}
		consDict.update(parentDict)
		consDict.update(varDict)	
		tmp = jointProbabilityCalculatorWithHiddenVariables(consDict)/jointProbabilityCalculatorWithHiddenVariables(varDict)
		s_add+=tmp
		return tmp*utilityNode.probMatrix[signStr]
	current = parentDictList_Local.pop(0)
	if current in varDict:
		parentDict_Local = copy.deepcopy(parentDict)
		return expectedUtility(parentDict, varDict, parentDictList_Local)
	parentDict_True = copy.deepcopy(parentDict)
	parentDict_False = copy.deepcopy(parentDict)
	parentDict_True[current] = '+'
	parentDict_False[current] = '-'
	return expectedUtility(parentDict_True, varDict, parentDictList_Local) + expectedUtility(parentDict_False, varDict, parentDictList_Local)

expectedUtilityDict={}
def maximumExpectedUtility(qList, qDict):
	global jointProbDict, nodesDict, expectedUtilityDict, s_add, utilityNode
	qList_Local = copy.deepcopy(qList)
	if len(qList_Local)==0:
		s_add=0
		signStr = ''
		for key in qDict:
			signStr+=qDict[key]
		parentDictList = utilityNode.parents
		parentDict = {}
		for j in parentDictList:
			if j not in qDict:
				parentDict.update({j:'+'})
		res = expectedUtility(parentDict, qDict, parentDictList)
		expectedUtilityDict.update({signStr:res})
		return
	current = qList_Local.pop(0)
	qDict_True = copy.deepcopy(qDict)
	qDict_True[current]='+'
	qDict_False = copy.deepcopy(qDict)
	qDict_False[current]='-'
	maximumExpectedUtility(qList_Local, qDict_True)
	maximumExpectedUtility(qList_Local, qDict_False)
	return

def maximumExpectedUtilityWithConditional(qDict, evDict, qList):
	global jointProbDict, nodesDict, expectedUtilityDict, s_add, utilityNode
	qList_Local = copy.deepcopy(qList)
	if len(qList_Local)==0:
		s_add=0
		signStr = ''
		for key in qDict:
			signStr+=qDict[key]
		varDict = {}
		varDict.update(qDict)
		varDict.update(evDict)
		parentDictList = utilityNode.parents
		parentDict = {}
		for j in parentDictList:
			if j not in varDict:
				parentDict.update({j:'+'})
		tmp = expectedUtility(parentDict, varDict, parentDictList)
		res = tmp/s_add
		expectedUtilityDict.update({signStr:res})
		return
	current = qList_Local.pop(0)
	qDict_True = copy.deepcopy(qDict)
	qDict_True[current]='+'
	qDict_False = copy.deepcopy(qDict)
	qDict_False[current]='-'
	evDict_Local = copy.deepcopy(evDict)
	maximumExpectedUtilityWithConditional(qDict_True, evDict_Local, qList_Local)
	maximumExpectedUtilityWithConditional(qDict_False, evDict_Local, qList_Local)
	return

def main():
	inputArray = readFromFile('input.txt')
	i=0
	global query, nodesDict, utilityNode, s_add, expectedUtilityDict, nodesDict_Copy
	while i<len(inputArray):
		if '*' not in inputArray[i]:
			xx = inputArray.pop(i).split('\n')[0]
			query.append(xx)
		else:
			inputArray.pop(i)
			break
	#now we are left with the inputArray containing the node specification
	while len(inputArray)!=0:
		nodePlaceholder = []
		i=0
		#translating one node into a bayesian network node
		while i<len(inputArray):
			if '*' not in inputArray[i]:
				nodePlaceholder.append(inputArray.pop(i))
			else:
				inputArray.pop(i)
				break
		#now we have reached a line containing a '*', thus we can move forward with creating a node for the obtained lines of data
		#we start with initializing the probMatrix dictionary
		probMatrix = {}
		#finding out the name of this node & whether or not it has any parents
		firstLine = nodePlaceholder[0].split()
		if len(firstLine)==1:
			name = firstLine[0]
			parents = []
			children = []
			#if the node is a decision node, it has no parents and no probMatrix
			if 'decision' in nodePlaceholder[1]:
				nodeType = 'decision'
				probMatrix = None
				parents = None
			#if the node is a chance node, it will have one line after the name which gives us the probability of this node when this node is True,
			#independent of any other node (as it doesn't have any parents). Thus we create a dictionary storing the probability value for when
			#the node is True and when it is False.
			else:
				nodeType = 'chance'
				prob = float(nodePlaceholder[1])
				probMatrix.update({'s':prob})
			#now we create the node for this node, and we add the newly created node in the dictionary nodesDict
			node = Node(name, nodeType, parents, children, probMatrix)
			nodesDict.update({name : node})
		#if the node had dependencies on other nodes, i.e., it has some parent nodes
		else:
			firstLine = nodePlaceholder[0].split() 
			name = firstLine.pop(0)
			firstLine.pop(0)
			if name=='utility':
				nodeType = 'utility'
				children = None
			else:
				nodeType = 'chance'
				children = []
			parents = sorted(firstLine)
			nodePlaceholder.pop(0)
			#loop to populate the probMatrix dicitionary
			for j in nodePlaceholder:
				current = j.split()
				val = float(current[0]) #probability value is stored here
				boolVals = [x for (y,x) in sorted(zip(firstLine, current[1:]))] #array containing the signs as per the sorted variables
				boolValsString = ''.join(boolVals) #string containing the signs as per the sorted variables
				probMatrix.update({boolValsString : val})
			#now we have the probMatrix populated as per the sorted parents list
			#now we create the node for this node, and we add the newly created node in the dictionary nodesDict
			node = Node(name, nodeType, parents, children, probMatrix)
			#if it is a utility node, store it in the utilityNode variable
			if name=='utility':
				utilityNode = node
			#else, if the node is not a utility node, we add the node to the dictionary nodesDict
			else:
				nodesDict.update({name : node})
			#now update the children list for the parents of this node
			for p in parents:
				nodesDict[p].children.append(name)

	outputArr = []
	for i in query:
		yy = i.split('(')
		zz = yy[1].split(')') #removing the closing brace
		internalStr = zz[0] #this is the internal string, i.e the string of variables inside the brace
		func = yy[0]
		if func=='P':
			#probability
			if '|' in internalStr:
				#conditionality exists
				nodesDict_Copy = None
				nodesDict_Copy = copy.deepcopy(nodesDict)
				qDict = {}
				evDict = {}
				aa = internalStr.split('|')
				q = aa[0].split(',')
				e = aa[1].split(',')
				for z in q:
					bb = z.split('=')
					k = bb[0].strip()
					v = bb[1].strip()
					qDict.update({k:v})
				for z in e:
					bb = z.split('=')
					k = bb[0].strip()
					v = bb[1].strip()
					evDict.update({k:v})
				varDict = {}
				varDict.update(qDict)
				varDict.update(evDict)
				num = jointProbabilityCalculatorWithHiddenVariables(varDict)
				hv = list_difference(hiddenVariablesCalcLocal(evDict.keys()), evDict.keys())
				den = enumJointProbWithHV(evDict, hv)
				tmp = Decimal(str(num/den))
				output = str(Decimal(tmp.quantize(Decimal('0.01'))))
				outputArr.append(output.ljust(4, '0'))
				nodesDict_Copy = None

			else:
				#conditionality doesn't exist
				nodesDict_Copy = None
				nodesDict_Copy = copy.deepcopy(nodesDict)
				lit = internalStr.split(', ') #split the string str on ', ' to get the list of literals
				varDict = {}
				for z in lit:
					aa = z.split('=')
					k = aa[0].strip()
					v = aa[1].strip()
					varDict.update({k:v})
				#if the number of variables here in the varDict is the same as the number of variables in the nodesDict, we simply
				#calculate the Joint Probability
				if len(varDict)==len(nodesDict):
					tmp = Decimal(str(jointProbabilityCalculator(varDict)))
					output = str(Decimal(tmp.quantize(Decimal('0.01'))))
					outputArr.append(output.ljust(4, '0'))
				#otherwise, we will calculate the Joint Probability summed over the hidden variables 
				else:
					tmp = Decimal(str(jointProbabilityCalculatorWithHiddenVariables(varDict)))
					output = str(Decimal(tmp.quantize(Decimal('0.01'))))
					outputArr.append(output.ljust(4, '0'))

				nodesDict_Copy = None

		elif func=='EU':
			#Expected Utility
			s_add=0
			if '|' in internalStr:
				nodesDict_Copy = None
				nodesDict_Copy = copy.deepcopy(nodesDict)
				#conditionality exists
				qDict = {}
				evDict = {}
				aa = internalStr.split('|')
				q = aa[0].split(',')
				e = aa[1].split(',')
				for z in q:
					bb = z.split('=')
					k = bb[0].strip()
					v = bb[1].strip()
					qDict.update({k:v})
				for z in e:
					bb = z.split('=')
					k = bb[0].strip()
					v = bb[1].strip()
					evDict.update({k:v})
				parentsList = utilityNode.parents
				parentDict = {}
				for i in parentsList:
					if i not in evDict:
						parentDict.update({i:'+'})
				varDict = {}
				varDict.update(qDict)
				varDict.update(evDict)
				tmp = str(int(round(expectedUtility(parentDict, varDict, parentsList)/s_add, 0)))
				nodesDict_Copy = None

			else:
				#conditionality doesn't exist
				nodesDict_Copy = None
				nodesDict_Copy = copy.deepcopy(nodesDict)
				qDict={}
				evDict = {}
				aa = internalStr.split(',')
				for z in aa:
					bb = z.split('=')
					k = bb[0].strip()
					v = bb[1].strip()
					evDict.update({k:v})
				parentsList = utilityNode.parents
				for i in parentsList:
					if i not in evDict:
						qDict.update({i:'+'})
				tmp = str(int(round(expectedUtility(qDict, evDict, parentsList), 0)))
				nodesDict_Copy = None

			outputArr.append(tmp)
			
		elif func=='MEU':
			#Maximum Expected Utility
			expectedUtilityDict = {}
			s_add = 0
			if '|' in internalStr:
				#conditionality exists
				nodesDict_Copy = None
				nodesDict_Copy = copy.deepcopy(nodesDict)
				qList = []
				evDict = {}
				aa = internalStr.split('|')
				q = aa[0].split(',')
				e = aa[1].split(',')
				for z in q:
					bb = z.strip()
					qList.append(bb)
				for z in e:
					bb = z.split('=')
					k = bb[0].strip()
					v = bb[1].strip()
					evDict.update({k:v})
				qDict = {}
				for i in qList:
					qDict.update({i:'+'})
				maximumExpectedUtilityWithConditional(qDict, evDict, qList)
				tmp_val = max([expectedUtilityDict[_] for _ in expectedUtilityDict])
				for key in expectedUtilityDict:
					if expectedUtilityDict[key]==tmp_val:
						tmp_key = key 
				tmp = ''
				for i in tmp_key:
					tmp+=i
					tmp+=' '
				tmp+=str(int(round(tmp_val, 0)))
				nodesDict_Copy = None

			else:
				nodesDict_Copy = None
				nodesDict_Copy = copy.deepcopy(nodesDict)
				qList = []
				aa = internalStr.split(',')
				for z in aa:
					bb = z.strip()
					qList.append(bb)
				qDict = {}
				for i in qList:
					qDict.update({i:'+'})
				maximumExpectedUtility(qList, qDict)
				tmp_val = max([expectedUtilityDict[_] for _ in expectedUtilityDict])
				for key in expectedUtilityDict:
					if expectedUtilityDict[key]==tmp_val:
						tmp_key = key 
				tmp = ''
				for i in tmp_key:
					tmp+=i
					tmp+=' '
				tmp+=str(int(round(tmp_val, 0)))
				nodesDict_Copy = None

			outputArr.append(tmp)

	writeToFile('output.txt', outputArr)
	print outputArr
	print ' #### : ', expectedUtilityDict

main()