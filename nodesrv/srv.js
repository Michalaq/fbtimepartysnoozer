const fs = require("fs");
const login = require("facebook-chat-api");
const request = require("request");
const readlineSync = require("readline-sync");
const express = require('express');
const cors = require('cors');

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

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

    this.findThread = function(id, onThread, onFail) {
        this.api.getThreadList(10, null, [], (err, list) => {
            if (!list.some((t) => { return t.threadID == id; })) {
                const failMsg = "No such threadID";
                console.log(failMsg);
                if (onFail) {
                    onFail(failMsg);
                }
                return;
            }

            this.api.getThreadHistory(id, 10, undefined, (err, history) => {
                if (err) return console.error(err);

                return onThread(history);
            });
        });
    }

    this.suggest = function(id, onMsg, onFail) {
        return this.findThread(id, (history) => {
            // console.log("history:");
            // console.log(history);

            ans({"history": history, "myId": this.myId} , (body) => {
                // console.log("processed:")
                // console.log(body.processed);

                var d = body.ans.toString();
                onMsg(d);
            });
        }, onFail);
    };

    this.sendTo = function(id, onSend, onFail) {
        this.suggest(id, (msg) => {
            console.log("sending: " + msg);
            setTimeout(() => {
                this.api.markAsRead(id, true, (err) => {
                    if (err) return console.error(err);

                    setTimeout(() => {
                        console.log("marked as read");
                        end = this.api.sendTypingIndicator(id, (err) => {
                            if (err) return console.error(err);
                        });

                        setTimeout(() => {
                            end();
                            this.api.sendMessage(msg, id);

                            if (onSend) {
                                onSend(msg);
                            }
                        }, getRandomInt(3000, 4000));
                    }, getRandomInt(1000, 3000));
                });
            }, getRandomInt(0, 1000));
        }, onFail);
    };

    this.snooze = function(id) {
        this.snoozedOn.add(id);
        this.sendTo(id);
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
    return;
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
    res.send("Snoozed\n");
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
