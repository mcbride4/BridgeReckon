from app import app
import os
import json
import time
from flask import Flask, jsonify, abort, request, render_template


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Maxiii'}  # fake user
    return render_template('index.html', title='Home', user=user)


@app.route('/table')
def table():
    print(os.getcwd())
    with open("app/static/style.css") as f:
        pass
    with open("app/helpers/json/distribution.json") as f:
        distribution = json.load(f)
    north = distribution['N']
    south = distribution['S']
    east = distribution['E']
    west = distribution['W']

    north_played = []
    south_played = []
    east_played = []
    west_played = []
    trick = []

    return render_template('table.html', title='Table X', north=north, south=south, east=east, west=west)

snapshots = [
    {
        'id': 1,
        'cards_played': [],
        'board': 1,
        'table': 1,
    },
    {
        'id': 2,
        'cards_played': [],
        'board': 1,
        'table': 1,
    },
]



@app.route('/snapshots', methods=['POST'])
def add_snapshot():
    if not request.json:
        abort(400)
    snapshot = {
        'id': snapshots[-1]['id'] + 1,
        'cards_played': request.json['cards_played'],
        'board': request.json.get('board', 1),
        'table': request.json.get('table', 1)
    }
    snapshots.append(snapshot)
    return jsonify({'snapshot': snapshot}), 201


@app.route('/snapshots', methods=['GET'])
def get_snapshots():
    return jsonify({'snapshots': snapshots})


@app.route('/snapshots/<int:snapshot_id>', methods=['GET'])
def get_snapshot(snapshot_id):
    snapshot = [snapshot for snapshot in snapshots if snapshot['id'] == snapshot_id]
    if len(snapshot) == 0:
        abort(404)
    return jsonify({'snapshot': snapshot[0]})


@app.route('/snapshots/lasts', methods=['GET'])
def get_two_last_snapshots():
    snapshot1 = snapshots[-1]
    snapshot2 = snapshots[-2]
    if not len(snapshot1) or not len(snapshot2):
        abort(404)
    return jsonify({'snapshots': [snapshot1, snapshot2]})


@app.route('/snapshots/cards_difference', methods=['GET'])
def get_cards_difference():
    if len(snapshots) <= 1:
        abort(404)
    snapshot_last = snapshots[-1]
    snapshot_last_but_one = snapshots[-2]
    cards_differences = {
        'cards_difference': list(set(snapshot_last_but_one['cards_played']) - set(snapshot_last['cards_played'])),
        'last_snapshot_id': snapshot_last['id'],
        'last_but_one_snapshot_id': snapshot_last_but_one['id'],
        'board': snapshot_last['board'],
        'table': snapshot_last['table'],
    }
    return jsonify({'cards_differences': cards_differences})

tricks = [
    {
        'id': 1,
        'table': None,
        'board': None,
        'tricks': {}
    }
]


@app.route('/tricks', methods=['GET'])
def get_all_tricks():
    return jsonify({'tricks': tricks})


@app.route('/tricks/<int:table_id>', methods=['GET'])
def get_tricks_table(table_id):
    ret = [board for i, board in tricks if board["table"] == table_id]
    return jsonify({'boards': ret})


@app.route('/tricks/<int:table_id>/<int:board>', methods=['GET'])
def get_tricks(table_id, board):
        for i in tricks:
            if i["table"] == table_id:
                if i["board"] == board:
                    return jsonify({'tricks': i})
        return jsonify({})


@app.route('/tricks', methods=['POST'])
def post_tricks():
    if not request.json:
        abort(400)
    board = {
        'id': tricks[-1]['id']+1,
        'tricks': request.json['tricks'],
        'board': request.json.get('board', 1),
        'table': request.json.get('table', 1),
        'trick_index': request.json.get('trick_index', 1)
    }
    updated = False
    for item in tricks:
        if item["table"] == board["board"]:
            if item["board"] == board["table"]:
                item["tricks"] = board["tricks"]
                item["trick_index"] = board["trick_index"]
                updated = True
    if not updated:
        tricks.append(board)
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
