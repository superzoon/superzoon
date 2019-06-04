LOCAL_DIR := $(GET_LOCAL_DIR)

TARGET := zechin6580_weg_m

MODULES += app/mt_boot \
           dev/lcm


MTK_EMMC_SUPPORT = yes
DEFINES += MTK_NEW_COMBO_EMMC_SUPPORT
DEFINES += MTK_KERNEL_POWER_OFF_CHARGING
MTK_KERNEL_POWER_OFF_CHARGING = yes
MTK_LCM_PHYSICAL_ROTATION = 0
# cz mod CUSTOM_LK_LCM = "otm9608_qhd_dsi_vdo"
CUSTOM_LK_LCM = "jd9365_hd7201440_dsi_vdo_gs9p jd9369_hd7201440_dsi_vdo_f8a st7703_hd7201440_dsi_vdo_l388 ili9881d_hd7201440_dsi_vdo_l388 ili9881c_hd7201440_dsi_vdo_l388"

DEFINES += __HW_BOARD_L388_V10__
DEFINES += __PROJECT_S89__


#FASTBOOT_USE_G_ORIGINAL_PROTOCOL = yes
MTK_SECURITY_SW_SUPPORT = yes
MTK_SEC_FASTBOOT_UNLOCK_SUPPORT = yes
MTK_VERIFIED_BOOT_SUPPORT = yes
BOOT_LOGO := hd720x1440
#DEFINES += WITH_DEBUG_DCC=1
DEFINES += WITH_DEBUG_UART=1
#DEFINES += WITH_DEBUG_FBCON=1
#DEFINES += MACH_FPGA=y
#DEFINES += MACH_FPGA_NO_DISPLAY