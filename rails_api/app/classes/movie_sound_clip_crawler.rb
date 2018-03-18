class MovieSoundClipCrawler < Crawler
  base_uri 'moviesoundclips.net'

  def self.extract_soundclip_for(movie_title)
    id = extract_id_for(movie_title)
    raw_html = get("/sound.php?id=#{id}").parsed_response
    noko = Nokogiri::HTML(raw_html)
    css_selector = 'a[href^="download.php"][href$="wav"]'
    href = noko.css(css_selector).to_a.sample['href']

    file_name = SecureRandom.hex(10) + '.wav'
    file_path = Rails.root.join('public', file_name)
    # Thread.new do
    #   File.open(file_path, 'wb') do |file|
    #     file << get("/#{href}")
    #   end
    # end

    `aria2c "http://moviesoundclips.net/#{href}" -o #{file_path}`
    
    file_name
  end

  def self.extract_id_for(movie_title)
    raw_html = get("/search.php?ser=#{movie_title}").parsed_response
    noko = Nokogiri::HTML(raw_html)
    css_selector = '#searchmovies div a'
    movies = noko.css(css_selector).to_a
      .select { |el| el['href'].match(/id/).present? }
      .map { |el| { id: el['href'].match(/id=(\d+)/).captures.first.to_i, title: el.text } }

    fuzzy_matched_movie_title = FuzzyMatch.new(movies.map { |movie| movie[:title] }).find(movie_title)
    id = movies.find { |movie| movie[:title] = fuzzy_matched_movie_title }[:id]
  end
end