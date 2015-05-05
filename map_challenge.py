import os
from py2neo import Graph, Relationship, watch

#watch('httpstream')

graph = Graph(os.environ['DB_URI'])

def get_posts_in_order():
    unordered_posts = [post for post in graph.find('Post')]
    return sorted(unordered_posts, key=lambda post: post['timeCreated'])

def get_poster(post):
    raw_rel = graph.match_one(rel_type='POSTED', end_node=post)

    return raw_rel.start_node if not raw_rel is None else None

def get_tagged(post):
    tagged = graph.match(rel_type='TAGGED', start_node=post)

    return [tagged_rel.end_node for tagged_rel in tagged]

def create_nomination_rel(poster, post, tagged_person):
    rel = Relationship(poster, 'NOMINATED', tagged_person, timeNominated=post['timeCreated'])
    graph.create_unique(rel)

def map_tagged(post, poster, tagged):
    for tagged_person in tagged: 
        if not 'timeNominated' in tagged_person.properties or post['timeCreated'] < tagged_person['timeNominated']:
            tagged_person['timeNominated'] = post['timeCreated']
            tagged_person.push()

        if not poster is None and not 'timeCompleted' in tagged_person.properties:
            create_nomination_rel(poster, post, tagged_person)

def map_nominations():
    for post in get_posts_in_order():
        poster = get_poster(post)

        if not poster is None:
            poster['timeCompleted'] = post['timeCreated']

            if not 'timeNominated' in poster.properties:
                poster['timeNominated'] = post['timeCreated']

            poster.push()

        tagged = get_tagged(post)

        map_tagged(post, poster, tagged)

map_nominations()