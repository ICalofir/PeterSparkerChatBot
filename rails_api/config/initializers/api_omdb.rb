module OMDB
  class Client
    def get(url, params = {})
      params.merge!(apikey: Figaro.env.omdb_api_key)
      request = self.class.get '/', query: params
      convert_hash_keys(request.parsed_response)
    end
  end
end