
import requests
import json
from IPython.display import display, HTML
import re
import pandas as pd
import watson_nlp
from watson_nlp.toolkit import predict_document_sentiment


def createMural( room_name, workshop_key ):
    url = "https://weavesphere-mural-oauth.tqns6lm651z.us-south.codeengine.appdomain.cloud/create-mural-workshop-part2"
    headers = { "Content-Type" : "application/json", "Accept" : "application/json" }
    data = json.dumps( { "room_name" : room_name, "workshop_key" : workshop_key } )
    response = requests.request( "POST", url, headers=headers, data=data )
    response_json = response.json()
    if "error_str" in response_json:
        print( response_json["error_str"] )
        return None, None, None
    if "mural_id" not in response_json:
        print( "Field 'mural_id' not returned in result\nResult:" + json.dumps( response_json, indent=3 ) )
        return None, None, None
    if "mural_link" not in response_json:
        print( "Field 'mural_link' not returned in result\nResult:"+ json.dumps( response_json, indent=3 ) )
        return None, None, None
    if "widgets_arr" not in response_json:
        print( "Field 'widgets_arr' not returned in result\nResult:"+ json.dumps( response_json, indent=3 ) )
        return None, None, None
    mural_id = response_json["mural_id"]
    mural_link = response_json["mural_link"]
    widgets_arr = response_json["widgets_arr"]
    html = HTML( "<h3>Mural for: Workshop Part 2 of 2</h3>" + 
             "<p>Mural ID: <code>" + mural_id + "</code></p>" +
             "<p>\"Visitor\" link: <a href='" + mural_link + "' target='_other'>Click to open mural in a new tab</a></p>" )
    display( html )
    return mural_id, mural_link, widgets_arr
    
def putStickiesIntoDF( widgets_arr ):
    widgets_df_full = pd.DataFrame( widgets_arr )
    stickies_df = widgets_df_full[ widgets_df_full["type"] == "sticky-note" ].copy()
    stickies_df = stickies_df[["id","x", "y","width","height","text"]].reset_index( drop=True )
    return stickies_df

def analyzeComment( syntax_model, sentiment_model, comment ):
    syntax_result = syntax_model.run( comment )
    sentiment_result  = sentiment_model.run_batch( syntax_result.get_sentence_texts(), syntax_result.sentences )
    document_sentiment = predict_document_sentiment( sentiment_result, sentiment_model.class_idxs )
    sentiment_dict = document_sentiment.to_dict()
    sentiment_dict["label"] = re.sub( r"^.*_", "", sentiment_dict["label"].lower() ).title()
    return sentiment_dict

def generateSentimentColumns( row, syntax_model, sentiment_model ):
    comment = row["text"]
    sentiment_dict = analyzeComment( syntax_model, sentiment_model, comment )
    return sentiment_dict["label"], sentiment_dict["score"]

def getPOS( tokens_arr ):
    result = { "POS_NOUN" : [], "POS_VERB" : [], "POS_ADJ" : [], "POS_ADV" : [] }
    for token in tokens_arr:
        txt = token["lemma"] if token["lemma"] else token["span"]["text"].lower()
        pos = token["part_of_speech"]
        if pos in result.keys():
            result[ pos ].append( txt )
    return result

def generateSyntaxColumns( row, syntax_model ):
    comment = row["text"]
    syntax_dict = syntax_model.run( comment, parsers=( "token", "lemma", "part_of_speech" ) ).to_dict()
    pos = getPOS( syntax_dict["tokens"] )
    return pos["POS_NOUN"], pos["POS_ADJ"]

def addNLPAnalysis( syntax_model, sentiment_model, stickies_df ):
    stickies_w_sentiment_df = stickies_df.copy()
    stickies_w_sentiment_df[ [ "SENTIMENT", "SENTIMENT_SCORE" ] ] = stickies_w_sentiment_df.apply ( generateSentimentColumns, syntax_model=syntax_model, sentiment_model=sentiment_model, axis=1, result_type="expand" )
    stickies_w_pos_df = stickies_w_sentiment_df.copy()
    stickies_w_pos_df[ [ "NOUNS", "ADJECTIVES" ] ] = stickies_w_pos_df.apply ( generateSyntaxColumns, syntax_model=syntax_model, axis=1, result_type="expand" )
    return stickies_w_pos_df

