#!/usr/bin/env bash

set -e

# Get the root folder. This should be Crispy's parent folder.
ROOT=$(dirname $(dirname "${PWD}"))

# Path to the built application.
APP="${ROOT}"/dist/Crispy.app

# Path to resources (volume icon, background, ...).
RESOURCES="${ROOT}"/crispy/assets

# Other paths.
ARTIFACTS="${ROOT}"/artifacts
TEMPLATE="${ARTIFACTS}"/template
TEMPLATE_DMG="${ARTIFACTS}"/template.dmg
DMG="${ARTIFACTS}"/Crispy-0.6.0.dmg

echo "Removing previous images."
if [[ -e "${DMG}" ]]; then rm -rf "${DMG}"; fi

echo "Copying required files."
mkdir -p "${TEMPLATE}"/.background

cp -a "${RESOURCES}"/background.pdf "${TEMPLATE}"/.background/background.pdf
cp -a "${RESOURCES}"/crispy.icns "${TEMPLATE}"/.VolumeIcon.icns
cp -a "${RESOURCES}"/DS_Store "${TEMPLATE}"/.DS_Store

cp -a "${APP}" "${TEMPLATE}"/Crispy.app

ln -s /Applications/ "${TEMPLATE}"/Applications

# Create a regular .fseventsd/no_log file
# (see http://hostilefork.com/2009/12/02/trashes-fseventsd-and-spotlight-v100/ )
mkdir "${TEMPLATE}"/.fseventsd
touch "${TEMPLATE}"/.fseventsd/no_log

echo "Creating the temporary disk image."
hdiutil create -format UDRW -volname Crispy -fs HFS+ \
       -fsargs '-c c=64,a=16,e=16' \
       -srcfolder "${TEMPLATE}" \
       "${TEMPLATE_DMG}"

hdiutil detach /Volumes/Crispy -force || true

echo 'Attaching the temporary disk image in read/write mode.'
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "${TEMPLATE_DMG}" | grep '^/dev/')
DEV_NAME=$(echo -n "${MOUNT_OUTPUT}" | head -n 1 | awk '{print $1}')
MOUNT_POINT=$(echo -n "${MOUNT_OUTPUT}" | tail -n 1 | awk '{print $3}')

echo 'Fixing permissions.'
chmod -Rf go-w "${TEMPLATE}" || true

# Makes the disk image window open automatically when mounted.
bless -openfolder "${MOUNT_POINT}"

# Hides background directory even more.
SetFile -a V "${MOUNT_POINT}"/.background

# Sets the custom icon volume flag so that volume has nice icon.
SetFile -a C "${MOUNT_POINT}"

echo "Detaching the temporary disk image"
hdiutil detach "${DEV_NAME}" -force

if [[ -e "${DMG}" ]]; then rm -rf "${DMG}"; fi

echo 'Converting the temporary image to a compressed image.'
hdiutil convert "${TEMPLATE_DMG}" -format UDZO -imagekey zlib-level=9 -o "${DMG}"

echo 'Cleaning up.'
rm -rf "${TEMPLATE}"
rm -rf "${TEMPLATE_DMG}"
