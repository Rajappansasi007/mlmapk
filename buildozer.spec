[app]
title = Song Lyrics Manager
package.name = songlyricsmanager
package.domain = org.mlm.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,sql,db
source.exclude_dirs = tests, bin, venv, .git, .github, .buildozer
version = 1.0.0

# Pin requirements without standalone sqlite3 (python3 compiles sqlite3 natively)
requirements = python3,kivy==2.3.0,urllib3,requests,certifi,charset_normalizer,idna

orientation = portrait
fullscreen = 0

# Android SDK / NDK Specifications
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.archs = arm64-v8a

# CRITICAL: Lock python-for-android branch to avoid experimental Python 3.14
p4a.branch = release-2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
