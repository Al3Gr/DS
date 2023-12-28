db.createCollection("photos")
db.photos.createIndex( { "username": 1 } )