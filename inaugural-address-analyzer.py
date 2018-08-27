# runs matplotlib in the ipython notebook
%matplotlib inline

# imports
from __future__ import division # allows for python3-like division to be used
from textblob import TextBlob
import glob
import string
import os
import matplotlib.pyplot as plt
import numpy as np

file_loc = '/Users/zkevinfu/Desktop/things/inaugural_addresses/*.txt' # my path the the files

# i currently manually assign each pronoun to a pronoun type catagory, since there arne't that many this has worked out fine
# if i ever want to change to a different part of speech to analyze or graph, this method may need to be changed
first_person_singular_pronouns = ['i', 'my', 'me', 'mine', 'myself']
first_person_plural_pronouns = ['we', 'us', 'our', 'ours', 'ourselves']
second_person_pronouns = ['you', 'your', 'yours', 'yourself', 'yourselves', 'thee', 'thou']
third_person_singular_pronouns = ['it', 'its', 'itself', 'he', 'she', 'him', 'her', 'his', 'her', 'himself', 'herself']
third_person_plural_pronouns = ['they', 'them', 'their', 'theirs', 'themselves']

all_pronouns = [first_person_singular_pronouns, first_person_plural_pronouns, second_person_pronouns, third_person_singular_pronouns, third_person_plural_pronouns]

def clean(s):
    """removes all excess punctuation from a string s, and converts it all to lowercase"""
    punctuations = "-,.?!;:\n\t()[]\"-"
    return s.translate(None, string.punctuation).lower()

def check_if_extra_pronoun(pronoun_dict):
    """helper method to see if there are any excess pronouns that aren't accounted for in my prnoun catagories.
    this actually caught a few edge cases like 'thee' and 'thou'. this isn't currently being used in main"""
    for key, value in sorted(pronoun_dict.iteritems(), key=lambda (k,v): (v,k), reverse = True):
        skip = False
        for pronoun_list in all_pronouns:
            if key in pronoun_list:
                skip = True
                break
        if not skip:
            print "%s: %s" % (key, value)

def print_sorted_pronouns(token_dict_dict, filename):
    """helper method to see a list of pronouns for a given file. I origionally thought I had done something wrong
    when I saw the shift from first person singular to first person plural, so this helped verify my correctness.
    this also is not currently used"""
    for key, value in sorted(token_dict_dict[filename].iteritems(), key=lambda (k,v): (v,k), reverse = True):
        print "%s: %s" % (key, value)

def pronoun_breakdown(pronoun_dict):
    """takes a dictionary of pronouns and catagorizes them into the above 5 catagories. the return type is a dict"""
    first_person_singular = 0
    first_person_plural = 0
    second_person = 0
    third_person_singular = 0
    third_person_plural = 0
    total = 0

    for pronoun in pronoun_dict:
        if pronoun in first_person_singular_pronouns:
            first_person_singular += pronoun_dict[pronoun]
        elif pronoun in first_person_plural_pronouns:
            first_person_plural += pronoun_dict[pronoun]
        elif pronoun in second_person_pronouns:
            second_person += pronoun_dict[pronoun]
        elif pronoun in third_person_singular_pronouns:
            third_person_singular += pronoun_dict[pronoun]
        elif pronoun in third_person_plural_pronouns:
            third_person_plural += pronoun_dict[pronoun]
        total += pronoun_dict[pronoun]

    return {
        'first_person_singular': first_person_singular,
        'first_person_plural': first_person_plural,
        'second_person': second_person,
        'third_person_singular': third_person_singular,
        'third_person_plural': third_person_plural,
        'total': total
    }

def total_to_proportion(total_pronoun_dict):
    """converts a dict of raw numbers into rates. this uses the [pronoun type]/[total pronouns in address] model
    mentioned above. the return type is a dict"""
    if total_pronoun_dict['total'] is 0:
        return total_pronoun_dict
    else:
        return{
            'first_person_singular': total_pronoun_dict['first_person_singular']/total_pronoun_dict['total'],
            'first_person_plural': total_pronoun_dict['first_person_plural']/total_pronoun_dict['total'],
            'second_person': total_pronoun_dict['second_person']/total_pronoun_dict['total'],
            'third_person_singular': total_pronoun_dict['third_person_singular']/total_pronoun_dict['total'],
            'third_person_plural': total_pronoun_dict['third_person_plural']/total_pronoun_dict['total'],
            'total': total_pronoun_dict['total']
        }

def data_process(list_of_speeches_pronoun_data):
    """processess the data structure i use to sture pronoun data for easy use in matplotlib. the return type is
    a list of lists, which each list corresponding to some portion of the graph"""
    speech_list = []
    first_person_singular_proportion_list = []
    first_person_plural_proportion_list = []
    second_person_proportion_list = []
    third_person_singular_proportion_list = []
    third_person_plural_proportion_list = []

    for speech_data in list_of_speeches_pronoun_data:
        speech_list.append(speech_data[0].replace('_', ' ').title())
        first_person_singular_proportion_list.append(speech_data[2]['first_person_singular'])
        first_person_plural_proportion_list.append(speech_data[2]['first_person_plural'])
        second_person_proportion_list.append(speech_data[2]['second_person'])
        third_person_singular_proportion_list.append(speech_data[2]['third_person_singular'])
        third_person_plural_proportion_list.append(speech_data[2]['third_person_plural'])

    return [
        speech_list,
        first_person_singular_proportion_list,
        first_person_plural_proportion_list,
        second_person_proportion_list,
        third_person_singular_proportion_list,
        third_person_plural_proportion_list
    ]

