def get_title_from_dbpedia_url(dbpedia_url):
  s = dbpedia_url.replace("http://dbpedia.org/resource/", "")
  return s.replace("_", " ")


def get_titles_from_dbpedia_urls(dbpedia_urls):
  result = []
  for dbpedia_url in dbpedia_urls:
    result.append(get_title_from_dbpedia_url(dbpedia_url))
  return result
