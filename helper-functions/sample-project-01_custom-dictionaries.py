import watson_nlp
import os
import re
import pandas as pd

def createCustomDictionaries():

    module_folder = "Custom_NLP" 
    os.makedirs( module_folder, exist_ok=True )

    lunch_file = "lunch.csv"
    
    with open( os.path.join( module_folder, lunch_file ), "w" ) as table:
        table.write( "\"label\", \"entry\"\n" )
        table.write( "\"LOCATION\", \"far\"\n" )
        table.write( "\"MENU\", \"vegetarian\"\n" )
        table.write( "\"SERVICE\", \"service\"\n" )
        table.write( "\"SERVICE\", \"slow\"\n" )
        table.write( "\"SERVICE\", \"waiter\"\n" )
        table.write( "\"FOOD\", \"food\"\n" )
        table.write( "\"FOOD\", \"bread\"\n" )
        table.write( "\"FOOD\", \"fresh\"\n" )
        table.write( "\"LUNCH\", \"lunch\"\n" )

    lunch_config = {
        "name"   : "lunch",
        "source" : lunch_file,
        "dict_type" : "table",
        "mappings": { "columns": [ "label", "entry" ], "entry" : "entry" },
        "consolidate" : "ContainedWithin",
        "case"        : "insensitive"
    }

    golf_file = "mini-golf.csv"
    
    with open( os.path.join( module_folder, golf_file ), 'w' ) as table:
        table.write( "\"label\", \"entry\"\n" )
        table.write( "\"GOLF\", \"mini-golf\"\n" )
        table.write( "\"GOLF\", \"minigolf\"\n" )
        table.write( "\"GOLF\", \"golf\"\n" )
        table.write( "\"PLAY\", \"hole in one\"\n" )
        table.write( "\"PLAY\", \"scores\"\n" )
        table.write( "\"WEATHER\", \"weather\"\n" )
        table.write( "\"WEATHER\", \"rain\"\n" )
        table.write( "\"COURSE\", \"golf course\"\n" )
        table.write( "\"COURSE\", \"course\"\n" )
        
    golf_config = {
        "name"   : "golf",
        "source" : golf_file,
        "dict_type" : "table",
        "mappings": { "columns": [ "label", "entry" ], "entry" : "entry" },
        "consolidate" : "ContainedWithin",
        "case"        : "insensitive"
    }

    dict_arr = watson_nlp.toolkit.DictionaryConfig.load_all( [ lunch_config, golf_config ] )

    custom_dictionaries = watson_nlp.resources.feature_extractor.RBR.train( 
        module_folder,
        language = "en", 
        dictionaries = dict_arr
    )
    
    return custom_dictionaries


def getEntities( entities_raw ):
    entities = {}
    for category in entities_raw["annotations"].keys():
        catgory_name = re.sub( r"^.+\_", "", category ).upper();
        if catgory_name not in entities:
            entities[ catgory_name ] = []
        for match in entities_raw["annotations"][category]:
            label = match["label"]
            if label not in entities[ catgory_name ]:
                entities[ catgory_name ].append( label )
    top_category, top_entities = max( entities.items(), key = lambda x: len(set(x[1])) )
    result = { "DICTIONARY" : "", "ENTITIES" : [] }
    if len( top_entities ) > 0:
        result = { "DICTIONARY" : top_category, "ENTITIES" : top_entities }
    return result
    

def addEntities( pos_df, custom_dictionaries ):
    entities_arr = []
    for index, row in pos_df.iterrows():
        comment = row["text"]
        entities_raw = custom_dictionaries.executor.get_raw_response( comment, language = "en" )
        entities = getEntities( entities_raw )
        entities_arr.append( list( row ) + [ entities["DICTIONARY"] ] + [ entities["ENTITIES"] ]  )
    entities_df = pd.DataFrame( entities_arr, columns = pos_df.columns.tolist() + list( entities.keys() ) )
    for index, row in entities_df.iterrows():
        while "LUNCH" in row["ENTITIES"]:
            row["ENTITIES"].remove( "LUNCH" )
        while "GOLF" in row["ENTITIES"]:
            row["ENTITIES"].remove( "GOLF" )
    themes = []
    for index, row in entities_df.iterrows():
        entities_arr = row["ENTITIES"]
        theme = "GENERAL" if ( len( entities_arr ) < 1 ) else entities_arr[0]
        themes.append( theme )
    entities_df["theme"] = themes
    return entities_df.sort_values( "DICTIONARY", ignore_index=True )

