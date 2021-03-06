import pandas as pd
import numpy as np
subreddits = ['suicidewatch-sample', 'depression-sample']
subreddits.sort()


def main(ngram_range=(1,2)):
	import ml
	import numpy
	import itertools
	import pickle
	import os
	import content
	fname = "combinations-10fold.pickle"
	combinations = list(itertools.combinations(subreddits, 2))

	for combination in combinations:
		
		if os.path.isfile(fname):
			f = open(fname, "r")
			rs = pickle.load(f)
			f.close()
		else:
			rs = {}

		if combination[0] in rs.keys():
			if combination[1] in rs[combination[0]].keys():
				print combination, "already exists, skipping..."
				continue

		print "doing", combination[0], "-", combination[1]
		df1 = pd.read_pickle(combination[0] + ".pickle")
		df1 = df1.reset_index()
		df1['text'] = df1.apply(content.getTextFromRecord, axis=1)
		df1 = df1.reindex(numpy.random.permutation(df1.index))
		df2 = pd.read_pickle(combination[1] + ".pickle")
		df2 = df2.reset_index()
		df2['text'] = df2.apply(content.getTextFromRecord, axis=1)
		df2 = df2.reindex(numpy.random.permutation(df2.index))
		# keep only posts, keep only the text column
		df1 = df1[df1['parent_id'].astype(str)=='nan']
		df1 = df1.dropna(subset=['text'])
		df2 = df2[df2['parent_id'].astype(str)=='nan']
		df2 = df2.dropna(subset=['text'])

		results = []
		print "choosing min from", len(df1), len(df2)
		m = min(len(df1), len(df2))
		for i in range(0,10):
			df1_min = df1.reindex(numpy.random.permutation(df1.index)).head(m)	
			df2_min = df2.reindex(numpy.random.permutation(df2.index)).head(m)	

			data = ml.getData(df1_min, df2_min)
			print "got", len(data), "records...training"
			pipeline = ml.bagOfWords(ngram_range=ngram_range)
			pipeline, score = ml.evaluate(pipeline, data=data, getScore=True)
			results.append(score)

		print "RESULTS:", combination, results
		if combination[0] not in rs.keys():
			rs[combination[0]] = {}
		rs[combination[0]][combination[1]] = results
		
		f = open(fname, "w")
		pickle.dump(rs, f)
		f.close()
		print "finished", combination

def readResults(deviations=False):
	df = pd.read_pickle("combinations-10fold.pickle")
	df = pd.DataFrame(df)
	for column in df.columns:
		for index in df.index:
			tmp = df[column][index]
			if tmp is None:
				continue
			if deviations:
				df[column][index] = np.std(tmp)
			else:
				df[column][index] = np.mean(tmp)
	return df