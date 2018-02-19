### Update this to reflect this repos info/instructions
### Intro

This Slackbot is a slash command that reacts to the last message in the given channel with a bunch of reactions.

### Usage

```
/react #_reactions
/react 22
```

### Installation

1. Clone this repository and `cd` into it
2. Create a file called setup.cfg (`touch setup.cfg`) with the following content
```
[install]
prefix= 
```
3. Run the following command to install dependencies
``` 
pip install -t . -r requirements.txt
```
4. Archive the all the files/folders in the directory into a zip file
5. Follow this [tutorial](https://medium.com/@cu_tech/create-a-slack-slash-command-with-aws-lambda-83fb172f9a74) to setup Lambda and setup an API Gateway Trigger.
	* Use Python 2.x instead of NodeJS
	* Under code entry type select `Upload a .ZIP file` and upload the file created in step 5
	* Set the handler as `react_bot.lambda_handler`
6. Create a 2nd function with the name `slackReactReceiver`
	* Use Python 2.x as the runtime
	* Upload the same zip file
	* Set the handler as `react_action.lambda_handler`
7. [Create a slackbot](https://api.slack.com/apps) and add a slash command.
	* Set the endpoint as your API Gateway Endpoint given on the Lambda function created on step 6