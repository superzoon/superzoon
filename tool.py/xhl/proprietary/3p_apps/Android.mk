LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

xhl_modules : nothing
all-makefile=$(foreach module,$(1),$(LOCAL_PATH)/apps/$(module)/Android.mk)

ifeq ($(filter $(xhl_project),l388_80m sf8_80m),$(xhl_project))
override xhl_modules := 
endif

include $(call all-makefile, $(xhl_modules))