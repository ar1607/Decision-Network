# Decision-Network

##CSCI 561: Foundations of Artificial Intelligence
##Homework #3: Decision Network

A decision network uses a Directed Acyclic Graph (DAG) to represent a set of random variables and their conditional dependencies within a probabilistic model, while a decision network extends the Bayesian network to include decision nodes and utility nodes. There are three types of nodes: Rectangles represent decision nodes, Ovals represent chance nodes, and Diamonds represent utility nodes. In this assignment, you will write code to perform inference in Decision Networks of discrete variables.

You will be given a decision network, which may have several decision nodes, several chance nodes, and at most one utility node. You will be asked to answer queries using the given network:
Calculate a specific joint, marginal, or conditional probability.
Calculate the expected utility of a particular decision, or determine the decision with the maximum expected utility.

