import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np

# 3 clusters gave the most reliable results in testing
clusters = 3


# Code from https://www.pyimagesearch.com/2014/05/26/opencv-python-k-means-color-clustering/
def _centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=num_labels)
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    # return the histogram
    return hist


def _plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    start_x = 0
    # loop over the percentage of each cluster and the color of
    # each cluster
    for percent, color in zip(hist, centroids):
        # plot the relative percentage of each cluster
        end_x = start_x + percent * 300
        cv2.rectangle(bar, (int(start_x), 0), (int(end_x), 50),
                      color.astype("uint8").tolist(), -1)
        start_x = end_x

    # return the bar chart
    return bar


def k_means(img, title: str = None):
    """
    :param img: A BGR image.
    :param title: A title for the plot used for debugging.
    :return: The dominant cluster.
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = img.reshape((img.shape[0] * img.shape[1], 3))

    clt = KMeans(clusters)
    clt.fit(img)

    hist = _centroid_histogram(clt)

    if title is not None:
        bar = _plot_colors(hist, clt.cluster_centers_)
        # show our color bart
        plt.figure()
        plt.title(title)
        plt.axis("off")
        plt.imshow(bar)
        plt.show()

    hist_list = hist.tolist()
    return clt.cluster_centers_[hist_list.index(max(hist_list))]
