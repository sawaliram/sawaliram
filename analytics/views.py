from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
import datetime
import collections
from .lang import *
from dashboard.models import (
    Question)

state_code = {'lakshadweep': 'LD', 'andaman and nicobar islands': 'AN', 'maharashtra': 'MH', 
            'andhra pradesh': 'AP', 'meghalaya': 'ML', 'arunachal pradesh': 'AR', 'manipur': 'MN', 'assam': 'AS', 
            'madhya pradesh': 'MP', 'bihar': 'BR', 'mizoram': 'MZ', 'chandigarh': 'CH', 'nagaland': 'NL', 
            'chhattisgarh': 'CT', 'odisha': 'OR', 'daman and diu': 'DD', 'punjab': 'PB', 'delhi': 'DL', 
            'puducherry': 'PY', 'dadra and nagar haveli': 'DN', 'rajasthan': 'RJ', 'goa': 'GA', 'sikkim': 'SK', 
            'gujarat': 'GJ', 'telangana': 'TG', 'himachal pradesh': 'HP', 'tamil nadu': 'TN', 'haryana': 'HR', 
            'tripura': 'TR', 'jharkhand': 'JH', 'uttar pradesh': 'UP', 'jammu and kashmir': 'JK', 'uttarakhand': 'UT', 
            'karnataka': 'KA', 'west bengal': 'WB', 'kerala': 'KL'}

            # dictionary to hold the name of the state and its ISO code.

def home(request):
    """
    Returns the HTTP Response for the home page of analytics app.
    """
    # Each function getABC() returns the data for the ABC which is then added to context.
    year_labels, year_counts = getYearAsked()
    lang_names, lang_counts = getQuestionLanguages()
    gender_labels, gender_counts = getGenderStat()
    mlang_names, mlang_counts = getMediumLanguage()
    class_labels, class_counts = getStudentClassStat()
    # Stats for doughnut charts
    format_labels, format_counts = getQuestionFormatStats()
    curriculum_labels, curriculum_counts = getCurriculumStats()
    context_labels, context_counts = getContextStats()
    states, codes, counts = getMapStats()

    return render(request, 'home.html', 
        {"page_title": "Analytics", 
        "question_counter": getQuestionAsked(),
        "lang_names" : lang_names,
        "lang_counts" : lang_counts,
        "year_labels" : year_labels,
        "year_counts" : year_counts,
        "gender_counts" : gender_counts,
        "gender_labels" : gender_labels,
        "mlang_names" : mlang_names,
        "mlang_counts" : mlang_counts,
        "class_labels" : class_labels,
        "class_counts" : class_counts,
        "format_labels" : format_labels,
        "format_counts" : format_counts,
        "curriculum_labels" : curriculum_labels,
        "curriculum_counts" : curriculum_counts,
        "context_labels" : context_labels,
        "context_counts" : context_counts,
        "state_names" : states,
        "state_codes" : codes,
        "state_counts" : counts,
        })


def getQuestionAsked(params = None):
    return Question.objects.count()


def getQuestionLanguages(params=None):
    distinct = Question.objects.values('language').annotate(count=Count('language'))
    lang_names = []         # list to hold the name of the language
    lang_counts = []        # list to hold the count of question for the language corresponding to name in lang_names 
    for lang in distinct:
        lang_code = lang['language']
        if lang_code in language_name:
            lang_name = language_name[lang_code]
        else:
            lang_name = lang_code

        if lang_name in lang_names:
            # if the language name is twice in the list for any reason then reject it. (Workaround)
            # This is caused due to nonuniform labelling of languages in Database. 
            continue

        lang_names.append(lang_name)
        lang_counts.append(lang['count'])

    return lang_names, lang_counts


