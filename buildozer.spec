[app]

# (str) Title of your application
title = ArtNet Controller Pro Plus

# (str) Package name
package.name = artnetcontroller

# (str) Package domain (needed for android/ios packaging)
package.domain = org.artnet

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (list) List of services to declare
#services =

#
# OSX Specific
#

#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray, darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy, olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (string) Presplash animation using Lottie format.
# see https://lottiefiles.com/ for examples and https://airbnb.design/lottie/ for general documentation.
# Lottie files can be created using various tools, like Adobe After Effect or Synfig.
#android.presplash_lottie = "path/to/lottie/file.json"

# (list) Permissions
# (See https://python-for-android.readthedocs.io/en/latest/buildoptions/#build-options-1 for all the supported syntaxes and properties)
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (list) features (adds uses-feature -tags to manifest)
#android.features = android.hardware.usb.host

# (int) Target Android API, should be as high as possible.
#android.api = 27

# (int) Minimum API your APK will support.
#android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 24

# (str) Android NDK version to use
#android.ndk = 17

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
#android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
#android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only.
#android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = @android:style/Theme.Holo.Light

# (list) Pattern to whitelist for the whole project
#android.whitelist = 

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process.
#android.add_jars = foo.jar,bar.jar,path/to/more/jars

# (list) List of Java files to add to the android project (can be java or a directory containing the files)
#android.add_src = 

# (list) Android AAR archives to add (currently works only with sdl2_gradle)
#android.add_aars = 

# (list) Gradle dependencies to add
#android.gradle_dependencies = 

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir = 

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes = 

# (str) Filename of a custom whitelist file
#p4a.whitelist = 

# (str) Filename of a custom blacklist file
#p4a.blacklist = 

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.arch = armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

# (bool) enables AndroidX support. Enable when 'android.gradle_dependencies' contains
# entries that require AndroidX dependencies (e.g. androidx.appcompat:appcompat)
# android.enable_androidx = False

# (list) patterns to include in the copy of the whole project to the build environment
# include_exts = py,png,jpg,kv,atlas

# (str) The directory in which the apk is going to be stored
#apkdir = ./bin

# (str) The directory in which the libs need to be stored
#libdir = ./lib

# (str) The directory in which the python source code will be stored
#pythondir = ./lib/python3.7

# (str) The directory in which the assets need to be stored
#assetsdir = ./assets

# (bool) Run application in debug mode
#debug = 1

# (bool) Strip python bytecode from the app
#strip = 1

# (bool) Enable logcat output (run logcat with adb logcat *:S python:*)
#logcat = 1

# (bool) Android specific: enable application to keep running when the device is idle
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (bool) Android specific: disable the application's ability to create windows
# with system alert windows, should be True if you want to use the PIP feature.
#android.system_alert_window = False

# (list) Android specific: list of Google Play Store filters
#android.playstore_filters = 

# (str) Android specific: The URL of the privacy policy
#android.privacy_policy = 

# (str) Android specific: The URL of the terms of service
#android.terms_of_service = 

# (str) Android specific: The email address to contact the developer
#android.developer_email = 

# (str) Android specific: The company name to contact the developer
#android.developer_name = 

# (str) Android specific: The application's category
#android.category = 

# (str) Android specific: The application's type
#android.apptype = 

# (list) Android specific: The application's screenshots
#android.screenshots = 

# (str) Android specific: The application's video
#android.video = 

# (str) Android specific: The application's website
#android.website = 

# (str) Android specific: The application's description
#android.description = 

# (str) Android specific: The application's promotional text
#android.promotional_text = 

# (str) Android specific: The application's keywords
#android.keywords = 

# (str) Android specific: The application's short description
#android.short_description = 

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
#ios.kivy_ios_branch =

# Another platform dependency: ios-deploy
# Uncomment to use a custom checkout
#ios.ios_deploy_dir = ../ios_deploy
# Or specify URL and branch
#ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
#ios.ios_deploy_branch = 1.9.4

# (bool) Whether or not to sign the code
#ios.codesign.allowed = false

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------#
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
data/images/original/*
#
#    -----------------------------------------------------------------------------#

# (list) P4A flags
#p4a.flags = --use-color=no

# (list) P4A environment variables
#p4a.env = 

# (list) Application specific additionnal flags
#app.additionalflags = 
