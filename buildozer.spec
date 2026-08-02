[app]
title = AquaDingo
package.name = aquadingo
package.domain = org.aquadingo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.3.1,plyer
orientation = portrait
fullscreen = 0

# Ícone e splash (opcionais - remova estas duas linhas se não tiver os arquivos)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.permissions = POST_NOTIFICATIONS
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

# Usa a versão de desenvolvimento do python-for-android, que já tem
# correção para funcionar com versões mais novas do pip/Python
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
