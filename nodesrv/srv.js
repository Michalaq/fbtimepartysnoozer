var request = require('request');

function ans(j) {
    var options = {
        uri: 'http://localhost:5000/answer',
        method: 'POST',
        json: j
    };

    request(options, function (error, response, body) {
      if (!error && response.statusCode == 200) {
        console.log(body);
      } else {
          console.log("err " + error + ", " + response.statusCode);
      }
    });
}

ans({"test": "test"});
