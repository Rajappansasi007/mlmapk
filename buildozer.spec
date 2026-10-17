[app]
title = Song Lyrics Manager
package.name = mlmapp
package.domain = org.rajappansasi007
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json

version = 1.0.0
requirements = python3,kivy,bcrypt,sqlite3

orientation = portrait
fullscreen = 0

# Android specific configurations
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1

