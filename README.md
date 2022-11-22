# Information-Retrieval-Project


```
# start server with home directory server/ir
./bin/solr start -c -s ir  

# create decks collection using two cores and replicas
./bin/solr create -c decks -s 2 -rf 2 

# index decks
./bin/post -c decks path/to/folder/with/decks

# stop
./bin/solr stop -all
```