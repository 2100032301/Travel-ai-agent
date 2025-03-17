# server.py
from flask import Flask, request, jsonify, send_from_directory
import asyncio
from travel import run_travel_planner

app = Flask(__name__, static_folder="frontend", static_url_path="")

# Serve the frontend (index.html)
@app.route("/")
def serve_frontend():
    return send_from_directory("frontend", "index.html")

# API endpoint to handle user tasks and return the agents' responses
@app.route("/api/plan", methods=["POST"])
def plan_travel():
    data = request.get_json()
    task = data.get("task", "")
    if not task:
        return jsonify({"error": "Task is required"}), 400

    try:
        # Run the travel planner and get the responses
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(run_travel_planner(task))
        loop.close()

        return jsonify({"responses": responses})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)