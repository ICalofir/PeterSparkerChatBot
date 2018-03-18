class Crawler
  USER_AGENT_HEADER = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
  include HTTParty
  headers 'User-Agent' => USER_AGENT_HEADER
end