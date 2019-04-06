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

function mkLoginParams() {
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

    return loginParams;
}

function Srv(onLogin) {
    this.snoozedOn = new Set();
    this.myId = null;
    this.api = null;

    this.sendTo = function(id) {
        this.api.getThreadHistory(id, 10, undefined, (err, history) => {
            if (err) return console.error(err);

            console.log("history:");
            console.log(history);

            ans({"history": history, "myId": this.myId} , (body) => {
                // console.log("processed:")
                // console.log(body.processed);

                d = body.ans.toString();
                console.log("sending: " + d);
                this.api.sendMessage(d, id);
            });
        });
    };

    this.snooze = function(id, now) {
        this.snoozedOn.add(id);
        if (now) {
            this.sendTo(id);
        }
    };

    this.unsnooze = function(id) {
        this.snoozedOn.delete(id);
    }

    login(mkLoginParams(), (err, api) => {
        if (err) return console.error(err);

        fs.writeFileSync("state.json", JSON.stringify(api.getAppState()));

        this.api = api;
        this.myId = api.getCurrentUserID();

        api.listen((err, msg) => {
            if (err) return console.error(err);

            if (this.snoozedOn.has(msg.threadID)) {
                this.sendTo(msg.threadID);
            }
        });

        onLogin(api);
    });
}

srv = new Srv((api) => {
    findBartosz(api, (id) => srv.snooze(id, false));
});
