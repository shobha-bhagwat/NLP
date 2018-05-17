CREATE TABLE users
(
  id SERIAL PRIMARY KEY, 
  email text, 
  first_name text, 
  last_name text, 
  oauth_token text, 
  oauth_token_secret text
);

GRANT ALL PRIVILEGES ON table users TO postgres;

GRANT ALL PRIVILEGES ON sequence users_id_seq TO postgres;