def getYearAsked(params = None):
    distinct = Question.objects.values('question_asked_on').annotate(count=Count('question_asked_on'))
    year_tuples = [(tple['question_asked_on'].year if tple['question_asked_on'] else None, tple['count']) for tple in distinct ]
    year_dict = {}
    for year, count in year_tuples:
        if year is None:  #Some tuples might be None due to null value in database
            continue
        if year not in year_dict:
            year_dict[year] = count
        else:
            year_dict[year] += count
    # Now we shall generate the lists of year labels and counts
    year_label, year_count = [], []
    ordered_tuples = collections.OrderedDict(sorted(year_dict.items()))
    year_labels = list(map(str, ordered_tuples.keys()))
    year_counts = list(ordered_tuples.values())
    return year_labels, year_counts


def getGenderStat(params = None):
    distinct = Question.objects.values('student_gender').annotate(count=Count('student_gender'))
    gender_tuples = sorted([(tple['student_gender'] if tple['student_gender'] else "NA", tple['count']) for tple in distinct], key = lambda item : item[0])
    return map(list, zip(*gender_tuples))


def getMediumLanguage(params = None):
    distinct = Question.objects.values('medium_language').annotate(count=Count('medium_language'))
    mlang_names = []         # list to hold the name of the language
    mlang_counts = []        # list to hold the count of question for the language corresponding to name in lang_names 
    for lang in distinct:
        lang_code = lang['medium_language']
        if lang_code in language_name:              # This won't work here because medium is not stored using language code
            lang_name = language_name[lang_code]    # Might be useful if the database if updated and medium language is stored using code
        else:
            lang_name = lang_code
        if lang_name in mlang_names:
            # if the language name is twice in the list for any reason then reject it. (Workaround)
            continue
        if lang_name == "":         # null values for languages are captured as "Other" 
            lang_name = "Other"  
        mlang_names.append(lang_name)
        mlang_counts.append(lang['count'])
    return mlang_names, mlang_counts

def getStudentClassStat(params = None):
    distinct = Question.objects.values('student_class').annotate(count=Count('student_class'))
    class_tuples = sorted([(tple['student_class'] if tple['student_class'] else "NA", tple['count']) for tple in distinct], key = lambda item : item[0])
    # Cleaning tuples as classes are stored as 10, 10.0 ... etc
    ## Can use: clases_names = {"4,5,6": "Primary", "10,11": "Secondary", "6,7,8": "Middle School" }.update({i:i for i in range(1,13)})
    dct = {i:0 for i in range(1,13)}
    for tple in class_tuples:
        student_class = tple[0]
        student_count = tple[1]
        if student_count < 20 : # 10 is arbitrary here. Change it as per the requirements. 
            # ignore if count of student from this class is less than 10 
            continue
        try:
            st_class = int(float(student_class))
        except:
            st_class = student_class
        dct[st_class] = (dct[st_class] + student_count) if st_class in dct else student_count
    return map(list, zip(*(dct.items())))


def getQuestionFormatStats():
    distinct = Question.objects.values('question_format').annotate(count=Count('question_format'))
    format_tuples = sorted([(tple['question_format'] if tple['question_format'] else "Other", tple['count']) for tple in distinct], key = lambda item : item[0])
    return map(list, zip(*format_tuples))

def getCurriculumStats():
    distinct = Question.objects.values('curriculum_followed').annotate(count=Count('curriculum_followed'))
    curriculum_tuples = sorted([(tple['curriculum_followed'] if tple['curriculum_followed'] else "Other", tple['count']) for tple in distinct], key = lambda item : item[0])
    return map(list, zip(*curriculum_tuples))

def getContextStats():
    distinct = Question.objects.values('context').annotate(count=Count('context'))
    context_tuples = sorted([
            (tple['context'] 
            if (tple['context'] and tple['context'] != "Other (elaborate in the Notes column)") 
            else "Other", tple['count']) for tple in distinct],
        key = lambda item : item[0])
    return map(list, zip(*context_tuples))

def getMapStats():
    distinct = Question.objects.values('state').annotate(count=Count('state'))    # place from where question is asked is in column state
    states, codes, counts = list(), list(), list()
    for stateCountPairDict in distinct:
        state = stateCountPairDict['state']
        if state.lower() not in state_code:
            continue
        states.append(state)
        codes.append(state_code[state.lower()])
        counts.append(stateCountPairDict['count'])
    return states, codes, counts

def getCountryStats():
    pass
    


