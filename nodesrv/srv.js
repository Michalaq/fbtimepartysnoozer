const fs = require("fs");
const login = require("facebook-chat-api");
const request = require("request");
const readlineSync = require("readline-sync");

function ans(j, onRespBody) {
    var options = {
        uri: "http://localhost:5000/answer",
        method: "POST",
        json: j
    };

    request(options, function (error, response, body) {
      if (!error && response.statusCode == 200) {
          onRespBody(body);
      } else {
          console.log("err " + error);
          console.log("statusCode: " + response.statusCode);
      }
    });
}

function findBartosz(api, onId) {
    api.getUserID("Bartosz Michalak", (err, data) => {
        if (err) return console.error(err);

        for (var i = 0; i < data.length; i++) {
            console.log("url: " + data[i].profileUrl);
            if (data[i].profileUrl == "https://www.facebook.com/michalaq") {
                var id = data[i].userID;
                console.log("Bartosz' id: " + id);
                return onId(id);
            }
        }
    });
}

loginParams = {};

try {
    state = JSON.parse(fs.readFileSync("state.json", "utf8"));
    loginParams.appState = state;
} catch (err) {
    console.log("err getting old state: " + err);
    console.log("Login required");
    var email = readlineSync.question("email: ");
    var passw = readlineSync.question("password: ", {hideEchoBack: true});
    loginParams.email = email;
    loginParams.password = passw;
}

login(loginParams, (err, api) => {
    if (err) return console.error(err);

    fs.writeFileSync("state.json", JSON.stringify(api.getAppState()));

    var myId = api.getCurrentUserID();

    findBartosz(api, (id) => {
        api.listen((err, msg) => {
            if (err) return console.error(err);

            if (msg.senderID == id) {
                api.getThreadHistory(id, 10, undefined, (err, history) => {
                    if (err) return console.error(err);

                    console.log("history:");
                    console.log(history);


                    ans({"history": history, "myId": myId} , (body) => {
                        // console.log("processed:")
                        // console.log(body.processed);

                        d = body.ans.toString();
                        console.log("sending: " + d);
                        api.sendMessage(d, id);
                    });
                });
            }
        });

    });
});
