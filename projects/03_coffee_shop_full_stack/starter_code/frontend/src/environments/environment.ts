export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-dz95eudq.us', // the auth0 domain prefix
    audience: 'drinks', // the audience set for the auth0 app
    clientId: 'i8bWjTj2ngl2q5wOVwvrH8KmG76Ur7hk', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
