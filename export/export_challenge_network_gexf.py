import os
from datetime import datetime
from py2neo import Graph as Db
from gexf import Gexf, Graph, Node, Edge

db = Db(os.environ['DB_URI'])

def init_graph():
    graph = Graph('directed', 'dynamic', 'challenge', 'dateTime', datetime(2014, 5, 15, 0, 0, 0).isoformat(), datetime(2014, 10, 2, 0, 0, 0).isoformat())

    # declare attributes
    graph.addNodeAttribute('challenge_status', type='string', mode='dynamic', force_id='challenge_status')

    return graph

def get_challenge_participants():
    return [node_data.p for node_data in db.cypher.execute('MATCH (p:Person) WHERE has(p.timeNominated) RETURN p')]

def add_participants_to_graph(graph):
    for db_node in get_challenge_participants():
        id = str(db_node._id)
        node = Node(graph, id, db_node['name'], datetime.utcfromtimestamp(db_node['timeNominated']).isoformat())

        if 'didDonate' in db_node.properties and db_node['didDonate']:
            node.addAttribute('challenge_status', 'donated', datetime.utcfromtimestamp(db_node['donationDate']).isoformat())
        elif 'timeCompleted' in db_node.properties:
            node.addAttribute('challenge_status', 'completed', datetime.utcfromtimestamp(db_node['timeCompleted']).isoformat())

        graph.nodes[id] = node

def get_nominations():
    return db.match(rel_type='NOMINATED')

def add_nominations_to_graph(graph):
    for db_nomination in get_nominations():
        id = str(db_nomination._id)
        source_id = str(db_nomination.start_node._id)
        target_id = str(db_nomination.end_node._id)

        graph.addEdge(id, source_id, target_id, start=datetime.utcfromtimestamp(db_nomination['timeNominated']).isoformat(), label='NOMINATED')

graph = init_graph()

gexf = Gexf('Brad Ross', 'A Network of Ice Bucket Challenges')
gexf.graphs.append(graph)

add_participants_to_graph(graph)
add_nominations_to_graph(graph)

output_file = open('nomination_graph.gexf', 'w')
gexf.write(output_file, print_stat=True)