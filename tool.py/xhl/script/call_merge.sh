#!/bin/bash
#$@ mtk=zechin6580_weg_m combo=eng project=l388_80m screen=hd720x1440 hardware=v10 flash=flash4 network=3g customer=xlan battery=L388_123 language=foreign xxx=xxx config=device/zechin/zechin6580_weg_m/ProjectConfig.mk
COLOR_START="\033["
COLOR_END="\033[0m"
COLOR_BG1="43;"
COLOR_BG2="42;"

echo -e "${COLOR_START}${COLOR_BG1}30mcall merge ：${COLOR_START}${COLOR_BG2}31m$@ ${COLOR_END}"
for par in $@
do
  key=${par%%=*}
  value=${par##*=}
  if [ "mtk" == ${key} ]
  then
    #MTK项目 [zechin6580_weg_m, zechin6580_we_m]
    MTK_PROJECT=${value}
  elif [ "combo" == ${key} ]
  then
    #版本['user', 'eng', 'emulator']
    COMBO=${value}}
  elif [ "project" == ${key} ]
  then
    #项目['gs9_80', 'gs9p_80']
    ROJECT=${value}
  elif [ "screen" == ${key} ]
  then
    #屏幕['fw', 'qhd', 'hd']
    SCREEN=${value}
  elif [ "hardware" == ${key} ]
  then
    #硬件['v10', 'v20']
    HARDWARE=${value}
  elif [ "flash" == ${key} ]
  then
    #字库['mcp_nand', 'emmc_32+4_ddr2', 'emmc_32+8_ddr2']
    FLASH=${value}
  elif [ "network" == ${key} ]
  then
    #网络['2g', '3g']
    NETWORK=${value}
  elif [ "language" == ${key} ]
  then
    #语言['huayu','chinese','foreign']
    LANGUAGE=${value}
  elif [ "battery" == ${key} ]
  then
    #电池['gs8_henxing305472p1500_425v', ]
    BATTERY=${value}
  elif [ "sim" == ${key} ]
  then
    #单双卡
    SIM=${value}
  elif [ "band" == ${key} ]
  then
    #射频
    BAND=${value}
  elif [ "customer" == ${key} ]
  then
    #客户['customer', 'tianbao']
    CUSTOMER=${value}
  elif [ "logo" == ${key} ]
  then
    #LOGO
    LOGO=${value}
  elif [ "config" == ${key} ]
  then
    #MTK配置文件"./device/zechin/${MTK_PROJECT}/ProjectConfig.mk"
    MTK_PROJECT_CONFIG=${value}
  fi
done

#修改电池参数
#if [ ${BATTERY} = "gs8_henxing305472p1500_425v" ]
#then
#    chgvalue.sh ${MTK_PROJECT_CONFIG} BATTERY_TYPE __PROJECT_BATTERY_GS8_HANGXIN_305472_1500_425V__
#elif [ ${BATTERY} = "gs8_henxing305465p1280_425v" ]
#then
#    chgvalue.sh ${MTK_PROJECT_CONFIG} BATTERY_TYPE __PROJECT_BATTERY_GS8_SHICHANG_305465_1450_425V__
#elif [ ${BATTERY} = "gs8p_henxing306081p1900_425v" ]
#then
#    chgvalue.sh ${MTK_PROJECT_CONFIG} BATTERY_TYPE __PROJECT_BATTERY_GS8P_HANGXIN_306081_1900_425V__
#fi

