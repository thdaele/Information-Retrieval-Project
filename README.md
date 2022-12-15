# Information-Retrieval-Project

```
# stop solr
./bin/solr stop -all

# start server with home directory server/ir2 (not in cloud mode)
./bin/solr start -s ir2  

# create core called 'decks'
./bin/solr create -c decks

# index decks
./bin/post -c decks path/to/folder/with/decks

# stop solr
./bin/solr stop -all
```