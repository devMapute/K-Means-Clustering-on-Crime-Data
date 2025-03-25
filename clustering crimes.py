
"""
This program performs K-Means clustering on crime data from Baltimore. It reads 
crime data from a CSV file, extracts coordinates, and applies the K-Means 
clustering algorithm to group the data into clusters based on their spatial 
proximity. The program uses the Minkowski distance metric (with p=2 for 
Euclidean distance) to calculate distances between points and centroids.
The program includes the following functionalities:
- Reading and preprocessing data from a CSV file.
- Extracting coordinates for clustering.
- Calculating distances using the Minkowski distance formula.
- Initializing random centroids for clustering.
- Iteratively updating centroids based on the mean of points in each cluster.
- Assigning points to clusters based on the nearest centroid.
- Writing the clustering results, including initial and final centroids, 
    iterations, and labeled datasets, to an output file.
- Visualizing the clustering results using a geoplot.
The program is designed to handle up to 500 data points and allows the user to 
specify the number of clusters (k) and the distance metric parameter (p). 
Default values are provided for k (7) and p (2). The results are saved in 
'output.txt', and the clusters are visualized using the geoplot library.
"""

from geoplot import geoplot

# read data from a csv file
def get_data(file_path):
    column_headers = []
    data = []
    with open(file_path, 'r') as data_file:
        column_headers = data_file.readline().strip().split(',')
        
        counter = 0
        for line in data_file:
            if counter == 500:
                break
            row = line.strip().split(',')
            if row[10] != "" and row[11] != "":
                data.append(row)
                counter += 1
            else:
                continue

    return data

# extract coordinates from the data
def get_coords(data):
    coords = []

    for temp in data:
        coord = []
        coord.append(float(temp[10]))
        coord.append(float(temp[11]))
        coords.append(coord)

    return coords

# calculate the minkowski distance between two points
def minkowski_distance(test_point, train_point, p):
    distance = 0
    for i in range(len(test_point)):
        distance += abs(test_point[i] - train_point[i])**p
    distance = distance ** (1/p)
    return distance 

# get initial random points to serve as centroids
def get_points(coords, k):
    index_list = []
    centroids = set()
    seed = 170170

    for _ in range(k):
        seed = (seed * 170171172 + 173) % (2**17) # random number
        index = seed % 500 # get index from 0-499 range
        index_list.append(index)
    
    for index in index_list:
        centroids.add(tuple(coords[index]))

    # centroids = {(-76.61961,39.29164),(-76.66073,39.31828),(-76.60463,39.32736),(-76.66799,39.27466),(-76.60308,39.23302)} #temporary
    
    return centroids

def get_class(distances):
    min_distance = distances[0][1]
    min_class = distances[0][0]

    for distance in distances: 
        if distance[1] < min_distance: # get the class with the minimum distance
            min_distance = distance[1]
            min_class = distance[0]
    
    return min_class

# update centroids based on the mean of points in each cluster
def update_centroids(clusters):
    centroids = set()
    for c_class, points in clusters.items():
        x_0_sum = 0
        x_1_sum = 0

        for point in points:
            x_0_sum += point[0]
            x_1_sum += point[1]
        
        num_points = len(points)
        centroid_x_0 = x_0_sum / num_points
        centroid_x_1 = x_1_sum / num_points

        centroids.add(tuple([centroid_x_0, centroid_x_1]))

    return centroids

# helper function to get the class
def check_class(item):
    return item[0]

# main k-means clustering function
def k_means_clustering(coords, k, p, data):
    centroids = get_points(coords, k)
    initial_centroids = centroids
    prev_centroids = set()
    iteration = 0
    while True:
        if centroids == prev_centroids: # check if centroids have converged
            break
        centroids_class = {} # dictionary to store centroids with their corresponding class
        index = 0
        for centroid in centroids:
            centroids_class[index] = centroid
            index += 1
        
        clusters = {} # dictionary to store points in each cluster
        kmeans_output = [] # list to store the output that will be used for geoplot 
        labeled_dataset = [] # list to store the labeled dataset for output.txt
        for index, point in enumerate(coords):
            distances = []
            for c_class,coord in centroids_class.items():
                distances.append([c_class, minkowski_distance(point,coord,p)]) # get distances from each centroid, p=2 for euclidean distance

            cluster_class = get_class(distances) # get the class of the point based on the minimum distance
            if cluster_class not in clusters: # put point to a cluster
                clusters[cluster_class] = []
            clusters[cluster_class].append(point)
            kmeans_output.append(tuple([cluster_class,point])) 
            labeled_dataset.append([cluster_class, data[index][4], point])
        
        prev_centroids = centroids # store previous centroids
        centroids = update_centroids(clusters) # update centroids

        iteration += 1

    labeled_dataset.sort(key=check_class) # sort labeled dataset by class

    return centroids, initial_centroids, kmeans_output, iteration, labeled_dataset

file_path = "./crime-data.csv"
data = get_data(file_path) # read data from csv
coords = get_coords(data) # extract coordinates

# main
while True:
    try:
        # get user input for k and p values
        # k = int(input("Input k value: "))
        k = 7 # suggested value
        p = 2 # euclidean distance
        break
    except ValueError:
        print("Please enter a valid numerical value.")

# perform k-means clustering
centroids, initial_centroids, kmeans_output, iteration, labeled_dataset = k_means_clustering(coords, k , p, data)

# write output to a file
with open("output.txt", "w") as output_file:
    output_file.write(f"K-Means Clustering Output from {file_path}\n")
    output_file.write(f"K = {k}\n")

    output_file.write("\nInitial Centroids:\n")
    for centroid in initial_centroids:
        output_file.write(f"{centroid}\n")

    output_file.write("\nFinal Centroids:\n")
    for centroid in centroids:
        output_file.write(f"{centroid}\n")
    
    output_file.write(f"\nIterations: {iteration}\n")

    output_file.write("\nLabeled Dataset:\n")
    for temp in labeled_dataset:
        output_file.write(f"{temp[0]} : {temp[1]:<40}{temp[2]}\n")

# plot the results
geoplot(kmeans_output)