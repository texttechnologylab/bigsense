from flask import Flask, jsonify, request
import argparse
import ned
from flask_cors import CORS

arg_parser = argparse.ArgumentParser(description="NED Server")
arg_parser.add_argument("--model", type=str, required=True, help="Path to model")
arg_parser.add_argument("--worker_count", type=int, required=False, help="Number of NN instances")
args = arg_parser.parse_args()

USE_CORENLP = True

corenlp_bridge = None
if USE_CORENLP:
	corenlp_bridge = ned.CoreNlpBridge("../stanford-corenlp-full-2017-06-09/stanford-corenlp-3.8.0.jar:../stanford-corenlp-full-2017-06-09/stanford-corenlp-3.8.0-models.jar")

disambiguator = ned.Disambiguator(args.model, corenlp_bridge=corenlp_bridge, worker_count=args.worker_count)

app = Flask(__name__)
CORS(app)


def json_to_token(token_json) -> ned.Token:
	return ned.Token(
		start=token_json[0],  # Start index
		end=token_json[1],  # End index
		value=token_json[2],  # Token value
		pos=token_json[3],  # Stanford Tagger PoS Tag
		lemma=None,  # Not used by best model, therefore ignored
		before=token_json[4],  # Whitespace/Non-Token before token (e.g. " " or "")
		after=token_json[5]   # Whitespace/Non-Token after token (e.g. " " or "")
	)


@app.route("/")
def hello():
	return "https://github.com/texttechnologylab"


@app.route('/disambiguate', methods=("POST",))
def disambiguate():
	"""
	Expects JSON input in POST body in following format:

	List of segments (i.e. paragraphs).
	Each segment is a list containing tokens.
	Each token is a list containing 6 items:
	[Start Index, End Index, Token Value, PoS Tag (Stanford Tagger), WHitespace Before, WHitespace After]

	:return: JSON list containing dicts with start, end and url keys.
	"""
	input_json_temp = request.get_json(force=True)
	input_json = input_json_temp["paragraphs"]
	
	process_with_corenlp = input_json_temp["use_corenlp"] if "use_corenlp" in input_json_temp else False
	
	if USE_CORENLP and process_with_corenlp:
		results = disambiguator.disambiguate(input_json)
	else:
		input_paragraphs = list(map(lambda segment: list(map(lambda token_json: json_to_token(token_json), segment)), input_json))
		results = disambiguator.disambiguate_tokenized_segments(input_paragraphs)

	return jsonify({"results": list(map(lambda x: {"start": x[0], "end": x[1], "url": x[2]}, results))})


if __name__ == "__main__":
	app.run(host='0.0.0.0', port='80')
