import os
from datetime import datetime
from py2neo import Graph as Db
from gexf import Gexf, Graph, Node
from lxml import etree

db = Db(os.environ['DB_URI'])

def init_graph():
    graph = Graph('undirected', 'dynamic', 'friendships', 'dateTime', datetime(2014, 5, 15, 0, 0, 0).isoformat(), datetime(2014, 10, 2, 0, 0, 0).isoformat())

    # declare attributes
    graph.addNodeAttribute('nominated', type='boolean', mode='dynamic', force_id='nominated')
    graph.addNodeAttribute('completed', type='boolean', mode='dynamic', force_id='completed')
    graph.addNodeAttribute('donated', type='boolean', mode='dynamic', force_id='donated')
    graph.addNodeAttribute('isFirstDonation', type='boolean', mode='dynamic', force_id='isFirstDonation')

    return graph

def get_nodes():
    return db.find('Person')

def add_nodes_to_graph(graph):
    for db_node in get_nodes():
        id = str(db_node._id)
        node = Node(graph, str(db_node._id), db_node['name'])

        if 'timeNominated' in db_node.properties:
            node.addAttribute('nominated', "true", datetime.utcfromtimestamp(db_node['timeNominated']).isoformat())

        if 'timeCompleted' in db_node.properties:
            node.addAttribute('completed', "true", datetime.utcfromtimestamp(db_node['timeCompleted']).isoformat())

        if 'isFirstDonation' in db_node.properties:
            node.addAttribute('donated', "true", datetime.utcfromtimestamp(db_node['donationDate']).isoformat())
            node.addAttribute('isFirstDonation', "true" if db_node['isFirstDonation'] else "false", datetime.utcfromtimestamp(db_node['donationDate']).isoformat())

        graph.nodes[id] = node

def get_friendships():
    return db.match(rel_type='FRIENDS')

def add_friendships_to_graph(graph):
    for db_friendship in get_friendships():
        id = str(db_friendship._id)
        source_id = str(db_friendship.start_node._id)
        target_id = str(db_friendship.end_node._id)

        graph.addEdge(id, source_id, target_id, label='FRIENDS')

graph = init_graph()

gexf = Gexf('Brad Ross', 'A Network of Ice Bucket Challenges')
gexf.graphs.append(graph)

print 'GRAPH CREATED'

add_nodes_to_graph(graph)

print 'NODES ADDED'

add_friendships_to_graph(graph)

print 'FRIENDSHIPS ADDED'

output_file = open('graph.gexf', 'w')
gexf.write(output_file, print_stat=True)