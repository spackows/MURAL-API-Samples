import requests
import copy
import re
import json
import math
import numpy as np


def putWidget( auth_token, mural_id, widget ):
    # eg. https://developers.mural.co/public/reference/createstickynote
    widget_type = ""
    if( "arrowType" in widget ):
        widget_type = "arrow"
    else:
        widget_type = "textbox" if ( "text" == widget["type"] ) else widget["type"]
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets/" + re.sub( "\s+", "-", widget_type )
    headers = { "Accept"        : "application/json", 
                "Content-Type"  : "application/json", 
                "Authorization" : "Bearer " + auth_token }
    parms = copy.deepcopy( widget )
    if "id" in parms:
        del parms["id"]
    if "type" in parms:
        del parms["type"]
    response = requests.request( "POST", url, headers = headers, json = parms )
    response_json = json.loads( response.text )
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]
    return msg


def putWidgets( auth_token, mural_id, widgets_arr ):
    for widget in widgets_arr:
        error_str = putWidget( auth_token, mural_id, widget )
        if error_str:
            return error_str + "\n" + json.dumps( widget, indent=3 )
    return ""


def listWidgets( auth_token, mural_id ):
    # https://developers.mural.co/public/reference/getmuralwidgets
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets"
    headers = { "Accept": "application/json", "Authorization": "Bearer " + auth_token }
    response = requests.request( "GET", url, headers = headers )
    response_json = json.loads( response.text )
    msg = ""
    if "code" in response_json:
        msg += "response_json[\"code\"]: " + response_json["code"] + "\n"
    if "message" in response_json:
        msg += "response_json[\"message\"]: " + response_json["message"] + "\n"
    if "value" not in response_json:
        msg += "No 'value' field returned from the MURAL API"
        result = None
    else:
        result = response_json["value"]
    return msg, result


def createArcs( class_names_arr ):
    if( len( class_names_arr ) , 1 ):
        return []
    num_arcs = len( class_names_arr )
    arc_size = 360 / num_arcs
    first_angle = 90 - ( arc_size / 2 )
    arcs_arr = []
    for i in range( num_arcs ):
        start_angle = first_angle + i * arc_size
        end_angle = start_angle + arc_size
        arcs_arr.append( { "class_name"  : class_names_arr[i],
                           "start_angle" : start_angle,
                           "end_angle"   : end_angle } )
    return arcs_arr


def arrowWidget( angle ):
    length = 3000
    start_x = 0
    start_y = 0
    x_adjust = 1
    y_adjust = 1
    if( angle > 270 ):
        angle = 360 - angle
        y_adjust = -1
    elif( angle > 180 ):
        angle = angle - 180
        y_adjust = -1
        x_adjust = -1
    elif( angle > 90 ):
        angle = 180 - angle
        x_adjust = -1
    width = length * math.cos( np.deg2rad( angle ) )
    height = length * math.sin( np.deg2rad( angle ) )
    end_x = width * x_adjust
    end_y = height * y_adjust * -1
    widget = { "id"       : "dummy",
               "x"        : start_x,
               "y"        : start_y,
               "height"   : height,
               "width"    : width,
               "points"   : [ { "x": start_x, "y": start_y }, { "x": end_x, "y": end_y } ],
               "arrowType": "straight",
               "tip"      : "no tip",
               "style"    : { "strokeColor" : "#000000FF",
                              "strokeStyle" : "solid",
                              "strokeWidth" : 5 } }
    return widget

    
def putArcs( auth_token, mural_id, arcs_arr ):
    for arc in arcs_arr:
        angle = arc["start_angle"]
        if( angle > 360 ):
            angle = angle - 360
        widget = arrowWidget( angle )
        error_str = putWidget( auth_token, mural_id, widget)
        if error_str:
            return error_str
    return ""


def classNameXY( arc, widget ):
    buffer = 60
    arc_start_angle = arc["start_angle"]
    arc_end_angle = arc["end_angle"]
    arc_angle_diff = ( arc_end_angle - arc_start_angle ) / 2
    if( arc_start_angle > 360 ):
        arc_start_angle = arc_start_angle - 360
    if( arc_end_angle > 360 ):
        arc_end_angle = arc_end_angle - 360
    widget_angle = arc_start_angle + arc_angle_diff
    x_adjust = 1
    y_adjust = 1
    if( widget_angle > 360 ):
        widget_angle = widget_angle - 360
    elif( widget_angle > 270 ):
        widget_angle = 360 - widget_angle
        y_adjust = -1
    elif( widget_angle > 180 ):
        widget_angle = widget_angle - 180
        y_adjust = -1
        x_adjust = -1
    elif( widget_angle > 90 ):
        widget_angle = 180 - widget_angle
        x_adjust = -1
    widget_radius = math.sqrt( ( 0.5 * widget["width"] )**2 + ( 0.5 * widget["height"] )**2 )
    distance = widget_radius / ( math.sin( np.deg2rad( arc_angle_diff ) ) ) + buffer
    center_x = distance * math.cos( np.deg2rad( widget_angle ) )
    center_y = distance * math.sin( np.deg2rad( widget_angle ) )
    center_x = center_x * x_adjust
    center_y = -1 * center_y * y_adjust
    x = center_x - ( 0.5 * widget["width"] )
    y = center_y - ( 0.5 * widget["height"] )
    return x, y


