# User Service API

A demo of an RESTFULapplication which may be used in any market where user information is processed/gathered.

## Features

- git hooks
    > git hooks which are implemented to keep branching/commit names and a commit messages in a proper convention.
- virtual env
    > app with its dependencies work in poetry virt env
- SQL DB integration
    > app is integrated with POSTGRESQL which is capable of storing user's information
- noSQL DB integration
    > app is integrated with Redis which is used for caching data (cache lifetime is aproximately 120s)
- Messages Queue
    > There is an usage of RabbitMQ for messaging about using one of PUT/POST/DELETE method
- Unit/Integration tests
    > App is fully covered with tests
- Contenerization
    > App is contenerized using docker compose
- CI/CD pipeline
    > There is a script which automatically run tests after pushing changes into GIT. If tests are passed changes can be merged with MAIN branch.


