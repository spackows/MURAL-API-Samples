
import requests
import json

def colorSticky( sticky_id, new_color, mural_oauth_token, mural_id ):
    # https://developers.mural.co/public/reference/updatestickynote
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets/sticky-note/" + sticky_id
    headers = { "Content-Type" : "application/json", "Accept" : "vnd.mural.preview", "Authorization" : "Bearer " + mural_oauth_token }
    data = json.dumps( { "style" : { "backgroundColor" : new_color } } )
    response = requests.request( "PATCH", url, headers=headers, data=data )
    response_json = json.loads( response.text )
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    return msg

sentiment_colors = {
    "Positive" : "yellow",
    "Neutral"  : "green",
    "Negative" : "blue"
}

# https://coolors.co/palette/ff595e-ffca3a-8ac926-1982c4-6a4c93
my_palette = {
    "red"      : "#FF595E",
    "yellow"   : "#FFCA3A",
    "green"    : "#8AC926",
    "blue"     : "#1982C4",
    "purple"   : "#6A4C93"
}

def colorBySentiment( mural_oauth_token, mural_id, sentiment_df ):
    for index, row in sentiment_df.iterrows():
        sticky_id = row["id"]
        sentiment = row["SENTIMENT"]
        new_color = my_palette[ sentiment_colors[ sentiment ] ] + "FF"
        error_str = colorSticky( sticky_id, new_color, mural_oauth_token, mural_id )
        if error_str:
            print( "Changing sticky color failed" )
            print( "index: " + str( index ) )
            print( "MURAL error message:" )
            print( error_str )
            return
    print( "Done" )
