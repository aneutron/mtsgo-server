##### 05/04/2017 - 02:00
- It's a pain in the ass to send JSON data over GET, so GET requests will receive GET parameters only, including token and user_id.
- Added `try_decode_json` that only tries to decode json when there is a POST request. 
Please verify that your parameters are present before working with them.
- As I said earlier sending JSON data over GET is not recommended so I split the `AuthView` into two views: 
`AuthView` for authentication, and `AuthNewView` for registration, both of them are POST only.
- Added code to retrieve one question, and to try to answer a question. (Technically, a spot.)
- Added code to retrieve neighboring questions _(Again technically spot)_, __Still needs to be heavily optimized__.
- Added code to retrieve history.
- Updated the API specification.
- Added TravisCI Integration.