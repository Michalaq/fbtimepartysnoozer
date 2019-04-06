var request = require('request');

var options = {
    uri: 'http://localhost:5000/answer',
    method: 'POST',
    json: {
        "test": "test"
    }
};

request(options, function (error, response, body) {
  if (!error && response.statusCode == 200) {
    console.log(body);
  } else {
      console.log("err " + error + ", " + response.statusCode);
  }
});
