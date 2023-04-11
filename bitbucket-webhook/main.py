from flask import Flask, request, jsonify
import json
import os 
import requests
import configparser
import hmac
import hashlib
import re

app = Flask(__name__)

config = configparser.ConfigParser(allow_no_value=True, strict=False)
config.read(os.environ.get('CONFIG_FILE', 'config.ini'))
config.read(os.environ.get('BUILD_FILE', 'pyproject.toml'))

jenkins_url = config['Jenkins']['url']
jenkins_username = config['Jenkins']['username']
jenkins_api_token = config['Jenkins']['api_token']
secret_key = config['Webhook']['secret']
branch_filter_enabled = config.getboolean('Webhook', 'branch_filter_enabled')
branch_filter_list = [b.strip() for b in config['Webhook']['branch_filter'].split(',')]
app_version = config['tool.poetry']['version']

# Print all config variables at startup
for section in config.sections():
    print(f"[{section}]")
    for key, value in config.items(section):
        if key in ["api_token","secret"]: 
           value = "************" 
        print(f"{key} = {value}")
    print()

@app.route('/filter')
def get_filter():
    return jsonify({'branch-filter': branch_filter_list}), 200

@app.route('/version')
def get_version():
    return jsonify({'version': app_version.strip('"')}), 200

@app.route('/jenkins-webhook', methods=['POST'])
def handle_webhook():
    headers = request.headers
    event = headers.get('X-Event-Key')
    signature = headers.get('X-Hub-Signature')
    if event == 'repo:push':
        payload = request.get_data()
        if is_valid_signature(payload, signature):
            print("Payload received:")
            print(request.get_json())
            for commit in request.get_json()['push']['changes']:
                branch_name = commit['new']['name']
                if commit['new']['type'] != 'branch':
                    print(f"Skipping build for {branch_name} as it is not a branch")
                    continue
                if branch_filter_enabled:
                    if not any(re.match(pattern, branch_name) for pattern in branch_filter_list):
                        print(f"Skipping build for branch {branch_name} because it does not match the filter criteria.")
                        msg = f"Skipping build for branch {branch_name} because it does not match the filter criteria."
                        continue
                if request.args.get('dryrun'):
                    print(f"Dryrun mode is enabled. Would trigger build for {branch_name}@{jenkins_url}.")
                    msg = f"Dryrun mode is enabled. Would trigger build for {branch_name}@{jenkins_url}."
                else:
                    trigger_jenkins_build(branch_name)
                    msg = "triggering jenkins build for {branch_name}@{jenkins_url}."
            return jsonify({'message': msg}), 200
        else:
            return "Invalid signature", 401
    else:
        return "Unhandled event", 200

def is_valid_signature(payload, signature):
    digest = hmac.new(secret_key.encode(), payload, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={digest}"
    return hmac.compare_digest(expected_signature, signature)

def trigger_jenkins_build(branch_name):
    job_name = 'my-parameterized-job'
    build_with_parameters_url = f'{jenkins_url}/job/{job_name}/buildWithParameters'
    build_params = {'branch_name': branch_name}
    auth = (jenkins_username, jenkins_api_token)
    response = requests.post(build_with_parameters_url, params=build_params, auth=auth)
    if response.status_code == 201:
        print(f"Build triggered successfully for branch {branch_name}")
    else:
        print(f"Failed to trigger build for branch {branch_name}. Response code: {response.status_code}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.getint('Webhook', 'port'))
