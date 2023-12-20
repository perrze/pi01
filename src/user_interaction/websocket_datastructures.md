# Describe the data structure of json exchanged on the websocket

## From WS client
### Send information about user's orders
This type of data allow the client to tell the user interaction brain what direction and movement wants the user. 

Informations are sent using 2 float in [-1,1].

```json
{
    "type": "order",
    "position":{
        "forback": <float in [-1,1]>,
        "rotation": <float in [-1,1]>
    }
}
```

### Send a change of option
**Not used now**
Allow the client to signal a change in the option.  
For example coming from AI controlled to manually controlled.  

The content of data is not regulated.

```json
{
    "type": "option",
    "option": "<name of option>",
    "data":{} // Example of data
}
```

### Send a message to server stdout
Allow the client to write messages ato server stdout.  
Used for debug.

```json
{
    "type": "info",
    "content":"<Content of the message"
}
```

## From WS server
**Nothing for now...**