def classNameWidget( arc ):
    widget = { "id"     : "dummy",
               "x"      : 0,
               "y"      : 0,
               "height" : 200,
               "width"  : 500,
               "type"   : "text",
               "text"   : arc["class_name"],
               "style"  : { "backgroundColor": "#FFFFFF00",
                            "font"      : "proxima-nova",
                            "fontSize"  : 60,
                            "textAlign" : "center" } }
    x, y = classNameXY( arc, widget )
    widget["x"] = x
    widget["y"] = y
    return widget
    

def putClassNames( auth_token, mural_id, arcs_arr ):
    for arc in arcs_arr:
        widget = classNameWidget( arc )
        error_str = putWidget( auth_token, mural_id, widget )
        if error_str:
            return error_str
    return ""


from copy import deepcopy
import random


def minMaxAngle( arc, sticky_radius, sticky_distance ):
    min_angle = arc["start_angle"] + np.rad2deg( math.asin( sticky_radius / sticky_distance ) )
    max_angle = arc["end_angle"] - np.rad2deg( math.asin( sticky_radius / sticky_distance ) )
    return min_angle, max_angle


def possibleAngles( arc, sticky_radius, sticky_distance, iteration=0 ):
    if( iteration > 50 ):
        print( "Unexpected result: possibleAngles never found an angle" )
        return None
    
    min_angle, max_angle = minMaxAngle( arc, sticky_radius, sticky_distance )
    
    circumfrence = 2 * math.pi * sticky_distance
    angle_diff = max_angle - min_angle
    arc_length = ( angle_diff / 360 ) * circumfrence
    num_angles = math.floor( arc_length / ( 2 * sticky_radius + 10 ) )
    angle_piece = angle_diff / num_angles
    
    angles_arr = []
    for i in range( num_angles ):
        angle = min_angle + ( i * angle_piece ) + ( 0.5 * angle_piece )
        angles_arr.append( angle )

    if( len( angles_arr ) > 0 ):
        return angles_arr
    
    sticky_distance += sticky_radius
    return possibleAngles( arc, sticky_radius, sticky_distance, iteration + 1 )


def stickyXY( sticky_radius, sticky_angle, sticky_distance ):
    center_x = sticky_distance * math.cos( np.deg2rad( sticky_angle ) )
    center_y = sticky_distance * math.sin( np.deg2rad( sticky_angle ) )
    sticky_x = center_x - sticky_radius
    sticky_y = center_y + sticky_radius
    sticky_y = -1 * sticky_y
    return sticky_x, sticky_y


def moveSticky( auth_token, mural_id, sticky_id, new_x, new_y ):
    # https://developers.mural.co/public/reference/updatestickynote
    url = "https://app.mural.co/api/public/v1/murals/" + mural_id + "/widgets/sticky-note/" + sticky_id
    headers = { "Accept"        : "application/json", 
                "Content-Type"  : "application/json", 
                "Authorization" : "Bearer " + auth_token }
    parms = { "x" : new_x, "y" : new_y }
    response = requests.request( "PATCH", url, headers = headers, json = parms )
    response_json = json.loads( response.text )
    msg = ""
    if "code" in response_json:
        msg += response_json["code"] + " "
    if "message" in response_json:
        msg += response_json["message"]


def putStickiesInArc( auth_token, mural_id, arc, stickies_arr_in ):
    
    sticky_radius = 325
    sticky_distance = 400
    stickies_arr = deepcopy( stickies_arr_in )
    
    while( len( stickies_arr ) > 0 ):
        
        sticky_distance += 2 * sticky_radius
        
        angles_arr = possibleAngles( arc, sticky_radius, sticky_distance )
        if( angles_arr is None ):
            return
        
        sticky = stickies_arr.pop(0)
        sticky_angle = angles_arr.pop(0)
        new_x, new_y = stickyXY( sticky_radius, sticky_angle, sticky_distance + random.randint( 0, 20 ) )
        moveSticky( auth_token, mural_id, sticky["id"], new_x, new_y )
        
        while( ( len( angles_arr ) > 0 ) and ( len( stickies_arr ) > 0 ) ):
            sticky = stickies_arr.pop(0)
            sticky_angle = angles_arr.pop(0)
            new_x, new_y = stickyXY( sticky_radius, sticky_angle, sticky_distance + random.randint( 0, 20 ) )
            moveSticky( auth_token, mural_id, sticky["id"], new_x, new_y )

def moveStickiesToClassArcs( auth_token, mural_id, arcs_arr, classified_stickies ):
    for arc in arcs_arr:
        class_name = arc["class_name"]
        stickies_arr = classified_stickies[ class_name ]
        putStickiesInArc( auth_token, mural_id, arc, classified_stickies[ class_name ] )

