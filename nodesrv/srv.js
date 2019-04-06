const fs = require("fs");
const login = require("facebook-chat-api");
const request = require("request");
const readlineSync = require("readline-sync");
const express = require('express');
const cors = require('cors');

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
    this.startedYet = false;

    this.suggest = function(id, onMsg, onFail) {
        this.api.getThreadList(10, null, [], (err, list) => {
            for (var i = 0; i < list.length; ++i) {
                if (id == list[i].threadID) {
                    return this.api.getThreadHistory(id, 10, undefined, (err, history) => {
                        if (err) return console.error(err);

                        // console.log("history:");
                        // console.log(history);

                        ans({"history": history, "myId": this.myId} , (body) => {
                            // console.log("processed:")
                            // console.log(body.processed);

                            d = body.ans.toString();
                            onMsg(d);
                        });
                    });
                }
            }

            var failMsg = "No such threadID";
            console.log(failMsg);
            onFail(failMsg);
        });

    };

    this.sendTo = function(id, onSend, onFail) {
        this.suggest(id, (msg) => {
            console.log("sending: " + d);
            this.api.sendMessage(d, id);

            if (onSend) {
                onSend(d);
            }
        }, onFail);
    };

    this.snooze = function(id, now) {
        this.snoozedOn.add(id);
        if (now) {
            this.sendTo(id);
        }
    };

    this.unsnooze = function(id) {
        this.snoozedOn.delete(id);
    };

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

        this.startedYet = true;

        onLogin(api);
    });
}

srv = new Srv((api) => {
    findBartosz(api, (id) => srv.snooze(id, false));
});

const app = express();
const port = 3000;
const notStartedMsg = "Server not started yet, try again in a second";
const corsOptions = {
    origin: '*',
    credentials:  true
};

app.use(cors(corsOptions));

app.post('/snooze/:userId', (req, res) => {
    if (!srv.startedYet) {
        res.status(503).send(notStartedMsg);
        return;
    }

    srv.snooze(req.params.userId, false);
    res.send("Snoozed");
});

app.post('/unsnooze/:userId', (req, res) => {
    srv.unsnooze(req.params.userId);
    res.send("Unsnoozed");
});

app.post('/send/:userId', (req, res) => {
    if (!srv.startedYet) {
        res.status(503).send(notStartedMsg);
        return;
    }

    srv.sendTo(
        req.params.userId,
        (msg) => res.send("Sent: " + msg + "\n"),
        (msg) => res.send("Failed: " + msg + "\n")
    );
});

app.get('/suggest/:userId', (req, res) => {
    if (!srv.startedYet) {
        res.status(503).send(notStartedMsg);
        return;
    }

    srv.suggest(
        req.params.userId,
        (msg) => res.send(msg + "\n"),
        (msg) => res.send("Failed: " + msg + "\n")
    );
});

app.get('/lastUsers', (req, res) => {
    if (!srv.startedYet) {
        res.status(503).send(notStartedMsg);
        return;
    }

    srv.api.getThreadList(15, null, [], (err, list) => {
        users = [].concat.apply([],
            list.filter((t) => { return !t.isGroup; })
                .map((t) => { return t.participants.filter((p) => { return p.accountType == "User"; }); }))
                .filter((p) => { return p.userID != srv.myId; });

        console.log(users);

        res.send(users.map((u) => {
            return {
                "userID": u.userID,
                "pic": u.profilePicture,
                "name": u.name,
                "snoozed": srv.snoozedOn.has(u.userID)
            };
        }));
    });
});

app.listen(3000);
