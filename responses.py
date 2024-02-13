from db import db

def handle_response(message) -> str:
  p_message = message.lower()

  if p_message == 'help':
    return db["help"]

  elif p_message == 'rules':
    return [db["rules1"], db["rules2"]]

  else:
    return db[message]