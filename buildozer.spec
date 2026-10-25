[app]
title = Song Lyrics Manager
package.name = songlyricsmanager
package.domain = org.mlm.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,sql,db
version = 1.0.0

# Dependencies
requirements = python3,kivy==2.3.0,sqlite3,urllib3,requests

# Android UI Settings
orientation = portrait
fullscreen = 0

# Android Architecture & SDK
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = INTERNET
