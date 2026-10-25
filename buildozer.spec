[app]

(str) Title of your application

title = Song Lyrics Manager

(str) Package name

package.name = songlyricsmanager

(str) Package domain (needed for android packaging)

package.domain = org.test

(str) Source code where the main.py lives

source.dir = .

(list) Source files to include (let empty to include all the source files)

source.include_exts = py,png,jpg,kv,atlas,json,txt,sqlite3,db

(list) List of inclusions using pattern matching

#source.include_patterns = assets/,images/.png

(list) Source files to exclude (let empty to not exclude anything)

source.exclude_exts = spec

(list) List of directory to exclude (let empty to not exclude anything)

source.exclude_dirs = tests, bin, venv, .git, .github

(list) List of exclusions using pattern matching

#source.exclude_patterns = license,data/audio/*.wav

(str) Application versioning (method 1)

version = 0.1

(str) Application versioning (method 2)

version.regex = version = '"['"]

version.filename = %(source.dir)s/main.py

(list) Application requirements

comma separated e.g. requirements = sqlite3,kivy

requirements = python33.11.9,kivy2.3.0,sqlite3,urllib3,requests,certifi,chardet,idna

(str) Custom source folders for requirements

Sets custom source for any requirements with recipes

requirements.source.kivy = ../../kivy

(list) Garden requirements

#garden_requirements =

(str) Presplash of the application

#presplash.filename = %(source.dir)s/data/presplash.png

(str) Icon of the application

#icon.filename = %(source.dir)s/data/icon.png

(list) Supported orientations

Valid options are: landscape, portrait, portrait-reverse or landscape-reverse

orientation = portrait

(list) List of service to declare

#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

OSX Specific

author = © Copyright Info

change the major version of python used by the app

osx.python_version = 3

Kivy version to use

osx.kivy_version = 2.3.0

Android specific

(bool) Indicate if the application should be fullscreen

fullscreen = 0

(string) Presplash background color (for android toolchain)

Supported formats are: #RRGGBB #AARRGGBB or one of the following names:

red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,

darkgray, grey, lightgrey, darkgrey.

#android.presplash_color = ''

(list) Permissions

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

(list) features (adds uses-feature tags to manifest)

#android.features = android.hardware.usb.host

(int) Target Android API, should be as high as possible.

android.api = 34

(int) Minimum API your APK / AAB will support.

android.minapi = 21

(int) Android SDK version to use

android.sdk = 34

(str) Android NDK version to use

android.ndk = 25b

(bool) Use --private data storage (True) or --dir public storage (False)

android.private_storage = True

(str) Android NDK directory (if empty, it will be automatically downloaded.)

#android.ndk_path =

(str) Android SDK directory (if empty, it will be automatically downloaded.)

#android.sdk_path =

(str) ANT directory (if empty, it will be automatically downloaded.)

#android.ant_path =

(bool) If True, then skip trying to update the Android sdk

This can be useful to avoid excess Internet downloads or save time

when an update is due and you just want to test/build your package

android.skip_update = False

(bool) If True, then automatically accept SDK license

agreements. This is intended for automation only. If set to False,

the default, you will be shown the license when first running

buildozer.

android.accept_sdk_license = True
android.auto_accept_sdk_license = True

(str) Android entry point, default is ok for Kivy-based app

#android.entrypoint = org.kivy.android.PythonActivity

(str) Full name including package path of the Java class that implements Android Activity

Useful to replace the default PythonActivity with your own implementation

#android.activity_class_name = org.kivy.android.PythonActivity

(str) Extra xml to write directly inside the  element of AndroidManifest.xml

use that parameter to provide a filename from where to load your custom XML code

#android.extra_manifest_xml = ./src/android/extra_manifest.xml

(str) Extra xml to write directly inside the  tag of AndroidManifest.xml

use that parameter to provide a filename from where to load your custom XML code

#android.extra_manifest_application_xml = ./src/android/extra_manifest_application.xml

(list) Pattern to whitelist for the whole project

#android.whitelist =

(str) Path to a custom whitelist file

#android.whitelist_src =

(str) Path to a custom blacklist file

#android.blacklist_src =

(list) List of Java .jar files to add to the libs so that pyjnius can access

their classes. Don't add jars that you do not need, since extra jars can slow

down the build process. Allows wildcards matching, for example:

#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

(list) List of Java files to add to the android project (can be java or a

directory containing the files)

#android.add_src =

(list) Android AAR archives to add

#android.add_aars =

(list) Gradle dependencies to add

#android.gradle_dependencies =

(list) add java compile options

this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option

see https://developer.android.com/studio/write/java8-support for example:

#android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

(list) Packaging options to add

see https://google.github.io/android-gradle-dsl/current/com.android.build.gradle.internal.dsl.PackagingOptions.html

can be used to solve conflicts in gradle dependencies

see it in use here: https://github.com/kivy/python-for-android/blob/development/tests/issues/issue_1381/buildozer.spec

#android.packaging_options =

(list) Java classes to add as activities to the manifest.

#android.add_activities = com.example.ExampleActivity

(list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64

In GitHub Actions CI, building just arm64-v8a is much faster and covers almost all modern Android devices.

android.archs = arm64-v8a

(int) overrides automatic versionCode computation (used in build.gradle)

this is not the same as app version and should only be edited if you know what you're doing

android.numeric_version = 1

(bool) enables Android auto backup feature (Android API >=23)

android.allow_backup = True

(str) XML file for custom backup rules (see official Android documentation)

android.backup_rules =

(str) If you need to insert variables into your AndroidManifest.xml file,

you can define them here.

android.manifest_placeholders = [:]

(bool) Logcat filters to use

#android.logcat_filters = *:S python:D

(bool) Copy library instead of making a libpymodules.so

#android.copy_libs = 1

(list) Android application meta-data to set (key=value format)

#android.meta_data =

(list) Android runtime permissions to request at application start

#android.permissions_runtime =

(list) Android custom components to add

#android.custom_components =

[buildozer]

(int) Log level (0 = error only, 1 = info, 2 = debug (with command output))

log_level = 2

(int) Display warning if buildozer is run as root (0 = False, 1 = True)

warn_on_root = 1

(str) Path to build artifact storage, absolute or relative to spec file

build_dir = ./.buildozer

(str) Path to build output (i.e. .apk, .aab, .ipa) storage

bin_dir = ./bin
