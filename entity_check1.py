import csv
import difflib
import operator
from ngram import NGram
import logging
import traceback

logger_path = "Entityapi.log"
logger = logging.getLogger('entity_check')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(logger_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)2s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def extract_entity(filename, filename_version):
    try:
        logger.info("Extraction of entity and value from %s started", filename)
        entity = {}
        entity_version_dict = {}
        entity_variations = []
        entity_version = []
        max_word_len = 0
        entity_version_max_len = 0
        with open(filename_version, 'r') as data:
            data = csv.reader(data)
            #print(data)
            for row in data:
                #print(row)
                entity_version = []
                for i in range(1, len(row)):
                    entity_version.append(row[i].lower())
                    if len(row[i].split()) > entity_version_max_len:
                        entity_version_max_len = len(row[i].split())
                entity_version_dict[row[0].lower()] = entity_version
        with open(filename, 'r') as data:
            data = csv.reader(data)
            for row in data:
                for i in range(2, len(row)):
                    if len(row[i]) > 0:
                        entity_variations.append(row[i])
                        if len(row[i].split()) > max_word_len:
                            max_word_len = len(row[i].split())
                        entity[row[i].lower()] = (row[0], row[1])
        logger.info("Extraction of entity and value from %s completed", filename)
       # print entity
        return entity, entity_variations, max_word_len, entity_version_dict, entity_version_max_len
    except Exception as e:
        logger.error('Error Details.......%s', e)


def find_similar_entity(entity_variations, sentence):
    try:
        #print("-------")
        #print(entity_variations)
        #print(sentence)
        logger.info("Similarity matching started")
        #print (entity_variations)
        similarity = {}
        best_score = 0
        sm = difflib.SequenceMatcher(None)
        for word in sentence:
            #print (type(word))
            sm.set_seq2(word.lower())
            #print (word.lower)
            
            for variations in entity_variations:
                #print(type(variations.lower()))
                sm.set_seq1(variations.lower())
                #print (variations.lower())
                if (variations.lower() in similarity.keys()) and similarity[variations.lower()] > sm.ratio():
                    pass
                else:
                    similarity[variations.lower()] = sm.ratio()
                    #print (similarity[variations.lower()])
        result = sorted(similarity.items(), key=operator.itemgetter(1, 0), reverse=True)
        #print ("111111")
        #print (result)
        #print (result[1])
        result_list = []
        for value in result:
            if value[1] > 0.65:
                result_list.append([value[0], value[1]])
        dummy_list = []
        new_result = []
        logger.info("Extracted Entity:%s", result_list)
        for value in result_list:
            for word in sentence:
                sm = difflib.SequenceMatcher(None, value[0], word.lower())
                if sm.ratio() == value[1]:
                    new_result.append([value[0], value[1], word])
        logger.info("Similarity matching completed")
        if len(result_list) > 0:
            return new_result
        else:
            #return "Fail", "No match Found"
            return []
    except Exception as e:
        logger.error('Error Details.......%s', e)


def generate_ngrams(sentence, max_word_len):
    try:
        logger.info("ngram started")
        ngram_list = []
        max_word = max_word_len
        #print (max_word)
        for i in range(1, max_word):
            n_gram =NGram(sentence.split())
            #print (n_gram)
            for gram in n_gram:
                #print (gram)
                ngram_list.append(" ".join(list(gram)))
                #print (ngram_list)
        logger.info("ngram completed")
        #print (ngram_list)
        #print(ngram_list)
        return (ngram_list)
    except Exception as e:
        logger.error('Error Details.......%s', e)


def entity_retrieval(sentence):
    try:
        logger.info("Entity retrieval started")
        entity, entity_variations, max_word_len, entity_version_dict, entity_version_max_len = extract_entity(
            "entitynew.csv",
            "entity_version.csv")
        # print(entity)
        # print(entity_variations)
        #print(max_word_len)
        #print(entity_version_max_len)
        ngram_sentence = generate_ngrams(sentence, max_word_len)
        ngram_sentence_variation=generate_ngrams(sentence,entity_version_max_len)
        #print(ngram_sentence_variation)
        #print(entity_version_dict)
        for i in range(len(ngram_sentence_variation)):
            ngram_sentence_variation[i]=ngram_sentence_variation[i].lower()
        entity["Fail"] = ("No result Found", 0.0)
        #print(ngram_sentence_variation)
        #print(entity_variations)
        result = find_similar_entity(entity_variations, ngram_sentence)
        #print(result)
##        if result[0]=='Fail' and result[1]=='No match Found':
##            pass
        
        for res in result:
            res.append(entity[res[0]][0])
            res.append(entity[res[0]][1])
        for value in result:
            if value[4].lower() in entity_version_dict:
                version=entity_version_dict[value[4].lower()]
                v_list = []
                for ver in version:
                    #print ver
                    for ngram in ngram_sentence_variation:
                        sm = difflib.SequenceMatcher(None,ngram,ver)
                        # print iteam, ngram,sm.ratio()
                        if sm.ratio()>.8:
                            #print "hi"
                            v_list.append([sm.ratio(),ver])
                            #print v_list
                v_list=sorted(v_list,reverse=True)
                #print v_list
                if len(v_list)>0:
                    value[4]=v_list[0][1]
                #print version
                '''for ver in version:
                    if ver in ngram_sentence_variation:
                        #print ver
                        value[4]=ver
                        #print value
                        break'''
        #print result
        val = 0
        while val < len(result):
            if result[val][3] == result[val][4]:
                count = 0
                for res in result:
                    if result[val][3] in res:
                        count += 1
                if count > 1:
                    result.remove(result[val])
                    val = 0
                else:
                    val += 1
            else:
                val += 1
        #print result
        json = []
        check = []
        for value in result:
            start_pos = sentence.find(value[2])
            # print value
            if value[4] in check:
                continue
            check.append(value[4])
            end_pos = start_pos + len(value[2]) - 1
            json.append({"entity": entity[value[0]][0], "location": [start_pos, end_pos], "value": value[4],
                         "score": value[1]})
            # print json
        json_response = []
        if len(json) > 0:
            json_response.append({"description": sentence, "entities": json})
        else:
            json_response.append({"description": sentence, "entities": []})
        logger.info("Entity retrieval completed")
        return json_response
    except Exception as e:
        logger.error('Error Details.......%s', e)
        #print(traceback.format_exc())


def information_retrieval(description, separator):
    try:
        logger.info("information retrieval started")
        json_output_list = []
        sentence = description.split(separator)
        #print(sentence)
        for sen in sentence:
            E_R = entity_retrieval(sen)
            if E_R == None:
                json_output_list.append([{"description": sen, "entities": []}])
            else:
                json_output_list.append(E_R)
        # print json_output_list
        output_json = []
        # print json_output_list
        for json in json_output_list:
            output_json.append(json[0])
        # print  output_json
        return {"output":output_json}
    except Exception as e:
        logger.error('Error Details.......%s', e)


if __name__ == "__main__":
    sen = input("enter your querry\n") 
    a = information_retrieval(sen, " ")
    print (a)
