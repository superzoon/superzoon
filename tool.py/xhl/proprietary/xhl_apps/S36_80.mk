LOCAL_PATH:= $(call my-dir)

TARGET_KEEP_0 := yes
TARGET_KEEP_1 := no

TARGET_OUT_PRIV := $(TARGET_OUT)/priv-app
TARGET_OUT_APP := $(PRODUCT_OUT)/system/app
TARGET_OUT_VENDOR := $(TARGET_OUT)/vendor/operator/app
TARGET_OUT_DATA := $(TARGET_OUT_DATA_APPS)
#LOCAL_DEX_PREOPT := false || true 

#####  app  ############
APPS_PATH := $(LOCAL_PATH)/apps

#ifeq ($(TARGET_KEEP_1),no)
#$(shell rm -rf $(PRODUCT_OUT)/system/app/AccuweatherPhone)
#endif
#ifeq ($(TARGET_KEEP_1),yes)
#include $(CLEAR_VARS)
#LOCAL_MODULE := AccuweatherPhone
#LOCAL_SRC_FILES := apps/$(LOCAL_MODULE)/$(LOCAL_MODULE).apk
#LOCAL_MODULE_CLASS := APPS
#LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
#LOCAL_PRIVILEGED_MODULE := true
#LOCAL_CERTIFICATE := platform
#LOCAL_MODULE_PATH := $(TARGET_OUT)/app
#include $(BUILD_PREBUILT)
#endif

#ifeq ($(TARGET_KEEP_0),no)
#$(shell rm -rf $(PRODUCT_OUT)/system/app/Factory)
#endif
#ifeq ($(TARGET_KEEP_0),yes)
#include $(APP_PATH)/Factory/Factory.mk
#endif

#$(shell cp -r $(LOCAL_PATH)/T9DB $(TARGET_OUT)/T9DB)