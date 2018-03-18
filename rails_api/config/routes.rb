Rails.application.routes.draw do
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html

  resources :movies, only: [] do
    get :overview, on: :collection
    get :review, on: :collection
    get :quote, on: :collection
  end
end
