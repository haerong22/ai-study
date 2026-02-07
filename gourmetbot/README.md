## Multi AI Agent

### DB
- mariadb
```shell
docker run --name mariadb-vector-store -p 3306:3306 -e MARIADB_ROOT_PASSWORD=1234 -d mariadb:11.8
```

### mcp
- slack
```json
 {
    "mcpServers": {
      "slack": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-slack"
        ],
        "env": {
          "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
          "SLACK_TEAM_ID": "${SLACK_TEAM_ID}",
          "SLACK_CHANNEL_IDS": "${SLACK_CHANNEL_IDS}"
        }
      }
    }
  }
```