db.createCollection("users")
db.users.createIndex( { "username": 1 }, { unique: true } )
