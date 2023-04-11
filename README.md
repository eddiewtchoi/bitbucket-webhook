# Jenkins Webhook

This is a webhook server that listens for `repo:push` events from Bitbucket and triggers a Jenkins job with parameters for the branch that was pushed.

## Getting Started

To get started with this webhook server, follow these steps:

1. Install Python 3 and pip.
2. Clone this repository: `git clone https://github.com/example/jenkins-webhook.git`
3. Install the required Python packages: `pip install -r docs/requirements.txt`
4. Set up a parameterized Jenkins job that accepts a `branch_name` parameter.
5. Create a `config.ini` file in the project root with the following contents, location of the config file can be defined using ENVIRONMENT variable CONFIG_FILE:

```
[Jenkins]
url = http://jenkins.example.com
username = jenkins_user
api_token = jenkins_api_token

[Webhook]
port = 5000
secret = my_webhook_secret
branch_filter_enabled = true
branch_filter = (.*-dev|.*-sit)$
```


6. Replace the values in the `config.ini` file with your own values.
7. Run the webhook server: `python webhook.py`
8. Create a webhook in your Bitbucket repository settings that points to your server's URL (`http://your_server_url/webhook`). The webhook should be set to trigger on `repo:push` events and should use the `application/json` payload format.
9. Push a branch to the repository that matches one of the filters defined in `config.ini`.

## Configuration

The webhook server can be configured using the `config.ini` file. The following options are available:

### Jenkins

- `url`: The URL of your Jenkins server.
- `username`: The username to use when authenticating with Jenkins.
- `api_token`: The API token to use when authenticating with Jenkins.

### Webhook

- `port`: The port that the webhook server should listen on.
- `secret`: The secret key used to sign the webhook payload.
- `branch_filter_enabled`: If set to `true`, the webhook server will only trigger a build for branches that match the `branch_filter` list.
- `branch_filter`: A comma-separated list of branch names to trigger builds for when `branch_filter_enabled` is set to `true`.

