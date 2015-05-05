import os
from py2neo import Graph, Relationship

graph = Graph(os.environ['DB_URI'])

def get_survey_responses():
    return graph.find('SurveyResponse')

def find_person_with_name(name):
    return graph.find_one('Person', 'name', name)

def add_response_for_relationship(survey_response, person):
    rel = Relationship(survey_response, 'RESPONSE_FOR', person)
    graph.create_unique(rel)

def add_response_data_to_person(survey_response, person):
    person['didDonate'] = survey_response['didDonate']

    if survey_response['didDonate']:
        person['isFirstDonation'] = survey_response['isFirstDonation']
        person['donationDate'] = survey_response['donationDate']

    person.push()

def link_people_to_responses():
    for survey_response in get_survey_responses():
        person_to_link = find_person_with_name(survey_response["fbName"])

        if not person_to_link is None:
            add_response_for_relationship(survey_response, person_to_link)
            add_response_data_to_person(survey_response, person_to_link)
        else:
            print survey_response['fbName']

link_people_to_responses()