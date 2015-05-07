import os
import json
from py2neo import Graph, Relationship

graph = Graph(os.environ['DB_URI'])

def file_exists(filename):
    return filename in [f for f in os.listdir('.') if os.path.isfile(f)]

def remove_post_from_db(post_id):
    graph.cypher.execute('''
        MATCH (post:Post) WHERE Id(post) = {postId}
        OPTIONAL MATCH (:Person)-[posted:POSTED]->(post)
        OPTIONAL MATCH (post)-[tagged:TAGGED]->(:Person)
        DELETE posted, tagged, post
    ''', {'postId': post_id})

def remove_posts_from_file(filename):
    removed_posts = json.load(open(filename, 'r'))
    for post_id in removed_posts:
        remove_post_from_db(post_id)

def get_posts():
    return [post for post in graph.find('Post')]

def start_filter(posts_removed_filename):
    posts = get_posts()
    removed_posts = []

    currPost = 0

    for post in posts:
        print '[POST ' + str(currPost) + ' of ' + str(len(posts)) + '] ' + post['message']

        isChallengePostInput = raw_input('\n  Is this an Ice Bucket Challenge Post? YES [enter]/NO [space]: ')

        if isChallengePostInput == ' ':
            removed_posts.append(post._id)
            remove_post_from_db(post._id)

        currPost += 1
        print '\n------------\n'

    removed_posts_file = open(posts_removed_filename, 'w')
    json.dump(removed_posts, removed_posts_file)

posts_removed_filename = 'posts_removed.json'

if file_exists(posts_removed_filename):
    remove_posts_from_file(posts_removed_filename)

start_filter(posts_removed_filename)