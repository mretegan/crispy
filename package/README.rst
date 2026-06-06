Generate Crispy installers
==========================

Pre-requisites
--------------

On all platforms, install Crispy together with its bundling dependencies, from
the source directory::

    pip install .[bundle,notebook]

This pulls in PyInstaller. All the commands below are run from the ``package``
folder of the source directory.


Windows
-------

Run::

    pyinstaller --noconfirm crispy.spec

This generates ``dist\Crispy``, then runs Inno Setup to create the installer and
a zip archive of the application in ``artifacts``.


macOS
-----

The distributed application is a single **universal2** bundle that runs natively
on both Apple Silicon and Intel machines. Because Crispy's dependency wheels are
single-architecture, the universal bundle is assembled by building once per
architecture and fusing the two builds.

1. On an **Apple Silicon (arm64)** machine and on an **Intel (x86_64)** machine,
   build the application::

       pyinstaller --noconfirm crispy.spec

   On macOS this only produces the app bundle in ``dist/Crispy.app``; it does not
   sign, package or notarize it.

2. Collect the two ``dist/Crispy.app`` bundles and fuse them into one universal
   bundle with ``lipo``::

       python merge-universal.py arm64/Crispy.app x86_64/Crispy.app dist/Crispy.app

3. Sign the merged bundle, pack it into a disk image and notarize it::

       bash codesign.sh
       bash create-dmg.sh
       bash notarize.sh

   This produces ``artifacts/Crispy.dmg``.

In continuous integration this whole sequence is run automatically (see
``.github/workflows/release.yml``): the two architectures are built on separate
runners, merged on one of them, then signed, packed and notarized.

Signing and notarization are only performed if the following environment
variables are set; otherwise ``codesign.sh`` and ``notarize.sh`` exit without
doing anything, leaving an unsigned application:

- ``APPLE_ID``: The Apple ID used to generate the certificate and the
  application-specific password.
- ``APPLE_TEAM_ID``: The Apple Team ID associated with the Apple ID.
- ``CERTIFICATE_BASE64``: The Apple Developer ID Application Certificate exported
  as a ``.p12`` file and encoded in base64.
- ``CERTIFICATE_PASSWORD``: The password to decode the ``.p12`` file, as set when
  exporting the certificate.
- ``KEYCHAIN_PASSWORD``: The password used for the temporary keychain created to
  import the certificate. It can be any value; it only protects the temporary
  keychain.
- ``APPLICATION_SPECIFIC_PASSWORD``: An application-specific password generated
  for the Apple ID and used to connect to the notarization service.

A number of steps are needed to create the certificate and the
application-specific password. Step-by-step instructions can be found here:
`Mac Signing and Notarization Demo
<https://github.com/omkarcloud/macos-code-signing-example>`_. Even though the
instructions are for a different application type, the steps to create the
required credentials are the same.
