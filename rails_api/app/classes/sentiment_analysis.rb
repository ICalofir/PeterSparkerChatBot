class SentimentAnalysis
  SCRIPT_PATH = Rails.root.join('..', 'ml_summarization', 'summarize_reviews.py')

  def initialize(collection)
    @collection = collection
  end

  def run(reaction_type = nil)
    text = @collection.join(' ').gsub('"', '\'')
    cmd = %Q(python #{SCRIPT_PATH} --text "#{text}")
    cmd += " --reaction_type #{reaction_type}" if reaction_type.present?

    `#{cmd}`
  end
end