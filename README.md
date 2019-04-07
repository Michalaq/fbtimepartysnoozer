# fbtimepartysnoozer

### Setting up frontend

Execute (in frontend directory):

```
$ npm install
$ node index.js
$ ngrok 1337
```

Edit set_page_home.sh and whitelist_page.sh to use new ngrok urls.
Probably You should also update the url in Facebook Developer console:
Open the webhook options for your app and click "Edit Subscribtion"

put ngrok url e.g.
```
https://89b75115.ngrok.io/webhook
```
and Verify Token: random_string