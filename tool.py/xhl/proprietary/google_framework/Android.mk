LOCAL_PATH:= $(call my-dir)

TARGET_KEEP_CORE := yes
TARGET_KEEP_0 := yes
TARGET_KEEP_1 := no

TARGET_OUT_PRIV := $(TARGET_OUT)/priv-app
TARGET_OUT_APP := $(PRODUCT_OUT)/system/app
TARGET_OUT_VENDOR := $(TARGET_OUT)/vendor/operator/app
TARGET_OUT_DATA := $(TARGET_OUT_DATA_APPS)

###app############


#ifeq ($(TARGET_KEEP_0),no)
#$(shell rm -rf $(PRODUCT_OUT)/system/priv-app/GooglePlay)
#endif
#ifeq ($(TARGET_KEEP_0),yes)
#include $(CLEAR_VARS)
#LOCAL_MODULE := GooglePlay
#LOCAL_MODULE_TAGS := optional
#LOCAL_SRC_FILES := apps/$(LOCAL_MODULE)/$(LOCAL_MODULE).apk
#LOCAL_MODULE_CLASS := APPS
#LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
#LOCAL_CERTIFICATE := PRESIGNED
#LOCAL_MODULE_PATH := $(TARGET_OUT)/priv-app
#include $(BUILD_PREBUILT)
#endif

#ifeq ($(TARGET_KEEP_1),no)
#$(shell rm -rf $(PRODUCT_OUT)/system/app/Chrome)
#endif
#ifeq ($(TARGET_KEEP_1),yes)
#include $(CLEAR_VARS)
#LOCAL_MODULE := Chrome
#LOCAL_MODULE_TAGS := optional
#LOCAL_SRC_FILES := apps/$(LOCAL_MODULE)/$(LOCAL_MODULE).apk
#LOCAL_MODULE_CLASS := APPS
#LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
#LOCAL_CERTIFICATE := PRESIGNED
#LOCAL_MODULE_PATH := $(TARGET_OUT)/app
#LOCAL_PREBUILT_JNI_LIBS := \
#            @lib/armeabi-v7a/libchrome.2171.93.so \
#            @lib/armeabi-v7a/libchromium_android_linker.so
#include $(BUILD_PREBUILT)
#endif



#$(shell cp -r $(LOCAL_PATH)/framework $(TARGET_OUT)/framework)



