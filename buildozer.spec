[app]

# (str) Title of your application
title = Song Lyrics Manager

# (str) Package name
package.name = mlmapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.rajappansasi007

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,db,json,txt

# (list) List of directories to exclude
source.exclude_dirs = tests, bin, .git, .github

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Explicitly pin python3 to a stable version with precompiled wheels/recipes
requirements = python3==3.11.9,kivy==2.3.0,bcrypt,sqlite3

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0


# =============================================================================
# Android specific
# =============================================================================

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API supported by your APK
android.minapi = 21

# (str) Android NDK version matching GitHub Actions runner
android.ndk = 25b

# (str) Android SDK build-tools version
android.build_tools_version = 34.0.0

# (bool) Automatically accept SDK licenses
android.accept_sdk_license = True

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) If True, app data can be backed up via adb
android.allow_backup = True

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Output format for packaging (apk)
android.release_artifact = apk
android.debug_artifact = apk

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D


# =============================================================================
# Python for Android (p4a) specific
# =============================================================================

# (str) python-for-android branch to use (use develop instead of unstable master)
p4a.branch = develop


# =============================================================================
# Buildozer specific
# =============================================================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifact storage
bin_dir = ./bin
