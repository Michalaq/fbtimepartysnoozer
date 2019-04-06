var request = require('request');

function ans(j, callback) {
    var options = {
        uri: 'http://localhost:5000/answer',
        method: 'POST',
        json: j
    };

    request(options, function (error, response, body) {
      if (!error && response.statusCode == 200) {
          callback(body);
      } else {
          console.log("err " + error + ", " + response.statusCode);
      }
    });
}

ans({"test": "test"}, (body) => { console.log(body); });
