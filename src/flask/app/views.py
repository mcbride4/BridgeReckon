from flask import render_template
from app import app
import os
import json
from flask import Flask, jsonify, abort, request


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
	with open("app/helpers/json/distribution.json") as file:
		distribution = json.load(file)
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

from flask import request

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


@app.route('/snapshots/last', methods=['GET'])
def get_snapshot_last():
    snapshot = snapshots[-1]
    if len(snapshot) == 0:
        abort(404)
    return jsonify({'snapshot': snapshot})


@app.route('/snapshots/last_but_one', methods=['GET'])
def get_snapshot_last_but_one():
    snapshot = snapshots[-2]
    if len(snapshot) == 0:
        abort(404)
    return jsonify({'snapshot': snapshot})


@app.route('/snapshots/cards_difference', methods=['GET'])
def get_cards_difference():
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