def sort_list_by_president_order(pronoun_proportion_list):
    """takes a tuple that has a date in years as the second parameter, and sorts the tuples based of of that.
    since the texts don't come in order I chose to use the dates to order the texts. this allows for me to easily
    graph dates onto the pyplot as well if i so choose. i could have also used the inital number, perhaps.
    returns a sorted tuple"""
    return sorted(pronoun_proportion_list, key=lambda (k,d,v): (d,k,v))

def create_pronoun_graph(list_of_speeches_pronoun_data):
    """the graph method. takes some obscene data structure and cleans it up using the data_process helper method,
    and then builds a graph object using the lists it returns. simple, but at the same time incredibly painful.
    moving to the future, this could use a bit of cleaning up to provide a neater UI. A lot of ideas were leveraged from:
    https://matplotlib.org/gallery/units/bar_unit_demo.html and https://matplotlib.org/examples/api/barchart_demo.html"""

    # clean up the data
    processed_speech_data_list = data_process(list_of_speeches_pronoun_data)

    fig, ax = plt.subplots(figsize=(50,10))
    ax.set_title('Pronoun Type Density of Presidential Inaugural Addresses', fontsize=50)
    plt.xlabel('Inaugural Address', fontsize=40)
    plt.ylabel('Pronoun Type Rate', fontsize=40)
    plt.rc('xtick',labelsize=20)
    plt.rc('ytick',labelsize=20)

    N = len(list_of_speeches_pronoun_data)

    first_person_singular = processed_speech_data_list[1]
    first_person_plural = processed_speech_data_list[2]
    second_person = processed_speech_data_list[3]
    third_person_singular = processed_speech_data_list[4]
    third_person_plural = processed_speech_data_list[5]

    ind = np.arange(N)    # the x locations for the groups
    width = 0.1         # the width of the bars

    # the order for these are arbitrary
    p1 = ax.bar(ind, first_person_singular, width, color='b', bottom=0)
    p2 = ax.bar(ind + width, first_person_plural, width, color='g', bottom=0)
    p3 = ax.bar(ind + width*2, second_person, width, color='r', bottom=0)
    p4 = ax.bar(ind + width*3, third_person_singular, width, color='c', bottom=0)
    p5 = ax.bar(ind + width*4, third_person_plural, width, color='m', bottom=0)

    ax.set_xticks(ind + width / 5)
    ax.set_xticklabels(processed_speech_data_list[0], rotation='vertical')

    ax.legend((p1[0], p2[0], p3[0], p4[0], p5[0]),
              ('First Person Singular',
               'First Person Plural',
               'Second Person',
               'Third Person Singular',
               'Third Person Plural'
              ),
             fancybox=True,
             title = "Legend")

    plt.show()

def main():
    """main method, initialized the data structures we need, and iterates over the directory containing
    the addresses"""
    token_dict_dict = {}
    all_dict = {}
    pronoun_proportion_list = []
    tag = 'PRP' # base tag for all pronouns, see 'https://www.clips.uantwerpen.be/pages/MBSP-tags' for more info

    for text in glob.glob(file_loc):
        file_title = os.path.basename(text).split('.')[0]

        with open(text, 'r') as f:
            speech = f.read()
            text_dict = {}

            try:
                #TextBlob goodness that tags all the words for me
                speech_blob = TextBlob(clean(speech))
                speech_blob.tags
            except:
                #for some reason Trump's address contained a unicode 128 character that I couldn't find
                #instead of getting rid of it in a single file, i decided to have an except that could catch that case in
                #all sitations and handle them accordingly

                #lets the user know that there was an issue, and that it's been handled
                print file_title,
                print "contains unexpected unicode characters. they have been removed and the document has been processed"

                #gets rid of all unicode characters. i could do this by default, but all the other files ran fine
                #so i didn't think it was worth it
                speech_blob = TextBlob(clean(speech.decode('unicode_escape').encode('ascii','ignore')))

            for token in speech_blob.tags:
                # builds the inital dictionary of data, only looks at words with a specified tag
                if tag in token[1]:
                    try:
                        text_dict[token[0]] += 1
                    except:
                        text_dict[token[0]] = 1
                    try:
                        all_dict[token[0]] += 1
                    except:
                        all_dict[token[0]] = 1
            #breaks the title into 3 pieces: number, president, date
            token_dict_dict[file_title] = text_dict
            partial_split, date = string.rsplit(file_title, '_', 1)
            num_pres, pres = string.split(partial_split, '_', 1)

            pronoun_proportion_list.append(
                (pres, date, total_to_proportion(pronoun_breakdown(token_dict_dict[file_title])))
            )
    create_pronoun_graph(sort_list_by_president_order(pronoun_proportion_list))

if __name__ == "__main__":
    main()
