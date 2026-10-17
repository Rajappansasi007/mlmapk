[app]

# (str) Title of your application
title = Song Lyrics Manager

# (str) Package name
package.name = mlmapp

# (str) Package domain
package.domain = org.rajappansasi007

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,db,json,txt

# (list) Directories to exclude
source.exclude_dirs = tests, bin, .git, .github

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Keep python3 generic so p4a compiles matching hostpython3 and target python3 automatically
requirements = python3,kivy,bcrypt,sqlite3

# (list) Supported orientations
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0


# =============================================================================
# Android configuration
# =============================================================================

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version matching runner toolchain
android.ndk = 25b

# (str) Android SDK build-tools version
android.build_tools_version = 34.0.0

# (bool) Auto-accept SDK licenses
android.accept_sdk_license = True

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup via adb
android.allow_backup = True

# (bool) Enable AndroidX
android.enable_androidx = True

# (str) Artifact formats
android.release_artifact = apk
android.debug_artifact = apk

# (bool) Copy libraries
android.copy_libs = 1

# (str) Logcat filters
android.logcat_filters = *:S python:D


# =============================================================================
# Python-for-Android (p4a) configuration
# =============================================================================

# Pin to the stable p4a release tag to prevent pulling unreleased hostpython3 recipes
p4a.branch = master


# =============================================================================
# Buildozer settings
# =============================================================================

[buildozer]

log_level = 2
warn_on_root = 1
bin_dir = ./bin
