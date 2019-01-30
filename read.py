from PIL import Image
import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import random
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

def standardize_data(matrix):
    mean = np.mean(matrix, axis=0)
    std = np.std(matrix, axis=0, ddof=1)
    return (matrix - mean) / std

def get_k_eig(cov):
    w, v = LA.eig(cov)
    eig_sum = np.sum(w)
    idx = np.argsort(w)[::-1]

    projection_matrix = []
    k_sum = 0
    for i in idx:
        eig_vec = v[:,i]
        projection_matrix.append(eig_vec)

        k_sum += w[i]
        if (k_sum / eig_sum) > 0.95:
            break

    return np.array(projection_matrix).transpose()

def project(cov, k):
    w, v = LA.eig(cov)
    idx = np.argsort(w)[::-1][0:k]

    projection_matrix = []
    for i in idx:
        eig_vec = v[:,i]
        projection_matrix.append(eig_vec)

    return np.array(projection_matrix).transpose()

def display_pca(results, cov):
    projection_matrix = project(cov, 2)
    z = np.matmul(results, projection_matrix)
    plt.scatter(z[:,0], z[:,1])
    plt.show()

def convert_to_img(vector):
    vector -= vector.min()
    vector /= vector.max()/255.0
    uint8 = np.uint8(vector).reshape((40,40))
    return Image.fromarray(uint8)

def display_pc1(results, cov):
    projection_matrix = get_k_eig(cov)
    pc1 = projection_matrix[:,0]
    img = convert_to_img(pc1)
    plt.imshow(img)
    plt.show()

def reconstruct_face(results, cov):
    projection_matrix = get_k_eig(cov)
    z = np.matmul(results, projection_matrix)
    obj1 = z[0]
    reconstruction = np.matmul(obj1, projection_matrix.transpose())
    img = convert_to_img(reconstruction)
    plt.imshow(img)
    plt.show()

results = []
for root, dirs, files in os.walk("./yalefaces/yalefaces/"):
    for name in files[1:]:
        filename = os.path.join(root, name)
        im = Image.open(filename).resize((40, 40))
        results.append(list(im.getdata()))

def determine_cluster(obs, ref_vecs):
    min = LA.norm(obs - ref_vecs[0])
    cluster = 0

    #TODO: double check this computes Euclidian
    for i in range(1, len(ref_vecs)):
        distance = LA.norm(obs - ref_vecs[i])

        if distance < min:
            min = distance
            cluster = i

    return cluster

def get_color(index):
    color = {
        0: 'r',
        1: 'b',
        2: 'g',
        3: 'y',
        4: 'c',
        5: 'm',
        6: 'k'
    }[index]

    return color

def compute_clusters(data, reference_vectors, iteration, k):
    clusters = [ [] for _ in range(k)]

    for obs in data:
        index = determine_cluster(obs, reference_vectors)

        #color = get_color(index)
        clusters[index].append(obs)
        #plt.scatter(obs[0], obs[1], c=color, marker='x', s=10)

    #for i, vec in enumerate(reference_vectors):
    #    color = get_color(i)
    #    plt.scatter(vec[0], vec[1], c=color, marker="o", s=80)

    return clusters

def plot_kmeans(clusters, reference_vectors, iteration):
    plt.figure(iteration)
    for i, cluster in enumerate(clusters):
        color = get_color(i)
        for obs in cluster:
            plt.scatter(obs[0], obs[1], c=color, marker='x', linewidths=1, s=10)

    for i, vec in enumerate(reference_vectors):
        color = get_color(i)
        plt.scatter(vec[0], vec[1], c=color, marker="o", s=80, edgecolors='k')

def compute_reference_vectors(iteration, clusters):
    reference_vectors = []

    for i, cluster in enumerate(clusters):
        new_ref = np.sum(cluster, axis=0) / len(cluster)
        reference_vectors.append(new_ref)

    return reference_vectors


def myKMeans(data, k):
    num_obs = data.shape[0]
    random.seed(0)
    rand_inds = random.sample(range(0, num_obs), k)

    reference_vectors = []

    for i in rand_inds:
        reference_vectors.append(data[i])

    reference_vectors = np.array(reference_vectors)
    clusters = np.array(compute_clusters(data, reference_vectors, 1, k))
    plot_kmeans(clusters, reference_vectors, 1)

    iteration = 1
    while True:

        new_reference_vectors = np.array(compute_reference_vectors(iteration, clusters))
        change = np.sum(np.abs(reference_vectors - new_reference_vectors))

        if change < (2 ** -23):
            break

        clusters = np.array(compute_clusters(data, new_reference_vectors, iteration, k))
        plot_kmeans(clusters, reference_vectors, iteration)

        iteration += 1
        reference_vectors = new_reference_vectors

    plt.show()







results = np.array(results)
results = standardize_data(results)
cov = np.cov(results, rowvar=False)

#display_pca(results, cov)
#display_pc1(results, cov)
#reconstruct_face(results, cov)

projection_matrix = project(cov, 2)
z = np.matmul(results, projection_matrix)
myKMeans(z, 2)
