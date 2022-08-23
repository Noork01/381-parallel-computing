import sys
from operator import add
from pyspark import SparkConf, SparkContext

# for SparkConf() check out http://spark.apache.org/docs/latest/configuration.html
conf = (SparkConf()
        .setMaster("local")
        .setAppName("20 word count")
        .set("spark.executor.memory", "1g"))
sc = SparkContext(conf=conf)

print("Launch App..")
if __name__ == "__main__":
    print("Initiating main..")

    inputFile = "s3://proj2-input-output/task3_input/pride_prejudice.txt"
    print("Counting words in ", inputFile)
    counts = sc.textFile(inputFile).flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a, b: a + b)\
        .sortByKey(ascending=False)
    counts1 = counts.sortBy(lambda x: x[1], ascending=False)
    counts2 = counts1.take(20)
    #output = counts2.collect()
    for (word, count) in counts2:
        print("%s: %i" % (word, count))
    sc.stop()