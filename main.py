import os
from flask import Flask, jsonify, request
import json
import datetime
from dotenv import load_dotenv
from Job import MyJob

load_dotenv()

app = Flask(__name__)

jobs = []


@app.route("/", methods=['POST'])
def entry():
    # name = os.environ.get("NAME", "World")
    record = json.loads(request.data)

    def sublist(lst1, lst2):
        return set(lst1) <= set(lst2)

    if sublist(['user', 'playlist_id', 'project_name'], record.keys()):
        # if these things are in the post request
        if "threshold" in record:
            threshold = record['threshold']
        else:
            threshold = 5

        if 'num_threads' in record:
            num_threads = record['num_threads']
        else:
            num_threads = 3

        if 'debug' in record:
            debug = record['debug']
        else:
            debug = False

        job_id = len(jobs)
        job = MyJob(job_id=job_id, user=record['user'], playlist_id=record['playlist_id'],
                    project_name=record['project_name'], threshold=threshold, num_threads=num_threads, debug=debug)
        jobs.append(job)
        print(job.to_dict())
        return jsonify(job.to_dict())

    elif 'job_id' in record:
        for job in jobs:
            if job.job_id == record['job_id']:
                return jsonify(job.to_dict())
            # idk probably wont ever do anything cloud run will shutdown before running for a day
            # just to make me feel better
            if job.end_time > datetime.datetime.now() + datetime.timedelta(days=1):
                print(f"DELETING {job}")
                jobs.remove(job)
                del job

        return jsonify({'status': 'No job found'})

    else:
        return jsonify({'status': 'Error incorrect parameters'})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
