const express = require('express');
const cors = require('cors');
const app = express();
const server = require('http').createServer(app);
const env = process.env.NODE_ENV || 'development';
const config = require('../knexfile')[env];
const knex = require('knex')(config);


app.use(cors());
app.use(express.json());
app.use(cookieParser());

app.get('/', (request, response) => {
    response
        .status(200)
        .send('App root route running');
});


module.exports = server;