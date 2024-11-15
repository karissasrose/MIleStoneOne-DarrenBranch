# //////////////////////////////////////////////////
#                    MY IMPORTS
from bs4 import BeautifulSoup
from io import StringIO
import nltk
import os
import json
import psutil
from nltk.stem import PorterStemmer
# //////////////////////////////////////////////////


# //////////////////////////////////////////////////
# //////////////////////////////////////////////////



# //////////////////////////////////////////////////
# //////////////////////////////////////////////////

all_pages = {}
all_tokens = {}
dump_count = 0
last_memory_used = psutil.virtual_memory().used





"""def check_memory_used():
    global last_memory_used
    memory_count = psutil.virtual_memory()
    current_memory = memory_count.used
    memory_difference = (current_memory - last_memory_used) 
    if memory_difference <= 52428800:
        return True
    else:
        last_memory_used = current_memory
        return False """
    

def json_dump_content(all_pages,all_tokens,dump_counter):
    all_tokens_str = "all_tokens.json{}".format(dump_counter)
    with open(all_tokens_str, "w") as file: 
        json.dump(all_tokens, file)

    pass





def computeWordFrequencies(tokens):
    counts = dict()
    for token in tokens:
        if token not in counts:
            counts.update({token: 1})
        else:
            counts[token] += 1
    return counts
 

# //////////////////////////////////////////////////
#                     SOURCE
# https://www.projectpro.io/recipes/use-porter-stemmer
# ////////////////////////////////////////////////////

# PER SOURCE, initialize
ps = PorterStemmer()
 
def tokenize(text):
    file = StringIO(text)
    currentWord = ''
    tokens = []
    while True:
        char = file.read(1)
        if not char: #stop looping if file ended
            if currentWord != '': #if anything left in currentWord, that's a token
                tokens.append(currentWord)
            break
        if not char.isalnum(): #if char is not alphanumeric, it is a separator
            if currentWord != '': #make sure some sort of word was made
                tokens.append(currentWord)
                currentWord = ''
        else: #still reading letters
            currentWord += char.lower()
    file.close()

    stemmanized_tokens = []
    for token in tokens:
        stemmanized_tokens.append(ps.stem(token))

    return stemmanized_tokens #return tokens found


#TODO: figure out decoding from stuff like ISO-whatever, see if we need to do that with beautiful soup
#TODO: urls can contain fragments (#'s), make sure we don't care for that
def read_json_files(folder_path):
    global all_pages
    global all_tokens
    global dump_count
    rotation = 1
    current_docID = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                     with open(file_path, "r") as file:
                        # READING EVERYTHING INSIDE THE FILE I SPECIFY, FOR RIGHT NOW
                        # ALL I WANT TO DO IS SEE IF I CAN PARSE ONE JSON FILE
                        json_content = file.read()

                        dict_content = json.loads(json_content)

                        content = dict_content['content']

                        b_soup = BeautifulSoup(content, "html.parser")

                        defragmented_URL = dict_content['url'].split('#')[0]

                        

                        if defragmented_URL in all_pages.values():
                            pass
                        else:
                            current_docID = current_docID + 1
                            all_pages.update({current_docID : defragmented_URL})

                            # LIKE HW2, WE CAN USET get_text FROM BEAUTIFUL SOUP TO GET ALL THE TEXT FROM THE HTML WE PARSED 
                            text = b_soup.get_text(separator = ' ', strip = False).encode('utf-8', errors='ignore').decode('utf-8')

                            tokens = tokenize(text)
                            counts = computeWordFrequencies(tokens)
                            for token, number in counts.items():
                                if token in all_tokens:
                                    all_tokens[token].append((current_docID, number))
                                else: #we've never seen this token yet
                                    all_tokens.update({token: [(current_docID, number)]})


                            if len(all_pages) < (10000 * rotation):
                                pass
                            else:
                                json_dump_content(all_pages,all_tokens,dump_count)

                                all_tokens = {}

                                dump_count += 1

                                rotation += 1

                except:
                    print(f"ERROR: reading file {file_path} did not work.")


    return all_pages,all_tokens


if __name__ == "__main__":

    folder_path = "DEV"
    read_json_files(folder_path)
    with open("all_pages.json", "w") as file: 
        json.dump(all_pages, file)
    with open("all_tokens.json", "w") as file: 
        json.dump(all_tokens, file)