
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec

my_palette = {
    "red"      : "#FF595E",
    "yellow"   : "#FFCA3A",
    "green"    : "#8AC926",
    "blue"     : "#1982C4",
    "purple"   : "#6A4C93"
}

def plotFeedback( nlp_df ):

    theme_counts_df = nlp_df.loc[ :, [ "category_box", "theme" ] ].copy()
    theme_counts_df["count"] = 0
    theme_counts_df = theme_counts_df.groupby( [ "category_box", "theme" ], as_index=False ).count()
    theme_counts_df.sort_values( [ "category_box", "count" ], inplace=True, ascending=[ False, True ], ignore_index=True )

    theme_sentiment_df = nlp_df[ nlp_df["SENTIMENT"] == "Positive" ].loc[ :, [ "category_box", "theme" ] ].copy()
    theme_sentiment_df["num_positive"] = 0
    theme_sentiment_df = theme_sentiment_df.groupby( [ "category_box", "theme" ], as_index=False ).count()
    theme_sentiment_df.sort_values( [ "category_box", "num_positive", "theme" ], inplace=True, ascending=[ False, False, True ], ignore_index=True )

    themes_df = theme_counts_df.merge( theme_sentiment_df, how="left", on=[ "category_box", "theme" ] )
    themes_df["num_positive"].fillna( 0, inplace=True ) 
    themes_df["score"] = round( themes_df["num_positive"] / themes_df["count"], 2 )
    themes_df.sort_values( [ "category_box", "score" ], ascending=[ False, False ], inplace=True, ignore_index=True )

    cmap = LinearSegmentedColormap.from_list( "rbg", [ my_palette["blue"], my_palette["green"], my_palette["yellow"] ], N = 256 ) 

    fig_bar = plt.figure( figsize=( 12, 5 ) )
    fig_bar.suptitle( "Sentiment by theme", fontsize = 22 )
    plt.subplots_adjust( top = 0.7 )

    gs = GridSpec( 7, 15, figure=fig_bar )
    axs1 = fig_bar.add_subplot(gs[:4, 0:7])
    axs2 = fig_bar.add_subplot(gs[:4, 8:13])
    cb_axs = fig_bar.add_subplot(gs[6, 4:11])

    axes = [ axs1, axs2 ]
    bars = []
    annotations = []

    for category, axs in zip( themes_df["category_box"].unique(), axes ):
        
        labels = list( themes_df[ themes_df["category_box"] == category ].loc[ :, "theme" ] )
        counts = list( themes_df[ themes_df["category_box"] == category ].loc[ :, "count" ] )
        scores = list( themes_df[ themes_df["category_box"] == category ].loc[ :, "score" ] )
        num_bars  = len( labels )
        positions = np.arange( num_bars )
        colors = [ cmap( score ) for score in scores ]
        
        category_bars = axs.bar( labels, counts, color=colors )
        bars.append( category_bars )
        
        axs.set_yticks([])
        axs.set_ylabel( "Total comments", fontsize="9" )
        axs.tick_params( axis="x", labelsize=8)
        axs.set_title( category, fontsize=18, pad=23 )
        axs.spines["top"].set_visible( False )
        axs.spines["right"].set_visible( False )
        axs.spines["left"].set_visible( False )
        
        category_annotations = []
        for i in range( len( category_bars ) ):
            theme = labels[i]
            comments = list( nlp_df[ ( nlp_df["category_box"] == category ) & ( nlp_df["theme"] == theme ) ].loc[ :, "text" ] )
            annot = axs.annotate( "\n\n".join( comments ), xy=( 0.1, 0.8 ), fontsize="9", xycoords="axes fraction", verticalalignment="top" )
            annot.set_bbox( dict( facecolor="lightgrey", alpha=0.7, edgecolor="lightgrey") )
            annot.set_visible( False )
            category_annotations.append( annot )
        annotations.append( category_annotations )
        
    def contains( bar, event ):
        x = event.xdata;
        y = event.ydata;
        if ( x >= bar.get_x() ) and ( x <= ( bar.get_x() + bar.get_width() ) ) and ( y >= bar.get_y() ) and ( y <= ( bar.get_y() + bar.get_height() ) ):
            return True
        return False

    def hover( event ):
        for i in range( len( axes ) ):
            for j in range( len( bars[i] ) ):
                theme_bar = bars[i][j]
                theme_annot = annotations[i][j]
                if ( event.inaxes == axes[i] ) and contains( theme_bar, event ):
                    theme_annot.set_visible( True )
                else:
                    theme_annot.set_visible( False )

    fig_bar.canvas.mpl_connect( "motion_notify_event", hover )

    cmappable = ScalarMappable( norm=Normalize(0,1), cmap=cmap )
    cbar = plt.colorbar( cmappable, cax=cb_axs, orientation="horizontal" )
    cbar.set_ticks( [ 0.0, 0.5, 1.0 ] )
    cbar.set_ticklabels( [ "Negative", "Neutral", "Positive" ] )
    cb_axs.tick_params( axis="x", labelsize=10)
    cb_axs.invert_xaxis()

    plt.show()
