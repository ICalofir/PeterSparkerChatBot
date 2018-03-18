class ImdbCrawler < Crawler
  REVIEWS_LIMIT = 5
  
  base_uri 'imdb.com'

  attr_reader :id

  def initialize(id)
    @id = id
  end

  def extract_reviews
    return @reviews if @reviews.present?

    query_params = {
      spoiler: 'hide',
      sort: 'totalVotes',
      dir: 'desc'
    }
    raw_html = self.class.get("/title/#{id}/reviews", query: query_params).parsed_response
    noko = Nokogiri::HTML(raw_html)
    reviews_selector = '.lister-list .lister-item.imdb-user-review .review-container .lister-item-content .content .text'
    @reviews = noko.css(reviews_selector).to_a.first(REVIEWS_LIMIT).map(&:text)
  end

end