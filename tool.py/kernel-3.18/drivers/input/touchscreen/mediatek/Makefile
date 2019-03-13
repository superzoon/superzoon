subdir-ccflags-y += -Werror
ccflags-y += -I$(srctree)/drivers/misc/mediatek/include/mt-plat/
ccflags-y += -I$(srctree)/drivers/input/touchscreen/mediatek
# In case the platform does NOT support this type of sensors
obj-y   +=  mtk_tpd.o
obj-y   +=  tpd_button.o
obj-y   +=  tpd_calibrate.o
obj-y   +=  tpd_debug.o
obj-y   +=  tpd_default.o
obj-y   +=  tpd_init.o
obj-y   +=  tpd_misc.o
obj-y   +=  tpd_setting.o

# obj-$(CONFIG_TOUCHSCREEN_MTK_GT1151)	+=  GT1151/
# obj-$(CONFIG_TOUCHSCREEN_MTK_GT910)	+=  GT910/
# obj-$(CONFIG_TOUCHSCREEN_MTK_GT9XXTB_HOTKNOT)	+=  GT9XXTB_hotknot/
# obj-$(CONFIG_TOUCHSCREEN_MTK_SYNAPTICS_I2C_RMI4)	+=  synaptics_i2c_rmi4/
# obj-$(CONFIG_TOUCHSCREEN_MTK_GT928)	+=  GT928/
# CZ ADD FOR GSL680
obj-y +=GSL680_s89p/
obj-y +=	focaltech_can_update/

# ifeq	($(CUSTOM_KERNEL_TOUCHPANEL),focaltech)
	ldflags-y += --whole-archive -I$(srctree)/drivers/input/touchscreen/mediatek/ft5x0x/ft_gesture_lib.a_shipped  --no-whole-archive
# endif

obj-y += gsl_point_id.o
$(obj)/gsl_point_id.o: $(srctree)/$(obj)/gsl_point_id
	cp $(srctree)/$(obj)/gsl_point_id $(obj)/gsl_point_id.o
	
#ADD END.

# obj-$(CONFIG_TOUCHSCREEN_MTK_GT9XX_HOTKNOT_SCP)	+=  GT9XX_hotknot_scp/
# obj-$(CONFIG_TOUCHSCREEN_MTK_GT911)	+=  GT911/
# obj-$(CONFIG_TOUCHSCREEN_MTK_FT5X0X)	+=  ft5x0x/

