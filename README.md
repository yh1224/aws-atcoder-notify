# AWS AtCoder Notify Streak

![](screenshot.png)

## Deploy

```shell
sam build (--use-container)
sam deploy (--guided)
```

### Parameters

|Name|Default|Description|
|:--|:--|:--|
|AtCoderUsername|(none)|AtCoder username (required)|
|SlackWebhookUrl|(none)|Slack Webhook URL to notify. (can be ommitted)|
