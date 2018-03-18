const http = require('http');
const host = '7c254862.ngrok.io';
const ERROR_MESSAGE = 'No data currently available, please try again';

const PARAMETERS = {
  MOVIE_TITLE: 'movie-title',
  REVIEW_REACTION_TYPE: 'review-attribute'
}

const pathWithQueryParams = (path, params) => {
  const queryParams = Object.keys(params).map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`).join('&');
  return `${path}?${queryParams}`
}

const getIntentName = req => req.body.result.metadata['intentName'].match(/^[a-zA-Z]+/)[0];
const getMovieTitle = req => req.body.result.parameters[PARAMETERS.MOVIE_TITLE];
const getReviewReactionType = req => req.body.result.parameters[PARAMETERS.REVIEW_REACTION_TYPE];

const doQuoteRequest = ({ path, params }) => {
  return new Promise((resolve, reject) => {
    const fullPath = pathWithQueryParams(path, params);

    http.get({ host: host, path: fullPath }, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk });
      res.on('end', () => {
        let response = JSON.parse(body);
        let output = `<speak><audio src="https://${host}/${response.file_path}"></audio></speak>`;
        resolve(output);
      });
      res.on('error', (error) => {
        reject(ERROR_MESSAGE);
      })
    });
  });
}

const doRequest = ({ path, params, responseField }) => {
  return new Promise((resolve, reject) => {
    const fullPath = pathWithQueryParams(path, params);

    http.get({ host: host, path: fullPath }, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk });
      res.on('end', () => {
        let response = JSON.parse(body);
        let output = response[responseField];
        resolve(output);
      });
      res.on('error', (error) => {
        reject(ERROR_MESSAGE);
      })
    });
  });
}

const doOverviewRequestFor = (req, attribute) => {
  return doRequest({
    path: '/movies/overview',
    params: { title: getMovieTitle(req) },
    responseField: attribute
  })
}

const intentHandlers = {
  MovieCast(req) {
    return doOverviewRequestFor(req, 'actors');
  },

  MovieCreator(req) {
    return doOverviewRequestFor(req, 'director');
  },

  MovieGenre(req) {
    return doOverviewRequestFor(req, 'genre');
  },

  MovieOverview(req) {
    return doOverviewRequestFor(req, 'plot');
  },

  MovieRating(req) {
    return doOverviewRequestFor(req, 'rating_details');
  },

  MovieYear(req) {
    return doOverviewRequestFor(req, 'year');
  },

  MovieReview(req) {
    return doRequest({
      path: '/movies/review',
      params: { title: getMovieTitle(req), review_reaction_type: getReviewReactionType(req) },
      responseField: 'review'
    });
  },

  MovieQuote(req) {
    return doQuoteRequest({
      path: '/movies/quote',
      params: { title: getMovieTitle(req) }
    });
  },

  defaultHandler() {
    return new Promise((resolve, reject) => {
      resolve('This is the defaultHandler printing');
    })
  }
}

/*
* HTTP Cloud Function.
*
* @param {Object} req Cloud Function request context.
* @param {Object} res Cloud Function response context.
*/

exports.PeterSparker = (req, res) => {
  const intentName = getIntentName(req);
  const intentHandler = intentHandlers.hasOwnProperty(intentName) ? intentHandlers[intentName] : intentHandlers['defaultHandler'];

  intentHandler(req)
    .then((output) => {
      res.setHeader('Content-Type', 'application/json');
      let responseData = {
        'speech': output || ERROR_MESSAGE ,
        'displayText': output || ERROR_MESSAGE
      };

      if (intentName == 'MovieQuote') {
        responseData['data'] = { 'google': { 'is_ssml': true }};
      }
      res.send(JSON.stringify(responseData));
    }).catch((error) => {
      res.setHeader('Content-Type', 'application/json');
      res.send(JSON.stringify({ 'speech': error, 'displayText': error }));
    });
};