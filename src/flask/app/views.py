from app import app
import json
from pymongo import MongoClient
from flask import Flask, jsonify, abort, request, render_template


def get_next_snapshot_id(raspberry_id, camera_id):
    ids = snapshots.find({'raspberry_id': raspberry_id, 'camera_id': camera_id}, {'id': 1, '_id': 0})
    print(ids)
    if not ids.count():
        return 0
    else:
        return max([i['id'] for i in ids]) + 1


client = MongoClient('localhost', 27017)
db = client.bridge
snapshots = db.snapshots
tricks = db.tricks

snapshots.insert_one(
    {
        'id': get_next_snapshot_id("a", "f"),
        'raspberry_id': "fdsa",
        'camera_id': "dfsafd",
        'cards': [('AH', 3), ('3C', 4), ('2H', 2), ('QD', 1), ('5C', 1), ('QH', 2)]
    }
)
tricks.insert_one(
    {
        'id': 1,
        'table': None,
        'board': None,
        'tricks': {}
    }
)


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Maxiii'}  # fake user
    return render_template('index.html', title='Home', user=user)


@app.route('/table', methods=['GET'])
def table():
    with open("app/helpers/json/distribution.json") as f:
        distribution = json.load(f)
    north = distribution['N']
    south = distribution['S']
    east = distribution['E']
    west = distribution['W']

    return render_template('table.html', title='Table X', north=north, south=south, east=east, west=west)


@app.route('/table/<int:table_id>', methods=['GET'])
def table_id(table_id):
    with open("app/helpers/json/distribution.json") as f:
        distribution = json.load(f)
    north = distribution['N']
    south = distribution['S']
    east = distribution['E']
    west = distribution['W']

    return render_template('table.html', title='Table {}'.format(table_id),
                           north=north, south=south, east=east, west=west, table_id=table_id)


@app.route('/distribution/<int:board_id>', methods=['GET'])
def get_distribution(board_id):
    with open("app/helpers/json/distribution_vugraph.lin.json") as f:
        distribution_segment = json.load(f)
    room = "c"
    distribution = distribution_segment[room][str(board_id)][0]
    return jsonify(distribution)


@app.route('/snapshots', methods=['POST'])
def add_snapshot():
    if not request.json:
        abort(400)
    raspberry_id = request.json['raspberry_id']
    camera_id = request.json['camera_id']
    cards = request.json['cards']
    snapshot = {
        'id': get_next_snapshot_id(raspberry_id, camera_id),
        'cards': cards,
        'camera_id': camera_id,
        'raspberry_id': raspberry_id
    }
    snapshots.insert_one(snapshot)
    del snapshot["_id"]
    return jsonify(snapshot), 201


@app.route('/snapshots', methods=['GET'])
def get_snapshots():
    return snapshots.find({}, {'_id': 0})


@app.route('/snapshots/<int:snapshot_id>', methods=['GET'])
def get_snapshot(snapshot_id):
    snap1 = snapshots.find({"id": snapshot_id}, {'_id': 0})
    print("snap 1 here {}".format(snap1))
    snap2 = snapshots.find({"id": snapshot_id-1}, {'_id': 0})
    print("snap 2 here {}".format(snap2))
    if snap1 is None or snap2 is None:
        abort(404)
    snaps = [[i for i in snap1], [i for i in snap2]]
    print("snaps: {}".format(snaps))
    return jsonify({'snapshots': snaps})


@app.route('/tricks', methods=['GET'])
def get_all_tricks():
    return tricks.find()


@app.route('/snapshots/<int:raspberry_id>/<int:snapshot_id>', methods=['GET'])
def get_snapshot_raspberry(raspberry_id, snapshot_id):
    snap1 = snapshots.find({"raspberry_id": raspberry_id, "id": snapshot_id}, {'_id': 0})
    snap2 = snapshots.find({"raspberry_id": raspberry_id, "id": snapshot_id-1}, {'_id': 0})
    if snap1 is None or snap2 is None:
        abort(404)
    snaps = []
    cards_snap1 = []
    cards_snap2 = []
    for snap in snap1:
        cards_snap1 += snap['cards']
    for snap in snap2:
        cards_snap2 += snap['cards']
    snaps.append({
        'id': snapshot_id,
        'raspberry_id': raspberry_id,
        'cards': cards_snap1
    })
    snaps.append({
        'id': snapshot_id-1,
        'raspberry_id': raspberry_id,
        'cards': cards_snap2
    })
    print("returnning snaps {}".format(snaps))
    return jsonify({'snapshots': snaps})


@app.route('/tricks/<int:table_id>', methods=['GET'])
def get_tricks_table(table_id):
    # ret = [board for i, board in tricks if board["table"] == table_id]
    ret = tricks.find_one({"table": table_id})
    return jsonify({'boards': ret})


@app.route('/tricks/<int:table_id>/<int:board>', methods=['GET'])
def get_tricks(table_id, board):
    t1 = tricks.find({"table": table_id, "board": str(board)}, {'_id': 0}).sort([("trick_index", -1)])
    try:
        return jsonify({'tricks': t1[0]})
    except IndexError:
        abort(404)


@app.route('/tricks', methods=['POST'])
def post_tricks():
    if not request.json:
        abort(400)
    board = {
        # 'id': tricks.find_one({"id": 1}, {"_id": 0}),  # tricks[-1]['id']+1,
        'tricks': request.json['tricks'],
        'board': request.json.get('board', 1),
        'table': request.json.get('table', 1),
        'trick_index': request.json.get('trick_index', 1)
    }
    updated = False
    # for item in tricks.find({}, {"board": 1, "table": 1, "tricks": 1, "tricks_index": 1, "_id": 0}):
    for item in tricks.find({}, {"_id": 0}):
        if item["table"] == board["board"]:
            if item["board"] == board["table"]:
                item["tricks"] = board["tricks"]
                item["trick_index"] = board["trick_index"]
                updated = True
    if not updated:
        tricks.insert_one(board)
        del board['_id']
    return jsonify({'tricks': board}), 201


'''
@app.route('/snapshots/cards_played', methods=['GET'])
def get_cards_played():
    if len(snapshots) <= 1:
        abort(404)
    snapshot_last = snapshots[-1]
    snapshot_last_but_one = snapshots[-2]
    cards_differences = {
	    'cards_difference' : list(set(snapshot_last_but_one['cards_played']) - set(snapshot_last['cards_played'])),
	    'last_snapshot_id' : snapshot_last['id'],
	    'last_but_one_snapshot_id' : snapshot_last_but_one['id'],
	    'board' : snapshot_last['board'],
	    'table' : snapshot_last['table'],
    }
    return jsonify({'cards_differences': cards_differences})


@app.route('/snapshots/cards_played/<int:player_id>', methods=['GET'])
def get_cards_played():
    if len(snapshots) <= 1:
        abort(404)
    snapshot_last = snapshots[-1]
    snapshot_last_but_one = snapshots[-2]
    cards_differences = {
	    'cards_difference' : list(set(snapshot_last_but_one['cards_played']) - set(snapshot_last['cards_played'])),
	    'last_snapshot_id' : snapshot_last['id'],
	    'last_but_one_snapshot_id' : snapshot_last_but_one['id'],
	    'board' : snapshot_last['board'],
	    'table' : snapshot_last['table'],
    }
    return jsonify({'cards_differences': cards_differences})


'''
