# A start up script for the fd_device container.
# This script is run when the container is started.
# It will wait for the database to be ready, then run any migrations
# and then start fd_device.

# Wait for the database to be ready
echo "Waiting for database to be ready..."
while ! nc -z fd_database 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
pipenv run fd_device database database_upgrade --revision head

# Start fd_device
echo "Starting fd_device..."
pipenv run fd_device run