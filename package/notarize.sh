#!/usr/bin/env bash

# The script submits the application for notarization to Apple.

# Exit immediately if a command exits with a non-zero status
set -e
# Print commands and their arguments as they are executed (debug mode)
# set -x

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') INFO [notarize] $1"
}

# Check if the required environment variables are set.
if [[ -z "${APPLE_ID}" || -z "${APPLE_TEAM_ID}" || -z "${APPLICATION_SPECIFIC_PASSWORD}" ]]; then
  log "Skipping notarization; the required environment variables (APPLE_ID, APPLE_TEAM_ID, APPLICATION_SPECIFIC_PASSWORD) are not set."
  exit 0
fi

log "Setting the required environment variables."
APP_NAME="Crispy"
ROOT="${PWD}"
APP_DMG="${ROOT}/artifacts/${APP_NAME}.dmg"

log "Submitting the application for notarization."
xcrun notarytool submit \
  --apple-id "${APPLE_ID}" \
  --team-id "${APPLE_TEAM_ID}" \
  --password "${APPLICATION_SPECIFIC_PASSWORD}" \
  --wait "${APP_DMG}"

log "Stapling the notarization ticket to the disk image."
# The stapler downloads the ticket from Apple and fails if the connection drops, so
# try again before failing the job.
for attempt in 1 2 3 4 5; do
  if xcrun stapler staple "${APP_DMG}"; then
    break
  fi
  if [[ "${attempt}" -eq 5 ]]; then
    log "Stapling failed after ${attempt} attempts."
    exit 1
  fi
  log "Stapling failed (attempt ${attempt}); trying again in 30 seconds."
  sleep 30
done

log "Notarization completed successfully."
