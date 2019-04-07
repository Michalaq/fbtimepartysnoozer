#!/bin/bash

curl -X POST -H "Content-Type: application/json" -d "{
  \"home_url\" : {
     \"url\": \"https://89b75115.ngrok.io/\",
     \"webview_height_ratio\": \"tall\",
     \"webview_share_button\": \"show\",
     \"in_test\": false
  }
}" "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=EAAIKgrJGB2kBAE80hcZCiYMigUvAsB1gl3kTN21XvXKuWTTvZCNNGOH3tkE5xzEVYfl5NZBEqw6OyDCxYnOfPuVmc6GR3vaho6MCOFxIBIS9VvpUqVZAQLM8cGoU9vFrFyjaYLZBdKAlUKqI2Oha1pQbqvlMqMVqxTN1TMZAqVzgZDZD"