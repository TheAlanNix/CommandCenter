let error = true;

let result = [
  db.events.createIndex({ timestamp: 1 })
]

printjson(result);
