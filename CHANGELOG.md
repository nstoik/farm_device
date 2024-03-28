# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [Unreleased] - yyyy-mm-dd
 
Here we write upgrading notes for.
 
### Added
- [PROJECTNAME-XXXX](http://tickets.projectname.com/browse/PROJECTNAME-XXXX)
  MINOR Ticket title goes here.
- [PROJECTNAME-YYYY](http://tickets.projectname.com/browse/PROJECTNAME-YYYY)
  PATCH Ticket title goes here.
### Changed

### Fixed

## Unreleased - [v0.3.4](https://github.com/nstoik/farm_device/releases/tag/v0.3.4) - 2024-mm-dd
 
Update the `TAG` variable in the `.env` file to `v0.3.4`. Then execute the following to pull and run the containers:
```bash
> docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod down
> docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod pull
> docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod up -d
```

### Added
- `CHANGELOG.md` file to track changes to the project and added documentation on how to release new versions.

### Changed
- SQLAlchemy relations. Changed `backref` to `back_populates`.
- Context for the docker build process to be from the root directory of the project.
- Bumped the Ubuntu image to 24.04 for the fd_1wire container..

### Fixed
- Branch name in the github\workflows\codeql-analysis.yml file was incorrect. Changed from `master` to `main`.
- Fixed device `start.sh` script to properly run forever

## [v0.3.3](https://github.com/nstoik/farm_device/releases/tag/v0.3.3) - 2024-03-27
 
Update the `TAG` variable in the `.env` file to `v0.3.3`. Then execute the following to pull and run the containers:
```bash
> docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod down
> docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod pull
> docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env -p fd_prod up -d
```

### Added
- A startup script to the fd_device docker container.
- Additional tests and sample files for testing 
### Changed
- Removed the `database_management` container. That functionality is now handled by the startup script.
### Fixed
- Fixed bug when trying to take the average of no temperature readings.

## [v0.3.2](https://github.com/nstoik/farm_device/releases/tag/v0.3.2) - 2024-01-08
 
### Added
 
### Changed
- fd_device with docker images created for v0.3.2

### Fixed

## [v0.3.1](https://github.com/nstoik/farm_device/releases/tag/v0.3.1) - 2024-01-08

### Added

### Changed
- fd_device with docker images created for v0.3.1
### Fixed