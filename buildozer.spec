[app]

# (str) Title of your application
title = Song Lyrics Manager

# (str) Package name
package.name = mlmapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.rajappansasi007

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db,json,txt

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, .git, .github

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,data/audio/*.wav

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,bcrypt,sqlite3

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid values: landscape, sensorLandscape, portrait, sensorPortrait, all
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0


# =============================================================================
# Android specific
# =============================================================================

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android SDK build-tools version to use (Prevents pulling unverified v37)
android.build_tools_version = 34.0.0

# (bool) Automatically accept SDK licenses (Fixes license confirmation crashes)
android.accept_sdk_license = True

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) If True, then the app will be able to be backed up via adb
android.allow_backup = True

# (bool) Enable AndroidX support. Required for modern Android versions
android.enable_androidx = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk)
android.debug_artifact = apk

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_mips = libs/android-mips/*.so

# (bool) indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
#android.library_references =

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D


# =============================================================================
# Python for android (p4a) specific
# =============================================================================

# (str) python-for-android branch to use, defaults to master
p4a.branch = master


# =============================================================================
# Buildozer specific
# =============================================================================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with output of all commands))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, default to (source.dir)/bin
bin_dir = ./bin
