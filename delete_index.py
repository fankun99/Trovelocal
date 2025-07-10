import meilisearch

client = meilisearch.Client('http://127.0.0.1:7700', 'rzHvvVSus8cu_jgZ1UuXB5SyfXAGeSUMIlITMov9uig')
client.index('articles').delete()
