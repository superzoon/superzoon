#
# Copyright (C) 2009 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# This is a build configuration for a full-featured build of the
# Open-Source part of the tree. It's geared toward a US-centric
# build of the emulator, but all those aspects can be overridden
# in inherited configurations.

PRODUCT_PROPERTY_OVERRIDES := \
    ro.com.android.dateformat=MM-dd-yyyy \
    ro.config.ringtone=Alarm_Classic.ogg \
    ro.config.notification_sound=Alarm_Classic.ogg \
    ro.config.alarm_alert=Alarm_Classic.ogg

# Put en_US first in the list, so make it default.
# PRODUCT_LOCALES := en_US

# Include drawables for all densities
# PRODUCT_AAPT_CONFIG := normal hdpi xhdpi xxhdpi

# Get google all jar and app
$(call inherit-product-if-exists, xhl/proprietary/google_framework/GoogleFramework.mk)
# Get sec all jar and app
$(call inherit-product-if-exists, xhl/proprietary/xhl_apps/XhlApps.mk)
# Get 3p app
$(call inherit-product-if-exists, xhl/proprietary/3p_apps/ThirdApps.mk)
#OVERLAYS
PRODUCT_PACKAGE_OVERLAYS += xhl/overlay/$(xhl_project)_$(xhl_screen)_$(xhl_hardware)/$(xhl_customer)