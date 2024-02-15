## How to prepare your OptScale cluster for Slack integration

1. Go to https://api.slack.com/apps to create a new Slack app. Enter a name and pick a workspace.

2. In the "OAuth & Permissions" tab paste a local cluster oauth_redirect slacker URL https://<public_cluster_ip>/slacker/v2/oauth_redirect to the "Redirect URLs" field. In the "Scopes" section add "Bot Token Scopes" permissions (`chat:write`, `im:history`, `chat:write.public`, `groups:write`, `channels:read`, `groups:read`).

3. In the "Interactivity & Shortcuts" tab enable the "Interactivity" switch and paste a cluster slacker event URL https://<public_cluster_ip>/slacker/v2/events to the "Request URL" field.

4. Update the optscale/optscale-deploy/overlay/user_template.yml overlay with "Client ID", "Client Secret", "Signing Secret" values from the "Basic Information" tab in "App Credentials" section.
```
slacker:
  slack_signing_secret:
  slack_client_id:
  slack_client_secret:
```

5. Update your cluster with the new overlay:
`./runkube.py --with-elk --update-only <deployment name> <version>`

6. In the "Event Subscriptions" tab enable the "Enable Events" switch and paste a slacker events URL https://<public_cluster_ip>/slacker/v2/events to the "Request URL" field. Expand the "Subscribe to bot events" panel and add the following event types: `app_home_opened`, `message.im`, `member_joined_channel`.

7. In the "App Home" tab disable the "Home Tab" switch, enable the "Messages Tab" switch. In the "Messages Tab" tab check "Allow users to send Slash commands and messages from the messages tab".
