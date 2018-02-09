
#Import the necessay packages

import sys  
import os
import nltk
import re
from nltk.tokenize import word_tokenize
import lucene
from os import path, listdir
#from java.io import File
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.util import Version
from org.apache.lucene.store import RAMDirectory, SimpleFSDirectory
import time

# Indexer imports:
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
# from org.apache.lucene.store import SimpleFSDirectory

# Retriever imports:
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser

# ---------------------------- global constants ----------------------------- #

BASE_DIR = path.dirname(path.abspath(sys.argv[0]))
INPUT_DIR = BASE_DIR + "/IR_Assignment1/alldocs/"


"""
This method returns a document which afterwards can be added to the IndexWriter.
"""
def create_document(file_name):
	path = INPUT_DIR+file_name # assemble the file descriptor
	file = open(path) # open in read mode
	doc = Document() # create a new document
	# add the title field
	doc.add(StringField("title", input_file, Field.Store.YES))
	# add the whole book
	doc.add(TextField("text", file.read(), Field.Store.YES))
	file.close() # close the file pointer
	return doc



# Initialize lucene and the JVM
lucene.initVM()

# Create a new directory. As a SimpleFSDirectory is rather slow ...
directory = RAMDirectory() # ... we'll use a RAMDirectory!
#directory = SimpleFSDirectory(File("lucene_index/"))
#directory = SimpleFSDirectory("IR_Assignment1/fd")

# Get and configure an IndexWriter
analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
analyzer = LimitTokenCountAnalyzer(analyzer, 250000)
config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)

writer = IndexWriter(directory, config)

#print "Number of indexed documents: %d\n" % writer.numDocs()

preprocess_start_time = time.time()

for input_file in listdir(INPUT_DIR): # iterate over all input files
	#print "Current file:", input_file
	doc = create_document(input_file) # call the create_document function
	writer.addDocument(doc) # add the document to the IndexWriter

#print "\nNumber of indexed documents =  %d" % writer.numDocs()
writer.close()

preprocess_end_time = time.time()

output_file = open("part3_lucene_time_calc.txt","a")

output_file.write("Lucene Preprocessing time (Indexing) = "+str(preprocess_end_time-preprocess_start_time)+" secs\n")

output_file.close()

print "Indexing completed \n"


"""
Asks the user for query strings and will show the corresponding result
"""
def search_loop(searcher, analyzer):

	#opening the query file

	queries = open("IR_Assignment1/query.txt",'r')

	#reading every query from the input file
	for command in queries:

		temp_q = command

		print("Query = "+str(command)+"\n")

		x = word_tokenize(temp_q)

		query_no = int(x[0])

		query = QueryParser(Version.LUCENE_CURRENT, "text", analyzer).parse(command)
		
		query_start_time = time.time()

		# retrieving top 50 results for each query
		scoreDocs = searcher.search(query, 50).scoreDocs

		query_end_time = time.time()

		search_time = query_end_time - query_start_time

		print("Time taken = "+str(search_time)+"\n")
		print("No of matches ="+str(len(scoreDocs))+"\n")

		#writing time calculation to the file
		output_file1 = open("lucene_time_calc.txt","a")

		output_file1.write(str(query_no)+"  Query search time = "+str(search_time)+" secs\n")

		output_file1.close()

		# writing output to the file
		output_file2 = open("lucene_output.txt","a")

		for scoreDoc in scoreDocs:
			doc = searcher.doc(scoreDoc.doc)
			print doc.get("title")#, 'name:', doc.get("name")
			temp_str = str(doc.get("title"))
			output_file2.write(str(query_no)+" "+temp_str+"\n")

		output_file2.close()	


	#Closing the queries file
	queries.close()



#main function
if __name__ == '__main__':  

	# Create a searcher for the above defined Directory
	searcher = IndexSearcher(DirectoryReader.open(directory))

	# Create a new retrieving analyzer
	analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)

	# ... and start searching!
	search_loop(searcher, analyzer)

