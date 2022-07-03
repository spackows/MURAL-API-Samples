
# Hierarchical clustering
#
from collections import OrderedDict
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt
from scipy import cluster

def countWords( df, col_name, min_count ):
    all_words = {}
    for index, row in df.iterrows():
        words_arr = row[ col_name ]
        for word in words_arr:
            if word not in all_words:
                all_words[word] = 0
            all_words[word] += 1
    common_words = dict( [ (k,v) for k,v in all_words.items() if v > min_count ] )
    ordered_common_words = OrderedDict( sorted( common_words.items(), key=lambda x:x[1], reverse=True ) )
    return ordered_common_words

def uniqueWords( df, col_name, min_count ):
    words_od = countWords( df, col_name, min_count )
    unique_words = list( words_od.keys() )
    return sorted( unique_words )

def buildWordsMatrix( df, col_name, min_count ):
    unique_words = uniqueWords( df, col_name, min_count )
    labels = []
    matrix = []
    indices_org = []
    omitted_indices = []
    for index, df_row in df.iterrows():
        label_arr = []
        matrix_row = []
        for word in unique_words:
            if word in df_row[ col_name ]:
                label_arr.append( word )
                matrix_row.append( 1 )
            else:
                matrix_row.append( 0 )
        if( len( label_arr ) > 0 ):
            labels.append( " | ".join( label_arr ) )
            matrix.append( matrix_row )
            indices_org.append( index )
        else:
            omitted_indices.append( index )
    return labels, matrix, indices_org, omitted_indices

def addClusterH( df, col_name, Z, labels, indices_org, omitted_indices, height ):
    cutree = cluster.hierarchy.cut_tree( Z, height = height )
    cluster_arr = []
    for i in range( len(cutree) ):
        cluster_num = cutree[i][0]
        label = labels[i]
        index = indices_org[i]
        row = df.iloc[index]
        cluster_arr.append( list( row ) + [ cluster_num, label ] )
    other_cluster_num = int( max( cutree ) + 1 )
    for index in omitted_indices:
        row = df.iloc[index]
        cluster_arr.append( list( row ) + [ other_cluster_num, " | ".join( row[ col_name ] ) ] )
    clusterH_df = pd.DataFrame( cluster_arr, columns = df.columns.tolist() + [ "H_CLUSTER_ID", "LABEL" ] )
    return clusterH_df

def clusterH( df, col_name, height = 1.25 ):
    labels, matrix, indices_org, omitted_indices = buildWordsMatrix( df, col_name, 0 )
    Z = linkage( matrix, "single" )
    plt.figure( figsize=( 5, 8 ) )
    plt.gca().spines["left"].set_visible(False)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    dend = dendrogram( Z,
                       get_leaves=True,
                       orientation="left",
                       labels=labels,
                       leaf_font_size=12,
                       show_leaf_counts=True)
    plt.show()
    clusterH_df = addClusterH( df, col_name, Z, labels, indices_org, omitted_indices, height )
    return clusterH_df.sort_values( [ "H_CLUSTER_ID", "LABEL" ], ignore_index=True )


# K-means clustering
#
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.cluster.vq import whiten

def listDistances( label, matrix, centroid ):
    distances = []
    for i in range( len( label ) ):
        class_index = label[i]
        dist = np.linalg.norm( matrix[i] - centroid[class_index] )
        distances.append( dist )
    return distances

def getKMeansClusters( df, col_name, num_clusters ):
    labels, matrix, indices_org, omitted_indices = buildWordsMatrix( df, col_name, 1 )
    matrix_norm = whiten( matrix )
    centroid, label = kmeans2( matrix_norm, num_clusters )
    distances = listDistances( label, matrix_norm, centroid )
    results = np.asarray( [ list( label ), distances ] ).transpose()
    return results.tolist(), indices_org, omitted_indices

def clusterK( df, col_name, num_clusters ):
    clusters, indices_org, omitted_indices = getKMeansClusters( df, col_name, num_clusters - 1 )
    cluster_arr = []
    for df_index, df_row in df.iterrows():
        cluster_num = num_clusters - 1
        if df_index in indices_org:
            i = indices_org.index( df_index )
            cluster_num = int( clusters[i][0] )
        cluster_arr.append( list( df_row ) + [ cluster_num, " | ".join( df_row[ col_name ] ) ] )
    clusterK_df = pd.DataFrame( cluster_arr, columns = df.columns.tolist() + [ "K_CLUSTER_ID", "LABEL" ] )
    return clusterK_df.sort_values( [ "K_CLUSTER_ID", "LABEL" ], ignore_index=True )


