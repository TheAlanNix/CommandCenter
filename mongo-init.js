let error = true;

let result = [
  db.events.createIndex({ timestamp: 1 }, { expireAfterSeconds: 2678400 })
]

printjson(result);
