# meet.io - A calendar component to manage appointments.

## Test data
To load test data into the app, the `manage.py loaddata test_data.json` command can be used.


## Authentication
The app does not have a proper authentication flow implemented.
- Create a super user via `manage.py createsuperuser`
- Send a POST request to `http://localhost:8000/api-token-auth/` with the following payload:
```
{
  "username": <newly created user>,
  "password": <password for user>
}
```
- Set the auth token from the response as the `VITE_DUMMY_AUTH_TOKEN` env variable in the frontend application.
- The app will store the dummy token in local storage and add it to request headers.
