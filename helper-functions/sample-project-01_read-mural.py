import requests
import json
import re
import math
import pandas as pd


def listWidgets( mural_oauth_token, mural_id  ):
    # https://developers.mural.co/public/reference/getmuralwidgets
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets"
    headers = { "Accept": "application/json", "Authorization": "Bearer " + mural_oauth_token }
    response = requests.request( "GET", url, headers = headers )
    response_json = json.loads( response.text )
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    if msg != "":
        print( msg )
        return None
    if "value" not in response_json:
        print( "No value returned" )
        return None
    return response_json["value"]

    
def getLunchAndMinigolfBoxes( widgets_arr ):
    lunch_widget = None
    golf_widget = None
    for widget in widgets_arr:
        if ( "title" in widget ) and re.match( r".*lunch", widget["title"], re.IGNORECASE ):
            lunch_widget = widget.copy()
        elif ( "title" in widget ) and re.match( r".*golf", widget["title"], re.IGNORECASE ):
            golf_widget = widget.copy()
        if ( None != lunch_widget ) and ( None != golf_widget ):
            break;
    return lunch_widget, golf_widget


def stickyCategory( row, lunch_widget, golf_widget ):
    sticky_center_x = row["x"]  + ( 0.5 * row["width"] )
    lunch_center_x  = lunch_widget["x"] + ( 0.5 * lunch_widget["width"] )
    golf_center_x   = golf_widget["x"]  + ( 0.5 * golf_widget["width"] )
    lunch_distance  = abs( sticky_center_x - lunch_center_x )
    golf_distance   = abs( sticky_center_x - golf_center_x )
    return "LUNCH" if ( lunch_distance < golf_distance ) else "GOLF"


def readWidgets( mural_oauth_token, mural_id ):
    widgets_arr = listWidgets( mural_oauth_token, mural_id  )
    if None == widgets_arr:
        print( "Listing widgets failed" )
        return None
    lunch_widget, golf_widget = getLunchAndMinigolfBoxes( widgets_arr )
    widgets_df_full = pd.DataFrame( widgets_arr )
    widgets_df_full.drop( widgets_df_full[ widgets_df_full.type != "sticky note" ].index, inplace=True )
    widgets_df = widgets_df_full[["id","x", "y","width","height","text","style"]].copy()
    widgets_df["category_box"] = widgets_df.apply( stickyCategory, args=( lunch_widget, golf_widget ), axis=1 )
    widgets_df.sort_values("category_box", inplace=True, ignore_index=True )
    return widgets_df

	
