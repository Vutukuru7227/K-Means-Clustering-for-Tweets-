import json
import sys

num_clusters	= 25

tweet_dict = {}
seed_dict = {}
final_cluster = {}
new_centroids = {}


def sse(clusters, centroid_values, tweet_dict):
    result = 0
    for cluster in clusters:
        for tweet in clusters[cluster]:
            result += jaccard_distance(tweet_dict[tweet], tweet_dict[centroid_values[cluster]]) ** 2
    return result


def recalculateCentroid(cluster, tweet_data):
    centroid = cluster[0]
    min_distance = 1
    for tweet in cluster:
        total_distance = 0
        for tweet2 in cluster:
            total_distance = total_distance + jaccard_distance (tweet_data[tweet],tweet_data[tweet2])
            mean_distance = total_distance*1.0/len(cluster)
            if mean_distance < min_distance:
                min_distance = mean_distance
                centroid = tweet
    return centroid

def jaccard_distance(centroid_tweet, input_tweet):

    seta = set (centroid_tweet)
    setb = set (input_tweet)

    bucket_union = len (seta.union (setb))
    bucket_intersect = len (seta.intersection (setb))
    return 1.0 - bucket_intersect*1.0/bucket_union


def writeClusters(seed_dict, tweet_dict):
    clusters = {}
    cluster  = 1
    print(seed_dict)
    for index in range (len(seed_dict)):
        clusters[index] = []
    for tweet_id in tweet_dict:
        min_jaccard_dist = 1
        cluster		 = 1
        for seed in seed_dict:
            dist_to_centroid = 1
            dist_to_centroid = jaccard_distance (tweet_dict [str (seed_dict [seed])],tweet_dict [tweet_id])
            if dist_to_centroid < min_jaccard_dist:
                min_jaccard_dist = dist_to_centroid
                cluster = seed
        clusters[cluster].append(tweet_id)
    return clusters


if len(sys.argv) >= 5:

    num_clusters = int(sys.argv[1])
    seedFile = sys.argv[2]
    dataFile = sys.argv[3]
    outputFile = sys.argv[4]

elif len(sys.argv) == 4:
    print("Default Number of Clusters : 25")
    num_clusters = 25
    seedFile = sys.argv[1]
    dataFile = sys.argv[2]
    outputFile = sys.argv[3]

with open (dataFile, 'r') as file:

    data = file.readlines()
    for line in data:
        if (len (line) > 0):
            parsed_json = json.loads (line)
            tweet_dict [str (parsed_json ['id'])] = parsed_json ['text']

with open(seedFile, 'r') as file:

    data = file.read ().rsplit (',\n')
    if (len (data) != num_clusters):
        print("Centroids count mismatch")
        sys.exit (1)

    idx = 0
    for seed in data:
        seed_dict [idx] = seed

        idx = idx + 1
    print(seed_dict)

while True:
    clusters = writeClusters(seed_dict, tweet_dict)
    for cluster in clusters:
        new_centroids[cluster] = recalculateCentroid (clusters[cluster], tweet_dict)
    if new_centroids == seed_dict:
        print("SSE: " + str(sse(clusters, new_centroids, tweet_dict)))
        break
    else:
        seed_dict	= new_centroids

fileToOutput = open(outputFile, 'w')
fileToOutput.write("SSE Value: ")
fileToOutput.write(str(sse(clusters, new_centroids, tweet_dict)))
fileToOutput.write("\n\nClusters:\n")

for cluster in clusters:

    fileToOutput.write(str(cluster))
    fileToOutput.write("\t")
    for tweet_id in clusters[cluster]:
        fileToOutput.write(tweet_id)
        fileToOutput.write(", ")
    fileToOutput.write("\n")