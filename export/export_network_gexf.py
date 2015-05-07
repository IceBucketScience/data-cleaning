import os
from datetime import datetime
from py2neo import Graph as Db
from gexf import Gexf, Graph, Node, Edge
from lxml import etree

db = Db(os.environ['DB_URI'])

def init_graph():
    graph = Graph('undirected', 'dynamic', 'friendships', 'dateTime', datetime(2014, 5, 15, 0, 0, 0).isoformat(), datetime(2014, 10, 2, 0, 0, 0).isoformat())

    # declare attributes
    graph.addNodeAttribute('challenge_status', type='string', mode='dynamic', force_id='challenge_status')
    graph.addNodeAttribute('donated', type='boolean', mode='dynamic', force_id='donated')
    graph.addNodeAttribute('is_first_donation', type='boolean', mode='dynamic', force_id='is_first_donation')

    graph.addEdgeAttribute('nomination', None, type='boolean', mode='dynamic', force_id='nomination')

    return graph

def get_nodes():
    return db.find('Person')

def add_nodes_to_graph(graph):
    for db_node in get_nodes():
        id = str(db_node._id)
        node = Node(graph, str(db_node._id), db_node['name'])

        if 'timeCompleted' in db_node.properties:
            time_nominated = datetime.utcfromtimestamp(db_node['timeNominated']).isoformat()
            time_completed = datetime.utcfromtimestamp(db_node['timeCompleted']).isoformat()

            if time_nominated != time_completed:
                node.addAttribute('challenge_status', 'nominated', datetime.utcfromtimestamp(db_node['timeNominated']).isoformat(), time_completed, endopen=True)
                node.addAttribute('challenge_status', 'completed', time_completed)
            else:
                node.addAttribute('challenge_status', 'completed', time_completed)
        elif 'timeNominated' in db_node.properties:
            node.addAttribute('challenge_status', 'nominated', datetime.utcfromtimestamp(db_node['timeNominated']).isoformat())

        if 'didDonate' in db_node.properties and db_node.properties['didDonate']:
            node.addAttribute('donated', 'true', datetime.utcfromtimestamp(db_node['donationDate']).isoformat())
            node.addAttribute('is_first_donation', 'true' if db_node['is_first_donation'] else "false", datetime.utcfromtimestamp(db_node['donationDate']).isoformat())

        graph.nodes[id] = node

def get_friendships():
    return db.match(rel_type='FRIENDS')

def add_friendships_to_graph(graph):
    for db_friendship in get_friendships():
        id = str(db_friendship._id)
        source_id = str(db_friendship.start_node._id)
        target_id = str(db_friendship.end_node._id)

        edge = Edge(graph, id, source_id, target_id, label='FRIENDS')

        nomination = db.match_one(db_friendship.start_node, 'NOMINATED', db_friendship.end_node, bidirectional=True)

        if not nomination is None:
            edge.addAttribute('nomination', 'true', datetime.utcfromtimestamp(nomination['timeNominated']).isoformat())

        graph.edges[id] = edge

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