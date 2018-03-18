class MoviesController < ApplicationController
  # before_action :load_movie

  def overview
    # movie_attrs = {:title=>"Game of Thrones", :year=>"2011–", :rated=>"TV-MA", :released=>"17 Apr 2011", :runtime=>"57 min", :genre=>"Action, Adventure, Drama", :director=>"N/A", :writer=>"David Benioff, D.B. Weiss", :actors=>"Peter Dinklage, Lena Headey, Emilia Clarke, Kit Harington", :plot=>"Nine noble families fight for control over the mythical lands of Westeros, while an ancient enemy returns after being dormant for thousands of years.", :language=>"English", :country=>"USA, UK", :awards=>"Won 1 Golden Globe. Another 273 wins & 454 nominations.", :poster=>"https://images-na.ssl-images-amazon.com/images/M/MV5BMjE3NTQ1NDg1Ml5BMl5BanBnXkFtZTgwNzY2NDA0MjI@._V1_SX300.jpg", :ratings=>[{:source=>"Internet Movie Database", :value=>"9.5/10"}], :metascore=>"N/A", :imdb_rating=>"9.5", :imdb_votes=>"1,298,417", :imdb_id=>"tt0944947", :type=>"series", :total_seasons=>"8", :response=>"True"}
    movie_attrs = OMDB.title(movie_params[:title])
    movie_attrs.merge!(rating_details: "IMDB rating is #{movie_attrs[:imdb_rating]} out of #{movie_attrs[:imdb_votes]} votes")

    render json: movie_attrs
  end

  def review
    load_movie
    reviews = ImdbCrawler.new(@movie.imdb_id).extract_reviews

    render json: {
      review: SentimentAnalysis.new(reviews).run(movie_params[:review_reaction_type])
    }
  end

  def quote
    render json: {
      file_path: Dir["public/*.wav"].sample.gsub("public/", "") # MovieSoundClipCrawler.extract_soundclip_for(movie_params[:title])
      # file_path: MovieSoundClipCrawler.extract_soundclip_for(movie_params[:title])
    }
  end

  private

  def movie_params
    params.permit(:title, :review_reaction_type)
  end

  def load_movie
    @movie = OMDB.title(movie_params[:title])
  end
end
