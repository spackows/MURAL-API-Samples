import requests
import json
import random


widget_type_map = {
    # From export   # For importing
    "sticky note" : "sticky-note",
    "text"        : "title",
    "shape"       : "shape"
}


def addWidgetToMural( mural_oauth_token, mural_id, widget_data, widget_type ):
    # https://developers.mural.co/public/reference/createstickynote
    # https://developers.mural.co/public/reference/createtitle
    # https://developers.mural.co/public/reference/createshapewidget
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


def addWidgetsToMuralJSON( mural_oauth_token, mural_id, widgets_arr ):
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
    print( "Done" )


def randomColor():
    # Color palette: https://coolors.co/palette/ff595e-ffca3a-8ac926-1982c4-6a4c93
    colors_arr = [ 
        "#FF595EFF",
        "#FFCA3AFF",
        "#8AC926FF",
        "#1982C4FF",
        "#6A4C93FF"
    ]
    color = random.choice( colors_arr )
    return color


def randomSize():
    # Default canvas size: 9216 wide x 6237 high.
    # We're placing ~25 square stickies on the canvas, so 
    # let's make the stickies 10-15% of the canvas height.
    canvas_width = 9216
    canvas_height = 6237
    size_sm = round( 0.1 * canvas_height )
    size_lg = round( 0.15 * canvas_height )
    size = random.randint(size_sm, size_lg )
    return size


def stickyJSON( comment ):
    color = randomColor()
    size = randomSize()
    widget_json = {
        "text"   : comment,
        "shape"  : "rectangle",
        "x"      : 0, # Will adjust placement later
        "y"      : 0, #
        "height" : size,
        "width"  : size,
        "style"  : {
            "backgroundColor" : color,
            "fontSize" : 100
        }
     }
    return widget_json


def randomPosition( sticky_width, sticky_height ):
    # Default canvas size: 9216 wide x 6237 high
    canvas_width = 9216
    canvas_height = 6237
    buffer = 200
    x = random.randint( buffer, ( canvas_width - buffer - sticky_width ) )
    y = random.randint( buffer, ( canvas_height - buffer - sticky_height ) )
    return x, y


def stickyInsideOverlapsRectangle( sticky, rectangle ):
    #
    left_edge_overlaps = False
    if ( sticky["x"] >= rectangle["x"] ) and \
       ( sticky["x"] <= ( rectangle["x"] + rectangle["width"] ) ):
        left_edge_overlaps = True
    #
    right_edge_overlaps = False
    if ( ( sticky["x"] + sticky["width"] ) >= rectangle["x"] ) and \
       ( ( sticky["x"] + sticky["width"] ) <= ( rectangle["x"] + rectangle["width"] ) ):
        right_edge_overlaps = True
    #
    top_edge_overlaps = False
    if ( sticky["y"] >= rectangle["y"] ) and \
       ( sticky["y"] <= ( rectangle["y"] + rectangle["height"] ) ):
        top_edge_overlaps = True
    #
    bottom_edge_overlaps = False
    if ( ( sticky["y"] + sticky["height"] ) >= rectangle["y"] ) and \
       ( ( sticky["y"] + sticky["height"] ) <= ( rectangle["y"] + rectangle["height"] ) ):
        bottom_edge_overlaps = True
    
    if left_edge_overlaps and right_edge_overlaps and top_edge_overlaps and bottom_edge_overlaps:
        # Sticky is inside the rectangle
        return True
    
    if ( left_edge_overlaps or right_edge_overlaps ) and ( top_edge_overlaps or bottom_edge_overlaps ):
        # Sticky overlaps the rectangle
        return True
    
    return False


def overlaps( sticky_in, stickies_arr ):
    for existing_sticky in stickies_arr:
        if stickyInsideOverlapsRectangle( sticky_in, existing_sticky ) or stickyInsideOverlapsRectangle( existing_sticky, sticky_in ):
            return True
    return False


def addStickyPosition( sticky, existing_stickies_arr ):
    x, y = randomPosition( sticky["width"], sticky["height"] )
    sticky["x"] = x
    sticky["y"] = y
    count = 0
    while overlaps( sticky, existing_stickies_arr ) and ( count < 5 ):
        x, y = randomPosition( sticky["width"], sticky["height"] )
        sticky["x"] = x
        sticky["y"] = y
        count += 1
    return sticky


def addWidgetsToMuralDF( mural_oauth_token, mural_id, comments_df ):
    existing_stickies_arr = []
    for index, row in comments_df.iterrows():
        sticky = stickyJSON( row["COMMENT"] )
        sticky = addStickyPosition( sticky, existing_stickies_arr )
        error_str = addWidgetToMural( mural_oauth_token, mural_id, sticky, "sticky-note" )
        if error_str:
            print( "Adding sticky note failed" )
            print( "index: " + str( index ) )
            print( "sticky:\n" + json.dumps( sticky, indent=2 ) )
            print( "MURAL error message:" )
            print( error_str )
            return
        existing_stickies_arr.append( sticky )
    print( "Done" )


def addWidgetsToMural( mural_oauth_token, mural_id, **kwargs ):
    if "widgets_json" in kwargs:
        addWidgetsToMuralJSON( mural_oauth_token, mural_id, kwargs["widgets_json"] )
    elif "comments_df" in kwargs:
        addWidgetsToMuralDF( mural_oauth_token, mural_id, kwargs["comments_df"] )
    else:
        print( "No widgets specified.  Specify either: 'widgets_json' or 'comments_df'" )

