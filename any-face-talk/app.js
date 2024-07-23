const express = require('express');
const http = require('http');
const cors = require('cors');

const port = 1234;

const app = express();
app.use(cors({ origin: 'http://localhost:1234' }));

app.use('/', express.static(__dirname));

app.get('/', function(req, res) {
    res.sendFile(__dirname + '/index.html')
});
app.get('/any-face-talk', function(req, res) {
    res.sendFile(__dirname + '/index-agents.html')
});

const server = http.createServer(app);

server.listen(port, () => console.log(`Server started on port localhost:${port}\nhttp://localhost:${port}/any-face-talk`));
