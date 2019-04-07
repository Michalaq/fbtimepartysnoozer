#!/bin/bash

curl -X POST -H "Content-Type: application/json" -d "{
  \"setting_type\" : \"domain_whitelisting\",
  \"whitelisted_domains\" : [\"https://89b75115.ngrok.io/\"],
  \"domain_action_type\": \"add\"
}" "https://graph.facebook.com/v2.6/me/thread_settings?access_token=EAAIKgrJGB2kBAE80hcZCiYMigUvAsB1gl3kTN21XvXKuWTTvZCNNGOH3tkE5xzEVYfl5NZBEqw6OyDCxYnOfPuVmc6GR3vaho6MCOFxIBIS9VvpUqVZAQLM8cGoU9vFrFyjaYLZBdKAlUKqI2Oha1pQbqvlMqMVqxTN1TMZAqVzgZDZD"