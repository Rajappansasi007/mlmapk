[app]
title = Song Lyrics Manager
package.name = songlyricsmanager
package.domain = org.mlm.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,sql,db
version = 1.0.0

# Remove standalone sqlite3 and let python3 bundle it natively
requirements = python3,kivy==2.3.0,urllib3,requests,certifi,charset_normalizer,idna

orientation = portrait
fullscreen = 0

# Android build settings
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
bin_dir = ./bin
