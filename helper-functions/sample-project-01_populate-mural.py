import requests
import json

def addWidgetToMural( mural_oauth_token, mural_id, widget_data, widget_type ):
    # https://developers.mural.co/public/reference/createstickynote
    # https://developers.mural.co/public/reference/createtitle
    # https://developers.mural.co/public/reference/createshapewidget
    #widget_type = widget_type_map[ widget_data["type"] ]
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets/" + widget_type
    headers = { "Content-Type" : "application/json", "Accept" : "vnd.mural.preview", "Authorization" : "Bearer " + mural_oauth_token }
    data = json.dumps( widget_data )
    response = requests.request( "POST", url, headers=headers, data=data )
    response_json = json.loads( response.text )
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    return msg    

widget_type_map = {
    # From export   # For importing
    "sticky note" : "sticky-note",
    "text"        : "title",
    "shape"       : "shape"
}

def addWidgetsToMural( mural_oauth_token, mural_id, widgets_arr ):
    widgets_arr_copy = widgets_arr.copy()
    widgets_arr_copy.sort( key = lambda widget: widget["stackingOrder"] )
    for widget in widgets_arr_copy:
        widget_type = widget_type_map[widget["type"]]
        widget_copy = widget.copy()
        del widget_copy["stackingOrder"]
        del widget_copy["type"]
        error_str = addWidgetToMural( mural_oauth_token, mural_id, widget_copy, widget_type )
        if error_str:
            print( "Adding widget failed" )
            print( "widget:\n" + json.dumps( widget, indent=2 ) )
            print( "MURAL error message:" )
            print( error_str )
            return
