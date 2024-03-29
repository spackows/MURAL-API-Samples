
import re
import pandas as pd
import watson_nlp
from watson_nlp.toolkit import predict_document_sentiment


syntax_model = watson_nlp.load( watson_nlp.download( "syntax_izumo_en_stock" ) )
sentiment_model = watson_nlp.load( watson_nlp.download( "sentiment_sentence-bert_multi_stock" ) )
    
    
def analyzeComment( comment ):
    syntax_result = syntax_model.run( comment )
    sentiment_result  = sentiment_model.run_batch( syntax_result.get_sentence_texts(), syntax_result.sentences )
    document_sentiment = predict_document_sentiment( sentiment_result, sentiment_model.class_idxs )
    sentiment_dict = document_sentiment.to_dict()
    sentiment_dict["label"] = re.sub( r"^.*_", "", sentiment_dict["label"].lower() ).title()
    return sentiment_dict

def addSentiment( widgets_df ):
    sentiment_results = []
    for index, row in widgets_df.iterrows():
        comment = row["text"]
        sentiment = analyzeComment( comment )
        sentiment_results.append( list( row ) + [ sentiment["score"], sentiment["label"] ] )
    sentiment_df = pd.DataFrame( sentiment_results, columns = widgets_df.columns.tolist() + [ "SENTIMENT_SCORE", "SENTIMENT" ] )
    return sentiment_df.sort_values("SENTIMENT_SCORE", ignore_index=True )

def getPOS( tokens_arr ):
    result = { "POS_NOUN" : [], "POS_VERB" : [], "POS_ADJ" : [], "POS_ADV" : [] }
    for token in tokens_arr:
        txt = token["lemma"] if token["lemma"] else token["span"]["text"].lower()
        pos = token["part_of_speech"]
        if pos in result.keys():
            result[ pos ].append( txt )
    return result

def addPOS( sentiment_df ):
    pos_arr = []
    for index, row in sentiment_df.iterrows():
        comment = row["text"]
        syntax_result = syntax_model.run( comment, parsers = ( "token", "lemma", "part_of_speech" ) ).to_dict()
        pos = getPOS( syntax_result["tokens"] )
        pos_arr.append( list( row ) + [ pos["POS_NOUN"], pos["POS_ADJ"] ] )
    pos_df = pd.DataFrame( pos_arr, columns = sentiment_df.columns.tolist() + [ "NOUNS", "ADJECTIVES" ] )
    return pos_df.sort_values("SENTIMENT_SCORE", ignore_index=True )
