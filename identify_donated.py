import os
import json
from py2neo import Graph, Relationship

graph = Graph(os.environ['DB_URI'])

def get_posts():
    return graph.find('Post')

def find_donated_posts():
    donated_posts = []

    for post in get_posts():
        uppercase_message = post['message'].upper()
        if 'DONAT' in uppercase_message or 'GAVE' in uppercase_message or 'GIV' in uppercase_message:
            donated_posts.append(post)

    return donated_posts

def get_poster(post):
    rel = graph.match_one(rel_type='POSTED', end_node=post)
    return rel.start_node if not rel is None else None

def start_donation_filter(donated_posts):
    currPost = 0
    other_cause_posts = []

    for post in donated_posts:
        print '[POST ' + str(currPost) + ' of ' + str(len(donated_posts)) + '] ' + post['message']

        isChallengePostInput = raw_input('\n  Is this a Donation Post? YES [enter]/NO [space]/OTHER CAUSE [o]: ')

        if isChallengePostInput == '':
            poster = get_poster(post)
            if not poster is None:
                poster['didDonate'] = True
                poster['donationDate'] = post['timeCreated']
                poster.push()
        elif isChallengePostInput == 'o':
            other_cause_posts.append(post)

        currPost += 1
        print '\n------------\n'

    return other_cause_posts

other_cause_posts = start_donation_filter(find_donated_posts())
json.dump(other_cause_posts, open('other_cause_posts.json', 'w'))