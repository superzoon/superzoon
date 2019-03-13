LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LIBS_PATH:=$(LOCAL_PATH)/libs
SERVICE_PATH:=$(LOCAL_PATH)/service

$(shell echo $(xhl_project) > mklog.txt)

mkfile=$(LOCAL_PATH)/$(xhl_project).mk
isfile=$(shell test -e $(mkfile) && echo yes)
ifeq ($(call isfile), yes)
include $(mkfile)
endif


include $(SERVICE_PATH)/xhlservice/Android.mk
include $(LIBS_PATH)/Android.mk
