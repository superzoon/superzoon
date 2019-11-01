#!/usr/bin/python3

import sys, re, os, datetime, configparser, tarfile, zipfile, socket, uuid
from os import (walk, path, listdir, popen, remove, rename, makedirs)
from os.path import (realpath, isdir, isfile, sep, dirname, abspath, exists, basename, getsize)
from shutil import (copytree, rmtree, copyfile, move)
from sys import argv
from zipfile import ZipFile

'''
    #***#开头表示换项目会修改的地方
    #*<*#开头表示换项目会修改的地方开始
    #*>*#开头表示换项目会修改的地方结束
'''

#*<*#
MTK_PROJECT_WEG = 'zechin6580_weg_m'
MTK_PROJECT_WE = 'zechin6580_we_m'
MTK_BANYAN_ADDON = 'mini_emulator_x86-userdebug'

#MTK项目名称
MTK_PROJECT = MTK_PROJECT_WEG
FULL_MTK_PROJECT = 'full_'+MTK_PROJECT_WEG
FULL_MTK_PROJECT_ENG = FULL_MTK_PROJECT+'-eng'
FULL_MTK_PROJECT_USER = FULL_MTK_PROJECT+'-user'
FULL_MTK_PROJECT_USERBUG = FULL_MTK_PROJECT+'-userdebug'
#MTK的ProjectConfig.mk文件
MTK_FULL_PROJECT_CONFIG = sep.join(['device', 'zechin', MTK_PROJECT, FULL_MTK_PROJECT+'.mk'])
MTK_PROJECT_CONFIG = sep.join(['device', 'zechin', MTK_PROJECT, 'ProjectConfig.mk'])
MTK_LK_CONFIG = sep.join(['vendor', 'mediatek', 'proprietary', 'bootable','bootloader','lk', 'project', MTK_PROJECT+'.mk'])
# *>*#
COMBO='combo'
PROJECT='project'
SCREEN='screen'
HARDWARE='hardware'
FLASH='flash'
BATTERY='battery'
LANGUAGE='language'
NETWORK='network'
CUSTOMER='customer'

ComboList = list(['user', 'eng', 'emulator'])
LanguageList = list(['huayu', 'chinese', 'foreign'])

#翻译，与用户交互的列表选择对应的翻译，可以在drive/xxx.xxx.xxx和merge/xxx.xxx.xxx文件中以每行key=value形式配置
TRANSLATE_DICT={COMBO:'版本','user':'用户版', 'eng':'工程版','emulator':'模拟器','normal':'通用',
                PROJECT:'项目',SCREEN:'屏幕',HARDWARE:'硬件', 'huayu':'华语','chinese':'中文','foreign':'外文'}
getZh = lambda en:TRANSLATE_DICT[en] if en in TRANSLATE_DICT.keys() else en

PROJECT_CONFIG = 'ProjectConfig.mk'
CUSTOMER_PROP = 'customer.prop'
EXPAND_CUSTOMER_PROP = 'expand_customer.prop'
BUILD_PROP = 'build.prop'
XHL_CUSTOMER=sep.join(['xhl','out','system', 'xhl', CUSTOMER_PROP])
DEF_BUILD=sep.join(['xhl','out','system', BUILD_PROP])
#icon的路径
ICONS_PATCH=sep.join(['xhl','out','system', 'xhl','icons'])
#MTK的ProjectConfig.mk文件
MTK_PROJECT_CONFIG = sep.join(['device', 'zechin', MTK_PROJECT, PROJECT_CONFIG])
#配置xhl/device目录key=value文件
DEVICE_OVERLAYS_FILE_MAP={
  PROJECT_CONFIG:MTK_PROJECT_CONFIG
}
DEVICE_OVERLAYS_VALUES_MAP=dict()
#配置xhl/merge目录key=value文件
MERGE_OVERLAYS_FILE_MAP={
  BUILD_PROP:DEF_BUILD,
  CUSTOMER_PROP:XHL_CUSTOMER,
}
MERGE_OVERLAYS_VALUES_MAP=dict()
#########################################################################################################

os.environ['PATH'] = dirname(abspath(__file__)) + ':' + os.environ['PATH']
#生成自动安装的install.bat 如果为False只会生产install_apk.bat编译好了后需要手动按enter键push
AUTO_PUSH = False

#添加tab键自动补全
try:
    import rlcompleter, readline, atexit
    readline.parse_and_bind('tab:complete')
    histfile = os.path.join(os.environ['HOME'], '.pythonhistory')
    readline.read_history_file(histfile)
    atexit.register(readline.write_history_file, histfile)
except Exception:
    pass
    # if argv and argv[0].split(sep)[-1] == 'tool.py':
    #     print('------------------------------------------------------------------\n'
    #           '请使用python3 pip install readline安装readline模块使其能够自动补全\n'
    #           '------------------------------------------------------------------\n')

#当前tool版本
xlan_tool_version='1.3'

#bashrc添加tool 方法
bashrc_file = sep.join([os.environ['HOME'],'.bashrc'])
lines = popen('cat '+bashrc_file+' | grep "xlan_tool_version=v"').read().splitlines()
if not lines or len(lines)==0:
    shell_tool_version = 0
else:
    version_match = re.match('xlan_tool_version=v([\d|\.]+)', lines[0])
    if version_match:
        shell_tool_version = float(version_match.group(1))
    else:
        shell_tool_version = 0
if float(xlan_tool_version) > shell_tool_version:
    tool_function = '''#xlan add start
xlan_tool_version=v'''+xlan_tool_version+'''
function tool(){
  if [ -f ./xhl/script/tool.py ];then
    python3 ./xhl/script/tool.py $@
  fi
}

_tool(){
    local cur prev opts
    COMPREPLY=()
    case ${COMP_CWORD} in
    0)  #仍在完成根命令
        ;;
    1)  #根命令完成,补充一级命令
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        opts="new svn_new svn_mm new_driver mm mmm buildimage build_boot driver driver_r svn_ci svn_restore svn_revert select cp cflag rid patch chgvalue apktool logo diff"

        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        ;;
    2|*)  #补充其它命令
        action="${COMP_WORDS[1]}"
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        #根据上面不同的opts通过eval开发不同的补全， 例如使用eval _sh
        if [ ${action} == "mm" ] || [ ${action} == "mmm" ]
        then
            opts="`tool all`"
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        else
          eval _longopt
        fi
        ;;
    esac
}

complete -o default -F _tool tool
#xlan add end
'''
    if isfile(bashrc_file):
        lines = open(bashrc_file, mode='r').readlines()
    else:
        lines = list()
    bashrc_lines = list()
    bashrc_temp = '.temp'
    with open(bashrc_temp, mode='w', encoding='utf-8') as f:
        inXlanContent = False
        for line in lines:
            if line.startswith('#xlan add start'):
                inXlanContent = True;
                bashrc_lines.append(tool_function)
            elif line.startswith('#xlan add end'):
                inXlanContent = False;
            elif not inXlanContent:
                bashrc_lines.append(line)
        f.writelines(bashrc_lines)
        f.flush()
        f.close()
        os.system('cp -r '+bashrc_temp+' '+bashrc_file)
        os.system('rm -r '+bashrc_temp)
        print('xlan_tool_version=v'+xlan_tool_version)

#添加xhl.mk到系统编译环境
base_mk = sep.join(['build', 'target', 'product', 'base.mk'])
xhl_mk = sep.join(['xhl', 'xhl.mk'])
if isfile(base_mk) and isfile(xhl_mk):
    lines = popen('grep "\$(call inherit-product, xhl/xhl.mk)" ./build -rH').read().splitlines()
    lines = [line for line in lines if len(line.split(':')) ==2 and not line.split(':')[1].startswith('#')]
    if not lines or len(lines[0])==0 or lines[0].startswith('#'):
        with open(base_mk, mode='a') as f:
            f.writelines('#xlan add start\n')
            f.writelines('$(call inherit-product, xhl/xhl.mk)\n')
            f.writelines('#xlan add end\n')
            f.flush()
            f.close()

#初始化driver目录
driver_path = sep.join(['xhl', 'driver'])
if not isdir(driver_path):
    os.makedirs(driver_path)
    driver_common = sep.join([driver_path, 'common'])
    os.makedirs(driver_common)
    driver_example = sep.join([driver_path, 'project_screen_hardware'])
    os.makedirs(driver_example)
    driver_example_common = sep.join([driver_example, 'common'])
    os.makedirs(driver_example_common)
    driver_template = sep.join(['xhl', 'driver', 'flash.network.customer.battery'])
    with open(driver_template, mode='w', encoding='utf-8') as file:
        file.writelines('flash = 字库\n')
        file.writelines('network = 网络\n')
        file.writelines('customer = 客户\n')
        file.writelines('battery = 电池\n')
        file.flush()
        file.close()

#初始化merge目录
merge_path = sep.join(['xhl', 'merge'])
if not isdir(merge_path):
    os.makedirs(merge_path)
    merge_common = sep.join([merge_path, 'common'])
    os.makedirs(merge_common)
    merge_example = sep.join([merge_path, 'project_screen'])
    os.makedirs(merge_example)
    merge_example_common = sep.join([merge_example, 'common'])
    os.makedirs(merge_example_common)
    merge_template = sep.join([merge_path, 'language.network.flash.customer'])
    with open(merge_template, mode='w', encoding='utf-8') as file:
        file.writelines('language = 语言\n')
        file.writelines('network = 网络\n')
        file.writelines('flash = 字库\n')
        file.writelines('customer = 客户\n')
        file.flush()
        file.close()

class Tool(object):

    # MTK before android5.0之前版本
    BEFORE_LOLLIPOP = isdir('mediatek')
    #MTK的mode文件路径
    if BEFORE_LOLLIPOP:
        MODE_FILES = lambda mode: sep.join(['mediatek', 'custom', 'common', 'modem', mode, 'BPLGUInfoCustomAppSrcP_*'])
    else:
        MODE_FILES = lambda mode:sep.join(['vendor', 'mediatek', 'proprietary', 'modem', mode, 'BPLGUInfoCustomAppSrcP_*'])

    #编译log的保存文件
    MAKE_LOG = 'make.log'
    MM_LOG = 'mm.log'

    #打补丁功能 自动打补丁
    auto_patch = False
    #自定覆盖差异文件
    auto_over_diff_patch = False
    #自动跳出错误提示
    auto_jump_warn = False

    #支持扩展定制system/xhl/customer.prop
    SUPPORT_CUSTOMER = False
    CUSTOMER_DICT = dict()

    #MTK是否root
    MTK_BUILD_ROOT = 'yes'
    #xhl_eng Android.mk中 ifeq (yes,$(xhl_eng)) 工程师添加自己想判断的
    XHL_ENG = False
    #编译后生成的配置文件，下次次执行命令的时候会使用此文件
    INI_FILE = sep.join([dirname(abspath(__file__)), 'xhl.ini'])
    #保存上次编译的参数
    INI_FILE_OLD = sep.join([dirname(abspath(__file__)), 'xhl_old.ini'])
    #保存curstomer的参数
    CURSTOMER_INI_FILE = sep.join([dirname(abspath(__file__)), 'xhl_curstomer.ini'])
    #保存mm的映射表
    MM_INI_FILE = sep.join([dirname(abspath(__file__)), 'xhl_mm.ini'])
    #回调驱动脚本
    DRIVER_CALL = sep.join([dirname(abspath(__file__)), 'call_driver.sh'])
    #回调new脚本
    NEW_CALL = sep.join([dirname(abspath(__file__)), 'call_new.sh'])
    #回调merge脚本
    MERGE_CALL = sep.join([dirname(abspath(__file__)), 'call_merge.sh'])
    #xhl目录
    XHL_PATH = dirname(dirname(abspath(__file__)))
    #xhl的driver配置目录
    DRIVE_ROOT_PATH = sep.join([XHL_PATH, 'driver'])
    #xhl打包配置目录
    MERGE_ROOT_PATH = sep.join([XHL_PATH, 'merge'])
    #xhl打包目录
    XHL_OUT = sep.join([XHL_PATH, 'out'])
    #xhl打包system目录
    OUT_SYSTEM = sep.join([XHL_OUT, 'system'])
    #xhl打包data目录
    OUT_DATA = sep.join([XHL_OUT, 'data'])
    #项目打包data目录
    PRODUCT_SYSTEM = sep.join(['out', 'target', 'product', MTK_PROJECT, 'system'])
    #项目打包data目录
    PRODUCT_DATA = sep.join(['out', 'target', 'product', MTK_PROJECT, 'data'])
    #项目MT6580_Android_scatter
    MT6580_Android_scatter = sep.join(['out', 'target', 'product', MTK_PROJECT, 'MT6580_Android_scatter.txt'])

    #颜色常量
    COLOR_START = '\033['
    COLOR_END = '\033[0m'
    COLOR_BG1 = '43;'
    COLOR_BG2 = '42;'
    #是否为自动new 例如输入./mm_new 1 1 1 1 1 1 1 1 1就会根据输入参数自动编译不会提示用户输入
    mAutoNew = False
    mAutoBuild = False
    #drive目录中获取的参数项 project,screen,version,.....
    DRIVE_PARAMETER = list()
    #MERGE目录中获取的参数项 project,screen,.....
    MERGE_PARAMETER = list()
    #DRIVE_PARAMETER与MERGE_PARAMETER合并，供列表选项
    ALL_PARAMETER = list()
    #用户选择的参数index 例如1，1，2，3，1，
    PARAMETER_SELECT = list()
    #存储每个列表中对应有哪些选项
    PARAMETER_LIST_MAP = dict()

    @classmethod
    def getMmPath(cls, modulename, is_mm = False):
        ''' mm编译模块 模糊查询模块路径
        :param modulename: 
        :param is_mm: 
        :return: 返回查到的路径 是关键字或者没有查到或者看不上眼就返回None
        '''
        os.system('stty erase ^H')
        comm = ['mm', 'mma', 'mmm', 'mmma', 'lk', 'ptgen', 'pl', 'clean', 'kernel', 'preloader', 'bootimage', 'systemimage', 'dataimage']
        if isdir(modulename) or not isfile(Tool.MM_INI_FILE) or (not is_mm and modulename in comm):
            return None
        #构建高亮字符串函数
        def getPrintText(bg_color, name, array):
            printText=''.join([cls.COLOR_START, bg_color ,'30m',name,':  \n'])
            for i in range(1, len(array)+1):
                printText = ''.join([printText,  cls.COLOR_START, '31m ' , str(i), '--', array[i - 1],'\n' if i%4==0 else '    '])
            printText = ''.join([printText, cls.COLOR_END])
            return printText

        modulename = modulename.lower()
        mmConf = dict()
        Tool.addConfig(Tool.MM_INI_FILE, mmConf, pattern=r'([A-Z|0-9|_|a-z|\-]*)([ |:|=]+)(.*)')
        mmConf_lower = dict()
        for item in mmConf.keys():
            mmConf_lower[item.lower()] = mmConf[item]
        if modulename in mmConf_lower:
            return mmConf_lower[modulename]
        selectList = [ name for name in mmConf_lower.keys() if name.startswith(modulename) or name.endswith(modulename) or (is_mm and name.__contains__(modulename))]
        moduleList = [item for item in mmConf.keys() if item.lower() in selectList]

        if len(moduleList) == 0:
            return None
        elif len(moduleList) == 1:
            modulename = moduleList[0]
        elif not modulename in moduleList:
            moduleList.append('看不上眼')
            moduleList = sorted(moduleList)
            getStrStype1 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG1 + '31m' + strings + Tool.COLOR_END
            printStrStype1 = lambda strings: print(getStrStype1(strings))
            getStrStype2 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + strings + Tool.COLOR_END
            printStrStype2 = lambda strings: print(getStrStype2(strings))
            modulename = None
            while (not modulename):
                choice = input(getPrintText(cls.COLOR_BG1, '选择模块名称(输入数字或者模块名称)', moduleList) + '\n')
                if choice in moduleList:
                    modulename = choice
                elif (choice.isdigit() and int(choice) <= len(moduleList)):
                    modulename = moduleList[int(choice) - 1]
                else:
                    printStrStype1('输入错误\n')
        if modulename in mmConf:
            return mmConf[modulename]
        else:
            return None

    @classmethod
    def getJob(cls):
        '''
        :return: 返回cpu的核心数
        '''
        lines = popen('cat /proc/cpuinfo | grep processor | wc -l').read()
        for line in lines.splitlines():
            return line.strip()
        return '4'

    @classmethod
    def save_parameters_to_file(cls, inputArray, file=INI_FILE):
        ''' 保存用户输入的数字到文件        
        :param inputArray: 输入的数字列表
        :param file: 保存的名称
        '''
        if not isdir(dirname(file)):
            os.makedirs(dirname(file))
        try:
            iniFile = open(file, mode='w')
            iniFile.writelines('###################### start {}########################## \n\n'.format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            iniFile.writelines('parameter={}\n\n'.format(inputArray))
            for parameter in Tool.ALL_PARAMETER:
                key=parameter
                key_zh=getZh(key)
                index = Tool.ALL_PARAMETER.index(parameter)
                values = Tool.PARAMETER_LIST_MAP[parameter]
                if len(values)==0:
                    value=key
                else:
                    value=values[inputArray[index]-1]
                iniFile.writelines('#{}\n'.format(key_zh))
                iniFile.writelines('xhl_{}={}\n\n'.format(key, value))

            iniFile.writelines('####################### end #########################')
            iniFile.close()
            #print(os.system('cat '+file))
        except Exception as e:
            print('当前路径无法创建配置文件', e)

    @classmethod
    def readParameters(cls, readFile=INI_FILE):
        ''' 根据上次保存的文件读取上次的参数(先检查配置参数key=value，如果检查不成功就检查parameter数组) 
        :param readFile: 读取的文件名
        :return: 返回是否读取成功
        '''
        if isfile(readFile):
            lines = open(file=readFile, mode='r', encoding=Tool.checkFileCode(readFile)).readlines();
            pars = list()
            for line in lines:
                match = re.match('^xhl_([\w]+)=([\w]+)', line.replace(' ','').strip())
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if key in Tool.PARAMETER_LIST_MAP.keys() and value in Tool.PARAMETER_LIST_MAP[key]:
                        index = Tool.PARAMETER_LIST_MAP[key].index(value)+1
                        if index > 0 :
                            pars.append(str(index))
                    else:
                        pars.append('-1')
            isCheckSucceed = cls.checkParameterArray(pars, saveToFile=False)
            if isCheckSucceed:
                return True
            for line in lines:
                match = re.match('^parameter=\\[(.+)\\]', line.replace(' ','').strip())
                if match:
                    return cls.checkParameterArray(match.group(1).split(','), saveToFile=False)
        return False

    @classmethod
    def setParameters(cls, saveToFile=True, readFile=INI_FILE_OLD, dialog = False):
        '''与用户交互 获取用户输入的参数保存到对应的成员变量
        :param saveToFile: 保存文件
        :param readFile: 读取文件
        :return: 返回用户输入
        '''
        if not isfile(readFile) and isfile(Tool.INI_FILE):
            readFile = Tool.INI_FILE
        elif not isfile(readFile) and isfile(Tool.INI_FILE_OLD):
            readFile = Tool.INI_FILE_OLD
        #构建高亮字符串函数
        def getPrintText(bg_color, name, index, array):
            printText=''.join([cls.COLOR_START, bg_color ,'30m ',name,':  '])
            for i in range(1, len(array)+1):
                printText = ''.join([printText,  cls.COLOR_START, '31m ' if index == i else '30m ', str(i), '--', array[i - 1],'    '])
            printText = ''.join([printText, cls.COLOR_END])
            return printText
        indexList = list()
        while len(indexList) < len(Tool.ALL_PARAMETER):
            indexList.append('1')

        if isfile(readFile):
            for line in open(file=readFile, mode='r', encoding=Tool.checkFileCode(readFile)).readlines():
                match = re.match('^parameter=\\[(.+)\\]', line.replace(' ','').strip())
                if match:
                    parameters = match.group(1).split(',')
                    for index in [index for index in range(0, len(indexList)) if index < len(parameters)]:
                        indexList[index] = parameters[index]

        for index in range(0, len(indexList)):
            num =  indexList[index].strip()
            if num.isdigit() and int(num) > 0:
                indexList[index] = int(num)

        title_list=list()
        title_list.append('\n请输入你的选项,以空格隔开')
        msg = list()
        for name in Tool.ALL_PARAMETER:
            index = Tool.ALL_PARAMETER.index(name)
            name_zh = getZh(name)
            values_zh = list()
            if len(Tool.PARAMETER_LIST_MAP[name])==0:
                values_zh.append('通用')
            else:
                for value in Tool.PARAMETER_LIST_MAP[name]:
                    values_zh.append(getZh(value))
            title_list.append(str(index + 1) + ')' + getPrintText(Tool.COLOR_BG1 if index%2==0 else Tool.COLOR_BG2, name_zh, indexList[index], values_zh))
            msg.append(str(index+1)+'.'+name_zh)
        printText = Tool.COLOR_START + Tool.COLOR_BG1 + '31m输入方式1:直接输入数字  输入方式2:输入[序号]:[数字]  输入方式3:输入[名称]:[数字]'+Tool.COLOR_START + Tool.COLOR_BG2 + '30m\n' \
                    '    提示：1.输入方式3":/："符号可以可无 2.未输入的按高亮的选择 3.使用":/："方式输入可以不按顺序输入'+ Tool.COLOR_END+'\n\n'\
                    +'请输入:'+' '.join(msg)+ '\n'+Tool.COLOR_START + Tool.COLOR_BG1 + '31m当前使用项目:' + MTK_PROJECT + Tool.COLOR_END
        os.system('stty erase ^H')
        err_str=''
        while True:
            print('\n'.join(title_list))
            print(printText)
            print()
            if len(err_str)>0:
                print('('+err_str+')')
                err_str=''
            readLine = input().strip()
            inputArray = readLine.split(' ')
            #用户没有输入就为空数组
            if len(inputArray)==1 and len(inputArray[0])==0:
                inputArray = list()

            choiceList = [str(choice) for choice in indexList]
            choiceIndex = 0
            #根据用户的输入填写用户的选择
            for choice in inputArray:
                match = re.match('^([^\d|^:|^：]+)[:|：]?(\d+)', choice)
                if not match:
                    match = re.match('^(\d+)[:|：](\d+)', choice)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if key.isdigit():
                        choiceIndex = int(key)-1
                        choiceList[choiceIndex] = value
                    elif key in nameList:
                        choiceIndex = nameList.index(key)
                        choiceList[choiceIndex] = value
                    else:
                        choiceList[choiceIndex] = value
                    # print('choiceIndex---'+str(choiceIndex)+':  '+key+'---'+value)
                elif choiceIndex < len(Tool.ALL_PARAMETER):
                    choiceList[choiceIndex] = choice
                choiceIndex = choiceIndex+1
            #检测用户输入正确性
            choice = int(choiceList[Tool.ALL_PARAMETER.index(PROJECT)])
            if choice <= len(Tool.PARAMETER_LIST_MAP[PROJECT]):
                mProject = Tool.PARAMETER_LIST_MAP[PROJECT][choice-1]
            else:
                mProject = PROJECT

            choice = int(choiceList[Tool.ALL_PARAMETER.index(SCREEN)])
            if choice <= len(Tool.PARAMETER_LIST_MAP[SCREEN]):
                mScreen = Tool.PARAMETER_LIST_MAP[SCREEN][choice-1]
            else:
                mScreen = SCREEN

            choice = int(choiceList[Tool.ALL_PARAMETER.index(HARDWARE)])
            if choice <= len(Tool.PARAMETER_LIST_MAP[HARDWARE]):
                mHardware = Tool.PARAMETER_LIST_MAP[HARDWARE][choice-1]
            else:
                mHardware = HARDWARE

            driverName = '_'.join([mProject, mScreen, mHardware])
            if not isdir(sep.join([cls.DRIVE_ROOT_PATH, driverName])):
                err_str = ''.join([cls.COLOR_START, cls.COLOR_BG2, '31m没有找到驱动', driverName, '请重新选择 ', cls.COLOR_END])
            elif Tool.checkParameterArray(choiceList, saveToFile, dialog):
                return choiceIndex
            else:
                err_str = ''.join([cls.COLOR_START, cls.COLOR_BG2, '31m请输入正确的数字', cls.COLOR_END])
        return list()

    @classmethod
    def checkParameterArray(cls, inputArray, saveToFile=True, dialog=False):
        '''检查输入的参数是否正确，并尝试修复参数个数 ，如果为用户输入则保存到配置文件      
        :param inputArray: 输入的参数数组
        :param saveToFile: 是否保存文件
        :return: 返回参数是否正确
        '''
        getStrStype1 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG1 + '31m' + strings + Tool.COLOR_END
        printStrStype1 = lambda strings: print(getStrStype1(strings))
        getStrStype2 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + strings + Tool.COLOR_END
        printStrStype2 = lambda strings: print(getStrStype2(strings))
        for num in inputArray:
            if not num.strip().isdigit() or int(num)<1:
                return False

        while len(inputArray) < len(Tool.ALL_PARAMETER):
            inputArray.append(1)

        while len(inputArray) > len(Tool.ALL_PARAMETER):
            del inputArray[len(Tool.ALL_PARAMETER)]

        for i in range(0, len(inputArray)):
            inputArray[i] =int(inputArray[i])

        for paramter in Tool.ALL_PARAMETER:
            index = Tool.ALL_PARAMETER.index(paramter)
            choice = inputArray[index]
            paramters = list()
            if paramter in Tool.PARAMETER_LIST_MAP.keys():
                paramters = Tool.PARAMETER_LIST_MAP[paramter]
            if (choice>1 and len(paramters)==0) or (choice>len(paramters) and len(paramters)>0):
                return False
        Tool.PARAMETER_SELECT = inputArray
        if dialog and not saveToFile:
            choice = input(getStrStype2('参数修改是否保存,如果保存请输入')+getStrStype1('(y/Y)')+getStrStype2('，不保存直接回车')+'\n')
            if choice == 'Y' or choice == 'y':
                saveToFile = True
        if saveToFile:
            cls.save_parameters_to_file(inputArray)
        return True

    @classmethod
    def getParamter(cls, key):
        choiceList = Tool.PARAMETER_SELECT
        choice = int(choiceList[Tool.ALL_PARAMETER.index(key)])
        if choice <= len(Tool.PARAMETER_LIST_MAP[key]):
            return Tool.PARAMETER_LIST_MAP[key][choice - 1]
        else:
            return key

    @classmethod
    def checkSelect(cls):
        ''' 检查输入的参数是否有对应的驱动，如果不正确提示用户重新输入 '''
        mProject = Tool.getParamter(PROJECT)
        mScreen = Tool.getParamter(SCREEN)
        mHardware = Tool.getParamter(HARDWARE)
        driverPathName = '_'.join([mProject, mScreen, mHardware])
        if not isdir(sep.join([cls.DRIVE_ROOT_PATH, driverPathName])):
            input(''.join([cls.COLOR_START, cls.COLOR_BG2, '30m没有找到驱动',driverPathName,'请会车键后重选择 ', cls.COLOR_END]))
            if isfile(cls.INI_FILE):
                os.remove(cls.INI_FILE)
            os.system(abspath(__file__)+' new')
            sys.exit(0)

        show_msg =cls.COLOR_START+cls.COLOR_BG1+'30m '
        for key in Tool.ALL_PARAMETER:
            index = Tool.ALL_PARAMETER.index(key)
            key_zh = getZh(key)
            choice = int(Tool.PARAMETER_SELECT[index])
            if len(Tool.PARAMETER_LIST_MAP[key]) ==0 :
                value = key
            else:
                value = getZh(Tool.PARAMETER_LIST_MAP[key][choice-1])
            show_msg = show_msg+cls.COLOR_START+('31m' if index%2==0 else '30m')+key_zh+':'+value+' '
        print(show_msg+cls.COLOR_END)

        if not cls.mAutoNew:
            printText = cls.COLOR_START+cls.COLOR_BG2+'30m请确认你的选择,如果确认请输入y/Y,输入n/N或其它键重新选择,否则按 ctrl+c 退出'+cls.COLOR_END+'\n'
            choice = input(printText).lower()
            if len(choice) != 0 and choice != 'y':
                if isfile(cls.INI_FILE) and isfile(cls.INI_FILE_OLD):
                    os.remove(cls.INI_FILE_OLD)
                os.rename(cls.INI_FILE, cls.INI_FILE_OLD)
                os.system(abspath(__file__)+' new '+ ('o' if 'o' in argv or 'O' in argv else ''))
                sys.exit(0)

    @classmethod
    def setAutoNew(cls, inputArray):
        ''' 设置是否为自动编译 svn_new特有功能'''
        Tool.mAutoNew = len(inputArray)>0 and cls.checkParameterArray(inputArray, saveToFile=True)
        return Tool.mAutoNew

    @classmethod
    def checkDriveList(cls, isShowList = False):
        ''' 根据xhl/driver 和xhl/merge 自动检测本项目的编译参数，删除多余的参数列表，添加没有的参数列表
        :param isShowList: 是否打印出所支持的驱动
        '''

        #检测android项目检测android项目MTK_PROJECT
        is_mtk_project = False
        if isfile('mk'):
            lines = [line.strip() for line in popen('./mk listp').read().splitlines()]
            if MTK_PROJECT in lines:
                is_mtk_project = True

        else:
            lines = [line.split(' ')[-1] for line in popen('find device/ -name vendorsetup.sh | xargs grep {} -rHn'.format(MTK_PROJECT)).read().splitlines()]
            if FULL_MTK_PROJECT_ENG in lines and FULL_MTK_PROJECT_USER in lines :
                is_mtk_project = True

        if not is_mtk_project or not isfile(MTK_PROJECT_CONFIG):
            printText = cls.COLOR_START + cls.COLOR_BG2 + '30m请配置脚本Tool中的 MTK_PROJECT，FULL_MTK_PROJECT_ENG，FULL_MTK_PROJECT_USER, MTK_PROJECT_CONFIG' + cls.COLOR_END + '\n'
            choice = input(printText+'继续请按y/Y,其它键退出:')
            if choice != 'y' and choice != 'Y':
                exit(-1)

        # 检测driver目录
        if not isdir(cls.DRIVE_ROOT_PATH) or len(listdir(cls.DRIVE_ROOT_PATH))==0:
            printText = cls.COLOR_START + cls.COLOR_BG2 + '30m没有检测到驱动...' + cls.COLOR_END
            choice = input(printText + '继续请按y/Y,其它键退出:')
            if choice != 'y' and choice != 'Y':
                exit(-1)

        def findParameter(dirPath, pattern, parameters, parameterDict, overlays=DEVICE_OVERLAYS_FILE_MAP):
            findDrive = ''.join([cls.COLOR_START, cls.COLOR_BG2, '30m'])
            project_dir_list = list()
            parameter_dir_list = list()
            parameter_list = list()
            for filename in listdir(dirPath):
                filePath = sep.join([dirPath, filename])
                mathDir = re.match(pattern,filename)
                mathFile = re.match('^(([\w\+]*)\.?)+',filename)
                if mathDir and isdir(filePath):
                    findDrive = ' '.join([findDrive, cls.COLOR_START,'31m' if len(project_dir_list)%2 else '30m', filename])
                    project_dir_list.append(filePath)
                    for child_dir in [child for child in listdir(filePath)]:
                        if isdir(sep.join([filePath,child_dir])) and (child_dir not in parameter_dir_list) and (child_dir!='common'):
                            parameter_dir_list.append(child_dir)
                    items = mathDir.groups()
                    for item in items:
                        key = parameters[items.index(item)]
                        if key not in parameterDict.keys():
                            parameterDict[key] = list()
                        if item not in parameterDict[key]:
                            parameterDict[key].append(item)
                elif mathFile and isfile(filePath) and len(filename.split('.'))>=3:
                    encode = Tool.checkFileCode(filePath)
                    if encode == None:
                        encode = 'gbk'
                    #读取文件中配置的翻译
                    for line in [ line.replace('\n','').strip() for line in open(filePath, mode='r',encoding = encode).readlines()]:
                        match = re.match(r'^([\w|\.]+) ?= ?(.+)$', line)
                        if match and match.group(1).strip()=='OVERLAYS_MAP':
                            for (key, value) in [item.split(':') for item in match.group(2).strip().split(',')]:
                                if key and value:
                                    overlays[key.strip()]=value.strip()
                        elif match and match.group(1).strip() not in TRANSLATE_DICT:
                            TRANSLATE_DICT[match.group(1).strip()] = match.group(2).strip()
                    #根据文件名称添加参数列表
                    parameter_list = filename.split('.')
                    for parameter in [parameter for parameter in parameter_list if parameter not in parameters]:
                        parameters.append(parameter)
                elif mathFile and isdir(filePath) and filename != 'common':
                    parameter_dir_list .append(filename)
            #从xxx.xxx.xxx.xxx目录中获取参数列表内容
            for parameter_dir in parameter_dir_list:
                items = parameter_dir.split('.')
                for item in [item for item in items if items.index(item)<len(parameter_list)]:
                    key = parameter_list[items.index(item)]
                    if key not in parameterDict.keys():
                        parameterDict[key] = list()
                    if item not in parameterDict[key] and key!=item:
                        parameterDict[key].append(item)
            for parameter in [parameter for parameter in parameters if parameter not in Tool.ALL_PARAMETER]:
                Tool.ALL_PARAMETER.append(parameter)
            return ''.join([cls.COLOR_START, cls.COLOR_BG1, '30m驱动支持', str(len(project_dir_list)), '个分别为:\n', cls.COLOR_END, findDrive, cls.COLOR_END])

        Tool.ALL_PARAMETER.append(COMBO)
        Tool.PARAMETER_LIST_MAP[COMBO]=ComboList
        Tool.PARAMETER_LIST_MAP[LANGUAGE]=LanguageList
        #查找驱动目录，获取参数选项
        Tool.DRIVE_PARAMETER = [PROJECT,SCREEN,HARDWARE]
        drive_pattern = '^([a-z0-9\+]+_\d+[a-z]?)_([a-z0-9\+]+)_(v\d+[a-z0-9\+]*)$'
        showMsg = findParameter(Tool.DRIVE_ROOT_PATH, drive_pattern, Tool.DRIVE_PARAMETER, Tool.PARAMETER_LIST_MAP, DEVICE_OVERLAYS_FILE_MAP)

        if isShowList:
            print(showMsg)

        #查找驱动目录，获取参数选项
        Tool.MERGE_PARAMETER = [PROJECT,SCREEN]
        merge_pattern = '^([a-z0-9\+]+_\d+[a-z]?)_([a-z0-9\+]+)$'
        findParameter(Tool.MERGE_ROOT_PATH, merge_pattern, Tool.MERGE_PARAMETER, Tool.PARAMETER_LIST_MAP, MERGE_OVERLAYS_FILE_MAP)
        for key in [parameter for parameter in Tool.ALL_PARAMETER if not parameter in Tool.PARAMETER_LIST_MAP.keys()]:
            Tool.PARAMETER_LIST_MAP[key] = list()

        if LANGUAGE in Tool.ALL_PARAMETER:
            Tool.ALL_PARAMETER.remove(LANGUAGE)
            Tool.ALL_PARAMETER.insert(6, LANGUAGE)

        for parameter in Tool.ALL_PARAMETER[1:]:
            if parameter != LANGUAGE:
                Tool.PARAMETER_LIST_MAP[parameter] = sorted(Tool.PARAMETER_LIST_MAP[parameter])
            if parameter == CUSTOMER and 'normal' not in Tool.PARAMETER_LIST_MAP[parameter]:
                Tool.PARAMETER_LIST_MAP[parameter].insert(0,'normal')
        for key in DEVICE_OVERLAYS_FILE_MAP.keys():
            DEVICE_OVERLAYS_VALUES_MAP[key]=dict()
        for key in MERGE_OVERLAYS_FILE_MAP.keys():
            MERGE_OVERLAYS_VALUES_MAP[key]=dict()
        # print(TRANSLATE_DICT)
        # print(Tool.ALL_PARAMETER)
        # print(Tool.PARAMETER_LIST_MAP)
        #print(DEVICE_OVERLAYS_FILE_MAP)
        #print(DEVICE_OVERLAYS_VALUES_MAP)
        #print(MERGE_OVERLAYS_FILE_MAP)
        #print(MERGE_OVERLAYS_VALUES_MAP)


    @classmethod
    def addSupportCustomer(cls, file, curstomerDict=CUSTOMER_DICT):
        '''添加支持的customer选项  用于buildimgae -e
        :param file: 从这个文件里面读出customer选项
        :param curstomerDict: 读取的选项保存到这个字典中
        '''
        if Tool.SUPPORT_CUSTOMER and isfile(file):
            customer_file = open(file, mode='r', encoding=Tool.checkFileCode(file))
            for line in customer_file.readlines():
                match = re.match(r'^([^\:]+\:[^\:|^ ]+) ?= ?\[(.+)\]$', line)
                if match:
                    key = match.group(1)
                    values = [value.strip() for value in match.group(2).strip().split(',')]
                    curstomerDict[key]=values
            customer_file.close()
        return curstomerDict

    @classmethod
    def addToMap(cls, file, buildDict, pattern=None):
        '''
        :param file: 从这个文件里面读出customer选项
        :param buildDict: 读取的选项保存到这个字典中
        '''
        if isfile(file):
            build_file = open(file, mode='r', encoding=Tool.checkFileCode(file))
            pattern = r'([\w|_|\.]*)([ |:|=]+)(.*)' if not pattern else pattern
            for line in build_file.readlines():
                match = re.match(pattern, line)
                if match:
                    key = match.group(1)
                    value = match.group(3)
                    buildDict[key]=value
                build_file.close()
        return buildDict

    @classmethod
    def addConfig(cls, file, projectConfigDict, pattern=None):
        '''添加ProjectConfig选项        
        :param file: 从这个文件里面读出ProjectConfig选项
        :param projectConfigDict: 读取的选项保存到这个字典中
        '''
        if isfile(file):
            project_file = open(file, mode='r', encoding=Tool.checkFileCode(file))
            pattern = r'([A-Z|0-9|_]*)([ |:|=]+)(.*)' if not pattern else pattern
            for line in project_file.readlines():
                match = re.match(pattern, line)
                if match:
                    key = match.group(1)
                    value = match.group(3)
                    projectConfigDict[key]=value
                project_file.close()
        return projectConfigDict

    @classmethod
    def selectCustomer(cls,curstomerDict=CUSTOMER_DICT, layerName='DEFAULT'):
        '''让用户根据以前的提示选择参数      
        :param curstomerDict: 
        :param layerName: 配置层为mScreen.mFlash.mLanguage.mNetwork.mCustomer
        '''
        getStrStype1 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG1 + '31m' + strings + Tool.COLOR_END
        printStrStype1 = lambda strings: print(getStrStype1(strings))
        getStrStype2 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + strings + Tool.COLOR_END
        printStrStype2 = lambda strings: print(getStrStype2(strings))
        #删除xhl/out目录中的customer.prop，非system中的customer.prop
        outCustomerProp = sep.join([Tool.XHL_OUT, CUSTOMER_PROP])
        if isfile(outCustomerProp):
            os.remove(outCustomerProp)

        if Tool.SUPPORT_CUSTOMER and len(curstomerDict)>0:
            #初始化参数配置 customerConf
            customerConf = configparser.ConfigParser()
            customerConf.read(Tool.CURSTOMER_INI_FILE)
            defaultConf = customerConf.defaults()
            defaultConf['date_time'] = datetime.datetime.now()
            if not layerName in customerConf:
                customerConf[layerName] = dict()

            #初始化system目录下的customer.prop
            xhlPath = sep.join([Tool.OUT_SYSTEM, 'xhl'])
            if not isdir(xhlPath):
                os.makedirs(xhlPath)
            curstomerFile = sep.join([xhlPath, CUSTOMER_PROP])
            if not isfile(curstomerFile):
                os.mknod(curstomerFile)

            #定义显示的字符串函数
            def getPrintText(bg_color, name, choiceIndex, array):
                printText = ''.join([cls.COLOR_START, bg_color, '34m ', name, ':  '])
                for i in range(1, len(array) + 1):
                    printText = ''.join([printText, cls.COLOR_START, bg_color, '31m ' if i==(choiceIndex) else '30m ', str(i), '--', array[i - 1], '    '])
                printText = ''.join([printText, cls.COLOR_END])
                return printText

            #遍历字典让用户选择参数
            os.system('stty erase ^H')
            #初始化 选项
            keys = curstomerDict.keys()
            values = [value for value in curstomerDict.values()]
            keys_zh = [key.split(':')[0] for key in keys]
            keys_en = [key.split(':')[1] for key in keys]
            #初始化 用户选择
            choices = list()
            for key_en in keys_en:
                index = keys_en.index(key_en)
                choiceIndex = 1
                if key_en.lower() in customerConf[layerName]:
                    value = customerConf[layerName][key_en.lower()]
                    if value in values[index]:
                        choiceIndex = values[index].index(value)+1
                elif key_en.lower() in defaultConf:
                    value = defaultConf[key_en.lower()]
                    if value in values[index]:
                        choiceIndex = values[index].index(value)+1
                choices.append(choiceIndex)
            #打印出所有选项
            print_text = ''
            for key_zh in keys_zh:
                index = keys_zh.index(key_zh)
                print_text = print_text + str(index+1)+')'+getPrintText(Tool.COLOR_BG1 if index % 2 == 0 else Tool.COLOR_BG2, key_zh, choices[index], values[index])+'\n'

            print_text = print_text + Tool.COLOR_START + Tool.COLOR_BG1 + '31m输入方式1:直接输入数字  输入方式2:输入[序号]:[数字]  输入方式3:输入[名称]:[数字]' + Tool.COLOR_START + Tool.COLOR_BG2 + '30m\n'                                                                                                                                                   '    提示：1.输入方式3":/："符号可以可无 2.未输入的按高亮的选择 3.使用":/："方式输入可以不按顺序输入' + Tool.COLOR_END
            err_text = None
            choiceList = list()
            while True:
                print(print_text)
                if err_text:
                    print(err_text)
                    err_text = None
                readLine = input().strip()
                inputArray = readLine.split(' ')
                # 用户没有输入就为空数组
                if len(inputArray) == 1 and len(inputArray[0]) == 0:
                    inputArray = list()

                if len(choiceList) == 0:
                    choiceList = [str(choice) for choice in choices]
                choiceIndex = 0
                # 根据用户的输入填写用户的选择
                has_err = False
                for choice in inputArray:
                    match = re.match('^([^\d|^:|^：]+)[:|：]?(\d+)', choice)
                    if not match:
                        match = re.match('^(\d+)[:|：](\d+)', choice)
                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        if key.isdigit():
                            choiceIndex = int(key) - 1
                            choiceList[choiceIndex] = value
                        elif key in nameList:
                            choiceIndex = keys_zh.index(key)
                            choiceList[choiceIndex] = value
                        else:
                            choiceList[choiceIndex] = value
                            # print('choiceIndex---'+str(choiceIndex)+':  '+key+'---'+value)
                    elif choiceIndex <= len(key_en):
                        choiceList[choiceIndex] = choice

                    # 检测用户输入正确性 输入为数字 且数字小于等于选择个数 大于等于1
                    if not choiceList[choiceIndex] or not choiceList[choiceIndex].isdigit() \
                            or int(choiceList[choiceIndex]) > len(values[index]) \
                            or int(choiceList[choiceIndex]) < 1:
                        index_err_text = getStrStype2(str(choiceIndex+1)+' '+keys_zh[choiceIndex]+') 选项输入错误!')
                        if err_text:
                            err_text = err_text + '\n' + index_err_text
                        else:
                            err_text = '\n' + index_err_text
                        has_err = True
                    choiceIndex = choiceIndex + 1
                #如果输入有错误就重新输入那个选项
                if has_err:
                    continue
                #用户核查
                select_text = ''
                for key_zh in keys_zh:
                    index = keys_zh.index(key_zh)
                    select_text = select_text + getStrStype2(key_zh+':'+values[index][int(choiceList[index])-1]+' ')

                choice = input(select_text+'\n'+getStrStype1('重新选择请按(N/n),确定请回车或者按(Y/n)')+'\n')
                if not (len(choice) == 0 or choice=='Y' or choice=='y'):
                    continue

                #修改配置
                for key_en in keys_en:
                    index = keys_en.index(key_en)
                    choice = choiceList[index]
                    curstomerValue = values[index][int(choice)-1]
                    Tool.chgvalue(curstomerFile, key_en, curstomerValue, '=')
                    customerConf[layerName][key_en.lower()]=curstomerValue
                    defaultConf[key_en.lower()]=curstomerValue

                # 保存选择参数
                with open(Tool.CURSTOMER_INI_FILE, mode='w') as customerFile:
                    customerConf.write(customerFile)
                break

    @classmethod
    def releaseExecute(cls, src, dst, taskList, index, array, prefix = '', values_map=DEVICE_OVERLAYS_VALUES_MAP):
        '''执行覆盖命令        
        :param src: 源目录
        :param dst: 目标目录
        :param taskList: 队列列表
        :param index: 索引
        :param array: 目录构建的数组
        :param prefix: 目录的前缀
        :param values_map: 读取的选项保存到这个字典中
        '''
        if index < len(array):
            childArray = array[index]
            for i in range(0, len(childArray)):
                newPrefix = childArray[i] if not len(prefix) else prefix+'.'+childArray[i]
                taskList.append([index+1, newPrefix])
                comm = 'cp -R '+sep.join([src, newPrefix, '*'])+' '+dst
                if isdir(sep.join([src, newPrefix])):
                    print(comm)
                    os.system(comm)
                    for fileName in listdir(sep.join([src, newPrefix])):
                        filePath = sep.join([src, newPrefix, fileName])
                        if isfile(filePath) and fileName == EXPAND_CUSTOMER_PROP:
                            Tool.addSupportCustomer(filePath)
                            print('SupportCustomer --> '+filePath)
                        elif fileName in values_map.keys() and isfile(filePath):
                            Tool.addToMap(filePath, values_map[fileName])
                            print('key=value --> '+filePath)


    @classmethod
    def release(cls, src, dst, array, isMergeRoot=False, values_map=DEVICE_OVERLAYS_VALUES_MAP):
        '''覆盖文件类方法，包括common目录和根据array传入的参数构建出来的目录
        :param src: 源目录
        :param dst: 目标目录
        :param array: 目录构建的数组
        :param isMergeRoot: 是否为merge的顶层目录
        '''
        if not isMergeRoot:
            for fileName in listdir(src):
                filePath = sep.join([src, fileName])
                if isfile(filePath) and fileName == EXPAND_CUSTOMER_PROP:
                    Tool.addSupportCustomer(filePath)
                    print('SupportCustomer --> '+filePath)
                elif fileName in values_map.keys() and isfile(filePath):
                    Tool.addToMap(filePath, values_map[fileName])
                    print('key=value --> '+filePath)
        common_path = sep.join([src, 'common'])
        if isdir(common_path):
            comm = 'cp -R ' + sep.join([src, 'common', '*']) + ' ' + dst
            print(comm)
            os.system(comm)
            for fileName in listdir(sep.join([src, 'common'])):
                filePath = sep.join([src, 'common', fileName])
                if isfile(filePath) and fileName == EXPAND_CUSTOMER_PROP:
                    Tool.addSupportCustomer(filePath)
                    print('SupportCustomer --> '+filePath)
                elif fileName in values_map.keys() and isfile(filePath):
                    Tool.addToMap(filePath, values_map[fileName])
                    print('key=value --> '+filePath)

        taskList = list()
        Tool.releaseExecute(src, dst, taskList, 0, array, values_map=values_map)
        while len(taskList) > 0:
            parameter = taskList.pop(0)
            Tool.releaseExecute(src, dst, taskList, parameter[0], array, parameter[1], values_map=values_map)
        #拷贝结束后删除配置key=value文件
        if values_map==DEVICE_OVERLAYS_VALUES_MAP:
            for file in [file for file in DEVICE_OVERLAYS_VALUES_MAP.keys() if isfile(file)]:
                remove(file)
        else:
            for file in [sep.join([Tool.XHL_OUT, file]) for file in MERGE_OVERLAYS_VALUES_MAP.keys() if isfile(sep.join([Tool.XHL_OUT, file]))]:
                remove(file)

    @classmethod
    def copyDriverFiles(cls):
        '''拷贝驱动文件'''
        mProject = Tool.getParamter(PROJECT)
        mScreen = Tool.getParamter(SCREEN)
        mHardware = Tool.getParamter(HARDWARE)

        fileName='_'.join([mProject, mScreen, mHardware])
        dst = './'
        array = list()
        for parameter in Tool.DRIVE_PARAMETER[3:]:
            array.append([parameter, Tool.getParamter(parameter)])
        src = Tool.DRIVE_ROOT_PATH
        Tool.release(src, dst, array, isMergeRoot=False, values_map=DEVICE_OVERLAYS_VALUES_MAP)
        src = sep.join([Tool.DRIVE_ROOT_PATH,fileName])
        Tool.release(src, dst, array, isMergeRoot=False, values_map=DEVICE_OVERLAYS_VALUES_MAP)

    @classmethod
    def chgXmlvalue(cls, fileName, key, value):
        '''修改xml文件内容的键值对支持 
        例如
        key="cancel" value="hahahaha"
        <string name="cancel">hahahaha</string>
        key="wallpapers" value="<item>wallpaper1</item>\n<item>wallpaper2</item>"
        <string-array name="wallpapers" translatable="false">
            <item>wallpaper1</item>
            <item>wallpaper2</item>
        </string-array>
        :param fileName: 文件名称
        :param key: 键名称
        :param value: 值修改为的参数
        '''
        if fileName.endswith() and isfile(fileName) and key and value:
            value = value.replace('\\n','\n')
            tempFile = '.temp'
            srcFile = open(fileName, mode='r', encoding=Tool.checkFileCode(fileName))
            lines = srcFile.readlines()
            srcFile.close()
            if not lines or len(lines) == 0:
                return
            dstFile = open(tempFile, mode='w', encoding=Tool.checkFileCode(fileName))
            find_key = '([ ]*<[ ]*)([\w|-]+)(.*name[ ]*=[ ]*\"{}\"[^>]*>)(.*)'
            find_end_tag = '(.*)(<[ ]*/{}[ ]*>.*)'
            find = False
            new_line = None
            for line in lines:
                if find:
                    match = re.match(find_end_tag.format(line_tag), line)
                    if match:
                        space_len=len(match.group(1))-len(match.group(1).strip())
                        space = match.group(1)[-space_len:]
                        line_end = match.group(2)
                        new_value=space+'    '+('\n'+space+'    ').join([item.strip() for item in value.split('\n')])
                        new_line = new_line+new_value+'\n'+space+line_end+'\n'
                        find = False
                else:
                    match = re.match(find_key.format(key), line)
                    if match:
                        find = True
                        new_line = ''.join(match.groups()[0:-1])
                        line_tag = match.group(2)
                        line_content = match.groups()[-1]
                        match = re.match(find_end_tag.format(line_tag), line_content)
                        if match:
                            line_end = match.group(2)
                            new_line = new_line+value+line_end+'\n'
                            find = False
                        else:
                            new_line = new_line+'\n'
                if not find and new_line:
                    print('chgvalue change: \n' + new_line)
                    dstFile.writelines(new_line)
                    new_line = None
                elif not find:
                    dstFile.writelines(line)
            dstFile.flush()
            dstFile.close()
            os.remove(fileName)
            os.rename(tempFile, fileName)
        else:
            Tool.chgvalue(fileName, key, value)

    @classmethod
    def chgvalue(cls, fileName, key, value, equalStr=None):
        '''修改文件内容的键值对支持 key=value key:=value key==value等
        :param fileName: 文件名称
        :param key: 键名称
        :param value: 值修改为的参数
        '''
        if fileName.endswith('.xml'):
            Tool.chgXmlvalue(fileName, key, value)
        elif isfile(fileName) and key and value:
            tempFile = '.temp'
            code = Tool.checkFileCode(fileName)
            srcFile = open(fileName, mode='r', encoding=code)
            dstFile = open(tempFile, mode='w', encoding=code)
            hasLine = False
            equalStr = '' if not equalStr else equalStr
            for line in (line.strip() for line in srcFile.readlines()):
                if len(line.strip()) > 0 and not line.startswith('#'):
                    if len(equalStr) == 0:
                        equalMath = re.match(r'([\w|\.|\+]*)([ |:|=]+)(.*)', line)
                        equalStr = equalMath.group(2) if equalMath else ''

                    math = re.match('^'+ key+'[ ]*'+equalStr.strip()+'[ ]*'+'(.*)', line)
                    if math:
                        line = key + equalStr + value
                        hasLine = True
                        print('chgvalue change: '+line)

                dstFile.write(line+'\n')
            if not hasLine and len(equalStr):
                line = ''.join([key, equalStr, value])
                print('chgvalue add: '+line)
                dstFile.write(line+'\n')
            srcFile.close()
            dstFile.flush()
            dstFile.close()
            os.remove(fileName)
            os.rename(tempFile, fileName)

    @classmethod
    def addParameterToPath(cls, add = True):
        '''将编译的参数添加到环境变量方便mk文件使用'''
        call_list = list()
        call_list.append('mtk='+MTK_PROJECT)
        for key in Tool.ALL_PARAMETER:
            value = Tool.getParamter(key)
            call_list.append(key+'='+value)
            if add:
                os.environ['xhl_'+key] = value
                print('xhl_'+key+'=' + value)
        if add:
            os.environ['xhl_eng'] = 'yes' if (Tool.XHL_ENG and Tool.getParamter(COMBO)=='eng') else 'no'
            print('xhl_eng=' + os.environ['xhl_eng'])
        return call_list

    #在文件filename中查找key=value 返回value
    @classmethod
    def findValue(cls, key, filename=MTK_PROJECT_CONFIG):
        '''
        在文件filename中查找key对应的value值
        :param key: 
        :param filename: 
        :return: 返回value
        '''
        lines = popen('grep '+key+' '+filename).read().splitlines()
        if not lines or len(lines) == 0:
            return Null
        else:
            for line in lines:
                match = re.match(r''+key+'[ |=]+([\w\.\+]+)', line.strip())
                if match:
                    return match.group(1).strip()
        return Null

    @classmethod
    def getModem(cls):
        '''
        :return: 返回当前modem的名称
        '''
        lines = popen('grep CUSTOM_MODEM '+MTK_PROJECT_CONFIG).read().splitlines()
        if not lines or len(lines) == 0:
            return Null
        else:
            for line in lines:
                match = re.match(r'CUSTOM_MODEM[ |=]+([\w\.\+]+)', line.strip())
                if match:
                    return match.group(1).strip()
        return Null

    @classmethod
    def cpMode(cls, toPath):
        '''
        :param toPath: 拷贝mode到toPath目录
        :return: 
        '''
        if not isdir(toPath):
            sys.mkdirs(toPath)
        mode = Tool.getModem()
        if mode:
            comm ='cp '+Tool.MODE_FILES(mode)+' '+toPath
            print(Tool.COLOR_START + Tool.COLOR_BG1 + '34m拷贝mode '+comm + Tool.COLOR_END)
            os.system(comm)
        else:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m没有mode '+ Tool.COLOR_END)
            sys.exit(0)

    @classmethod
    def touchFiles(cls, path='', time='198705141230.31'):
        '''
        :param path: touch 的路径
        :param time: touch 的时间戳 [[CC]YY]MMDDhhmm[.SS]
        '''
        if isdir(path):
            for parent, dirnames, filenames in os.walk(path):
                for dirname in dirnames:
                    os.system('touch -t '+time+' '+sep.join([parent, dirname]))
                for filename in filenames:
                    os.system('touch -t '+time+' '+sep.join([parent, filename]))
        elif isfile(path):
            os.system('touch -t '+time+' '+path)

    @classmethod
    def touchAppModule(cls, path=''):
        '''
        :param path: 修改app编译目录里文件的时间
        '''
        getStrStype = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        module_list = Tool.findAppModule(path, isFindModule=True)
        if len(module_list)>0 :
            print('模块包含:\n\t'+getStrStype('\n\t'.join(module_list)))
            Tool.touchFiles(path, datetime.datetime.now().strftime('%Y%m%d%H%M.%S'))

    @classmethod
    def touchOutAppModule(cls, path=''):
        '''
        :param path: 修改app生成目录里文件的时间
        '''
        getStrStype = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        module_list = Tool.findAppModule(path, isFindModule=True)
        if len(module_list)>0 :
            print('模块包含:\n\t'+getStrStype('\n\t'.join(module_list)))
            for module in module_list:
                target_path = sep.join(['out', 'target', 'common', 'obj', 'APPS', module + '_intermediates'])
                if isdir(target_path):
                    Tool.touchFiles(target_path)
                target_path = sep.join(['out', 'target', 'common', 'obj', 'JAVA_LIBRARIES', module + '_intermediates'])
                if isdir(target_path):
                    Tool.touchFiles(target_path)

    @classmethod
    def findAppModule(cls, path='', delFile=False, isFindModule=False):
        '''
        查找编译目录里面的模块生成文件的路径
        :param path: 查找的路径
        :param delFile: 是否删除out目录下生成的文件
        :param isFindModule: 是否是指查找模块的名称
        :return: 
        '''
        out_module_path = list()
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        android_mk = path+'Android.mk' if path[-1]==sep else sep.join([path, 'Android.mk'])
        list_module = list()
        if len(path)>0 and isdir(path) and isfile(android_mk):
            #查找LOCAL_PACKAGE_NAME
            moduleNames = popen('cat '+android_mk+' | grep LOCAL_PACKAGE_NAME').read().splitlines()
            for moduleLine in moduleNames:
                match = re.match('LOCAL_PACKAGE_NAME[ |:|=]+([\w]+.*)', moduleLine)
                if match:
                    list_module.append(match.group(1))
            #查找LOCAL_MODULE
            moduleNames = popen('cat ' + android_mk + ' | grep LOCAL_MODULE').read().splitlines()
            for moduleLine in moduleNames:
                match = re.match('LOCAL_MODULE[ |:|=]+([\w]+.*)', moduleLine)
                if match:
                    list_module.append(match.group(1))

        if isFindModule:
            return list_module
        if delFile:
            print('\n'+Tool.COLOR_START + Tool.COLOR_BG1 + '31m' + "rebuild module contain :\n    "+ Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + ('\n    ').join(list_module) + Tool.COLOR_END)

        for module in list_module:
            #删除apk_intermediates
            target_path = sep.join(['out', 'target', 'common', 'obj', 'APPS', module+'_intermediates'])
            if isdir(target_path) and delFile:
                print_and_execute('rm -rf '+target_path)

            # 删除jar_intermediates
            target_path = sep.join(['out', 'target', 'common', 'obj', 'JAVA_LIBRARIES', module + '_intermediates'])
            if isdir(target_path) and delFile:
                print_and_execute('rm -rf ' + target_path)

            # 删除apk
            out_app_path = sep.join(['out', 'target', 'product', MTK_PROJECT, 'system', 'app'])
            if isdir(out_app_path):
                for app in [app for app in listdir(out_app_path) if app == module or ('.' in app and app[0:app.rindex('.')] == module)]:
                    target = sep.join([out_app_path, app])
                    if exists(target):
                        if delFile:
                            print_and_execute('rm -rf '+target)
                        else:
                            out_module_path.append(target)

            # 删除apk
            out_app_path = sep.join(['out', 'target', 'product', MTK_PROJECT, 'system', 'priv-app'])
            if isdir(out_app_path):
                for app in [app for app in listdir(out_app_path) if app == module or ( '.' in app and app[0:app.rindex('.')] == module)]:
                    target = sep.join([out_app_path, app])
                    if exists(target):
                        if delFile:
                            print_and_execute('rm -rf '+target)
                        else:
                            out_module_path.append(target)

            # 删除jar
            out_jar_path = sep.join(['out', 'target', 'product', MTK_PROJECT, 'system', 'framework'])
            if isdir(out_jar_path):
                for jar in [jar for jar in listdir(out_jar_path) if jar == module or ( '.' in jar and jar[0:jar.rindex('.')] == module)]:
                    target = sep.join([out_jar_path, jar])
                    if exists(target):
                        if delFile:
                            print_and_execute('rm -rf '+target)
                        else:
                            out_module_path.append(target)

        return out_module_path

    #创建安装apk文件方法
    @classmethod
    def create_install_file(cls):
        '''
        创建安装文件在windown下可执行文件bat
        '''
        install_bat = 'install.bat'
        with open(install_bat, mode='w', encoding='gbk') as install_file:
            install_file.writelines('@echo off\r\n')
            if AUTO_PUSH:
                install_file.writelines('echo 准备自动安装 %date% %time%\r\n')
                install_file.writelines('set install_apk=install_apk.bat\r\n')
                install_file.writelines('set install_apk_bak=install_apk.bak.bat\r\n')
                install_file.writelines(':CONTINUE\r\n')
                install_file.writelines('if exist %install_apk% (\r\n')
                install_file.writelines('echo 开始自动安装 %date% %time%\r\n')
                install_file.writelines('%install_apk%\r\n')
                install_file.writelines('if exist %install_apk_bak% del %install_apk_bak%\r\n')
                install_file.writelines('move %install_apk% %install_apk_bak%\r\n')
                install_file.writelines('install.bat\r\n')
                install_file.writelines(')\r\n')
                install_file.writelines('@ping /n 1 /w 1000 1.1.1.1 >null\r\n')
                install_file.writelines('goto CONTINUE\r\n')
            else:
                install_file.writelines('set install_apk=install_apk.bat\r\n')
                install_file.writelines('if exist install_apk.bat (\r\n')
                install_file.writelines('echo 开始安装 %date% %time%\r\n')
                install_file.writelines('install_apk.bat\r\n')
                install_file.writelines('pause\r\n')
                install_file.writelines('install.bat\r\n')
                install_file.writelines(')\r\n')
                install_file.writelines('pause\r\n')
                install_file.writelines('install.bat\r\n')
            install_file.flush()
            install_file.close()
            os.chmod(install_bat, 0o0777)

    # 获取AndroidManifest.xml启动的intent
    @classmethod
    def getIntent(cls, input_line=''):
        import xml.dom.minidom as xmldom
        ACTION_MAIN = 'android.intent.action.MAIN'
        CATEGORY_LAUNCHER = 'android.intent.category.LAUNCHER'
        filters = list()
        if isfile(input_line):
            domObj = xmldom.parse(input_line)
        else:
            domObj = xmldom.parseString(input_line)
        if not domObj:
            return
        element = domObj.documentElement
        package = element.getAttribute('package')
        filters.append(package)
        if package:
            activitys = element.getElementsByTagName('activity')
            for activity in activitys:
                name = activity.getAttribute('android:name')
                if name:
                    for filter in activity.getElementsByTagName('intent-filter'):
                        actions = [action for action in filter.getElementsByTagName('action') if action.getAttribute('android:name') == ACTION_MAIN]
                        categorys = [category for category in filter.getElementsByTagName('category') if category.getAttribute('android:name') == CATEGORY_LAUNCHER]
                        if len(actions)>0  and len(categorys)>0:
                            filters.append(name)
        intents = list()
        if len(filters)>0:
            intents.append('echo kill proess {}'.format(filters[0]))
            intents.append('adb shell am force-stop {}'.format(filters[0]))
        if len(filters)>1:
            if filters[0].split('.')[0] !=  filters[1].split('.')[0]:
                filters[1] = (filters[0]+filters[1]) if filters[1].startswith('.') else (filters[0]+'.'+filters[1])
            intents.append('echo start app {}'.format(filters[1]))
            intents.append('adb shell am start -a {main} -n {package}/{name}'.format(main=ACTION_MAIN, package=filters[0], name=filters[1]))
            intents.append('rem echo clear app {}'.format(filters[1]))
            intents.append('rem adb shell pm clear {}'.format(filters[0]))
        return intents

    #创建安装app文件方法
    @classmethod
    def create_install_apk_file(cls, make_log_file = 'mm.log'):
        '''
        根据编译的log文件创建adb install的bat安装app文件
        :param make_log_file: 
        :return: 
        '''
        if isfile(make_log_file):
            out_module_paths = list()
            #Install: out/target/product/mbk72_wet_lca/system/app/SystemUI.apk
            with open(make_log_file, encoding=Tool.checkFileCode(make_log_file)) as log_file:
                for line in [ line for line in log_file.readlines() if line.startswith('Install: out/target/product') or line.startswith('Copy: out/target/product')]:
                    out_module_paths.append(line.strip().split(' ')[1])

            install_apk_bat = 'install_apk.bat'
            with open(install_apk_bat, mode='w') as install_file:
                install_file.writelines('adb remount\r\n')
                apk_file = None
                for line in out_module_paths:
                    window_path = line.replace(sep, '\\')
                    if line.endswith('.apk'):
                        apk_file = line
                    if 'system' in line:
                        android_path = line[line.rindex('system'):]
                    elif 'data' in line:
                        android_path = line[line.rindex('data'):]
                    else :
                        android_path = '/system/app/'
                    line = 'adb push {} {}\r\n'.format(window_path, android_path)
                    install_file.writelines(line)
                AndroidManifest = sep.join([Tool.mm_path,'AndroidManifest.xml'])
                if Tool.mm_path and isfile(AndroidManifest):
                    intents = Tool.getIntent(AndroidManifest)
                    install_file.writelines('\r\n'.join(intents))
                elif apk_file and zipfile.is_zipfile(apk_file):
                    AXMLPrinter = sep.join([dirname(abspath(__file__)), 'apktool', 'lib', 'AXMLPrinter2.jar'])
                    data = zipfile.ZipFile(apk_file, mode='r').open('AndroidManifest.xml').read()
                    open('.temp', mode='wb').write(data)
                    intents = Tool.getIntent(popen('java -jar '+AXMLPrinter+' '+'.temp').read())
                    remove('.temp')
                    install_file.writelines('\r\n'.join(intents))
                install_file.flush()
                install_file.close()
                os.chmod(install_apk_bat, 0o0777)

    @classmethod
    def mm(cls, argv=list(), touchOut=True, keepOut=True, cleanModule=False):
        '''
        编译项目或者模块
        :param argv: 编译的参数
        :param touchOut: 是否修改生成文件的时间，如果为False就修改编译目录里的文件的时间
        :param keepOut: make项目时候是否执行make-clean
        '''
        parameterStr = ''
        isNew = True if (argv and len(argv) > 0 and argv[0] == 'new') else False

        #如果是android5.0以后版本编译参数不需要new
        if isNew and not Tool.BEFORE_LOLLIPOP:
            del argv[0]

        if argv and len(argv) > 1 and argv[0] == 'mm':
            module_path = Tool.getMmPath(argv[1], is_mm=True)
            Tool.mm_path = argv[1]
            if module_path and isdir(module_path):
                argv[1] = module_path
            if not isdir(argv[1]):
                print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m没有找到编译模块:'+ argv[1] + Tool.COLOR_END)
                sys.exit(0)

        print('mm( argv=', argv, 'touchOut=',str(touchOut),'keepOut=',str(keepOut),'cleanModule=',str(cleanModule),')')
        if argv:
            parameterStr = ' '.join(argv)
        if not Tool.readParameters(Tool.INI_FILE) and not Tool.readParameters(Tool.INI_FILE_OLD):
            if isfile(Tool.INI_FILE):
                os.remove(Tool.INI_FILE)
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m警告 没有找到配置文件'+Tool.INI_FILE+Tool.COLOR_END)
            Tool.setParameters()

        if isNew:
            #根据语言定制
            if Tool.BEFORE_LOLLIPOP:
                mLanguage = Tool.getParamter(LANGUAGE)
                if mLanguage == 'foreign':
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'DEFAULT_INPUT_METHOD', 'com.android.inputmethod.latin.LatinIME')
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_INPUTMETHOD_PINYINIME_APP', 'no')
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_PRODUCT_LOCALES', 'af_ZA am_ET ar_EG bg_BG ca_ES cs_CZ da_DK de_DE el_GR en_GB en_US es_ES es_US fa_IR fi_FI fr_FR hi_IN hr_HR hu_HU in_ID it_IT iw_IL km_KH ko_KR lo_LA lt_LT lv_LV ms_MY my_MM nb_NO nl_NL pl_PL pt_BR pt_PT rm_CH ro_RO ru_RU sk_SK sl_SI sr_RS sv_SE sw_TZ th_TH tl_PH tr_TR uk_UA vi_VN zu_ZA')
                elif mLanguage == 'huayu':
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'DEFAULT_INPUT_METHOD', 'com.android.inputmethod.latin.LatinIME')
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_INPUTMETHOD_PINYINIME_APP', 'yes')
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_PRODUCT_LOCALES','af_ZA am_ET ar_EG bg_BG ca_ES cs_CZ da_DK de_DE el_GR en_GB en_US es_ES es_US fa_IR fi_FI fr_FR hi_IN hr_HR hu_HU in_ID it_IT iw_IL km_KH ko_KR lo_LA lt_LT lv_LV ms_MY my_MM nb_NO nl_NL pl_PL pt_BR pt_PT rm_CH ro_RO ru_RU sk_SK sl_SI sr_RS sv_SE sw_TZ th_TH tl_PH tr_TR uk_UA vi_VN zu_ZA')
                elif mLanguage == 'chinese':
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'DEFAULT_INPUT_METHOD', 'com.android.inputmethod.pinyin.PinyinIME')
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_INPUTMETHOD_PINYINIME_APP', 'yes')
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_PRODUCT_LOCALES', 'en_US zh_CN')
            else:
                mLanguage = Tool.getParamter(LANGUAGE)
                if mLanguage == 'foreign':
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_PRODUCT_LOCALES', 'af_ZA am_ET ar_EG bg_BG ca_ES cs_CZ da_DK de_DE el_GR en_GB en_US es_ES es_US fa_IR fi_FI fr_FR hi_IN hr_HR hu_HU in_ID it_IT iw_IL km_KH ko_KR lo_LA lt_LT lv_LV ms_MY my_MM nb_NO nl_NL pl_PL pt_BR pt_PT rm_CH ro_RO ru_RU sk_SK sl_SI sr_RS sv_SE sw_TZ th_TH tl_PH tr_TR uk_UA vi_VN zu_ZA')
                elif mLanguage == 'huayu':
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_PRODUCT_LOCALES','af_ZA am_ET ar_EG bg_BG ca_ES cs_CZ da_DK de_DE el_GR en_GB en_US es_ES es_US fa_IR fi_FI fr_FR hi_IN hr_HR hu_HU in_ID it_IT iw_IL km_KH ko_KR lo_LA lt_LT lv_LV ms_MY my_MM nb_NO nl_NL pl_PL pt_BR pt_PT rm_CH ro_RO ru_RU sk_SK sl_SI sr_RS sv_SE sw_TZ th_TH tl_PH tr_TR uk_UA vi_VN zu_ZA zh_CN zh_TW')
                elif mLanguage == 'chinese':
                    Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_PRODUCT_LOCALES', 'en_US zh_CN')
            if not Tool.BEFORE_LOLLIPOP:
                Tool.chgvalue(MTK_PROJECT_CONFIG, 'MTK_BUILD_ROOT', Tool.MTK_BUILD_ROOT)

            #修改变量
            for fileName,valueMap in DEVICE_OVERLAYS_VALUES_MAP.items():
                for key,value in valueMap.items():
                    Tool.chgvalue(DEVICE_OVERLAYS_FILE_MAP[fileName], key, value)

            #大陈工用几个变量
            Tool.chgvalue(MTK_LK_CONFIG, 'BOOT_LOGO', Tool.findValue('BOOT_LOGO'))


        #将参数添加到环境变量并回调驱动脚本
        parameterArray = Tool.addParameterToPath()
        parameterArray.append('config='+MTK_PROJECT_CONFIG)
        if isfile(Tool.DRIVER_CALL):
            os.system(Tool.DRIVER_CALL+' '+' '.join(parameterArray))
        #回调NEW脚本
        if isfile(Tool.NEW_CALL):
            os.system(Tool.NEW_CALL+' '+' '.join(parameterArray))

        if not Tool.getModem():
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m没有mode ' + Tool.COLOR_END)
            sys.exit(0)

        mCombo = Tool.getParamter(COMBO)

        #mm模块的时候删除以前生存的模块
        if argv and len(argv) > 1 and argv[0] == 'mm':
            Tool.create_install_file()
            if touchOut:
                Tool.touchOutAppModule(path=argv[1])
            else:
                Tool.touchAppModule(path=argv[1])

        #如果是android5.0之前老版本
        if Tool.BEFORE_LOLLIPOP:
            if mCombo == 'eng':
                comm = './mk ' + MTK_PROJECT + ' ' + parameterStr + (' | tee make.log 2>&1' if len(argv) > 0 and argv[0] == 'new' else '')
            elif mCombo == 'emulator':
                comm = './mk ' + MTK_BANYAN_ADDON + ' ' + parameterStr + (' | tee make.log 2>&1' if len(argv) > 0 and argv[0] == 'new' else '')
            else:
                comm = './mk -o=TARGET_BUILD_VARIANT=user ' + MTK_PROJECT + ' ' + parameterStr + (' | tee make.log 2>&1' if len(argv) > 0 and argv[0] == 'new' else '')

            print(comm)
            os.system(comm)
            if argv and len(argv) > 1 and argv[0] == 'mm':
                log_file = sep.join(['out', 'target', 'product', MTK_PROJECT + '_mm.log'])
                Tool.create_install_apk_file(log_file)
                sys.exit(0)
            elif parameterStr.strip() == 'new' and not Tool.isSuccessfully() :
                print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m未检测到编译成功，' + Tool.COLOR_START + Tool.COLOR_END)
                sys.exit(0)
            else:
                Tool.mAutoBuild = True
        else:#android5.0之后版本
            comm_file = open('comm.sh', mode='w')
            comm_file.write('#!/bin/bash \n')
            comm_file.write('source ./build/envsetup.sh \n')

            if mCombo == 'eng':
                comm_file.write('lunch ' + FULL_MTK_PROJECT_ENG + ' \n')
            elif mCombo == 'emulator':
                comm_file.write('lunch ' + MTK_BANYAN_ADDON + ' \n')
            else:
                comm_file.write('lunch ' + FULL_MTK_PROJECT_USER + ' \n')
            if argv and len(argv) > 1 and argv[0] == 'mm':
                if cleanModule:
                    module_list = Tool.findAppModule(path=argv[1], isFindModule=True)
                    if len(module_list)>0:
                        comm = ';'.join(['make clean-'+module for module in module_list])
                        print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m' + comm + Tool.COLOR_END)
                        comm_file.write(comm+' \n')

                if argv[1] == 'packages/apps/Gallery2':
                    comm = 'mmma '+argv[1]+' 2>&1 | tee '+Tool.MM_LOG
                else:
                    comm = 'mmm '+argv[1]+' 2>&1 | tee '+Tool.MM_LOG
                print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m' + comm + Tool.COLOR_END)
                comm_file.write(comm+' \n')
                comm_file.close()

                os.system('chmod 777 comm.sh')
                os.system('cat ./comm.sh')
                os.system('./comm.sh')
                os.system('rm comm.sh')
                if isfile('./remoteadb.sh'):
                    os.system('./remoteadb.sh')
                Tool.create_install_apk_file(Tool.MM_LOG)
                sys.exit(0)
            else:
                successfully = popen('tail -n 2 ' + Tool.MAKE_LOG + ' | grep successfully | wc -l').read().splitlines()[0] if isfile(Tool.MAKE_LOG) else '0'
                #当上次成功编译且这次为编译用户版时候自动删除out目录，eng版需要工程师手动删除
                if isNew and not keepOut:
                    comm = 'rm -rf out'
                    print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m' + comm+ Tool.COLOR_END)
                    comm_file.write(comm+' \n')
                elif isNew :#or len(parameterStr):
                    #rm -rf out/target/product/zechin6580_weg_m/data/* \
                    # out/target/product/zechin6580_weg_m/data-qemu/* \
                    # out/target/product/zechin6580_weg_m/userdata-qemu.img \
                    # out/host/linux-x86/obj/NOTICE_FILES out/host/linux-x86/sdk \
                    # out/target/product/zechin6580_weg_m/*.img \
                    # out/target/product/zechin6580_weg_m/*.ini \
                    # out/target/product/zechin6580_weg_m/*.txt \
                    # out/target/product/zechin6580_weg_m/*.xlb \
                    # out/target/product/zechin6580_weg_m/*.zip \
                    # out/target/product/zechin6580_weg_m/kernel \
                    # out/target/product/zechin6580_weg_m/data \
                    # out/target/product/zechin6580_weg_m/skin \
                    # out/target/product/zechin6580_weg_m/obj/APPS \
                    # out/target/product/zechin6580_weg_m/obj/NOTICE_FILES \
                    # out/target/product/zechin6580_weg_m/obj/PACKAGING \
                    # out/target/product/zechin6580_weg_m/recovery \
                    # out/target/product/zechin6580_weg_m/root \
                    # out/target/product/zechin6580_weg_m/system \
                    # out/target/product/zechin6580_weg_m/vendor \
                    # out/target/product/zechin6580_weg_m/oem \
                    # out/target/product/zechin6580_weg_m/dex_bootjars \
                    # out/target/product/zechin6580_weg_m/obj/JAVA_LIBRARIES \
                    # out/target/product/zechin6580_weg_m/obj/FAKE \
                    # out/target/product/zechin6580_weg_m/obj/EXECUTABLES/adbd_intermediates \
                    # out/target/product/zechin6580_weg_m/obj/STATIC_LIBRARIES/libfs_mgr_intermediates \
                    # out/target/product/zechin6580_weg_m/obj/EXECUTABLES/init_intermediates \
                    # out/target/product/zechin6580_weg_m/obj/ETC/mac_permissions.xml_intermediates \
                    # out/target/product/zechin6580_weg_m/obj/ETC/sepolicy_intermediates \
                    # out/target/product/zechin6580_weg_m/obj/ETC/init.environ.rc_intermediates
                    comm = 'mv '+Tool.MT6580_Android_scatter+' '+Tool.MT6580_Android_scatter+'.bak'
                    comm_file.write(comm+' \n')
                    comm = 'make installclean'
                    print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m' + comm+ Tool.COLOR_END)
                    comm_file.write(comm+' \n')
                    comm = 'mv '+Tool.MT6580_Android_scatter+'.bak'+' '+Tool.MT6580_Android_scatter
                    comm_file.write(comm+' \n')
                comm = 'make -j'+Tool.getJob()+' '+parameterStr+' 2>&1 | tee '+Tool.MAKE_LOG
                print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m' + comm+ Tool.COLOR_END)
                comm_file.write(comm+' \n')
                comm_file.close()
                os.system('chmod 777 comm.sh')
                os.system('cat ./comm.sh')
                os.system('./comm.sh')
                os.system('rm comm.sh')
                if not Tool.isSuccessfully():
                    print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m未检测到编译成功，' + Tool.COLOR_START + Tool.COLOR_END)
                    exit(0)
                else:
                    Tool.mAutoBuild = True

    @classmethod
    def isSuccessfully(cls, log_file = sep.join(['out', 'target', 'product', MTK_PROJECT + '_android.log'])):
        successfully = False
        if isfile(log_file) and (popen('tail -n 1 ' + log_file + ' | grep "Checking memory usage DONE" | wc -l').read().splitlines()[0] == '1'):
            successfully = True
        if not successfully and isfile(Tool.MAKE_LOG) and (
            popen('tail -n 2 ' + Tool.MAKE_LOG + ' | grep successfully | wc -l').read().splitlines()[0] == '1'):
            successfully = True
        return successfully

    @classmethod
    def zipIcons(cls, icons_path=None):
        if not isdir(icons_path): return
        print('zipIcons path == {}'.format(icons_path))
        for item in listdir(icons_path):
            child_file = sep.join([icons_path, item])
            if isdir(child_file):
                print('icons --> {}'.format(child_file))
                Tool.zipIcons(child_file)

        zip_file = icons_path+'.zip'
        print('zip_file ===== {}'.format(zip_file))
        zipped=zipfile.ZipFile(zip_file, mode='w')
        for icon_name in listdir(icons_path):
            child_file = sep.join([icons_path, icon_name])
            print('write ===== {}'.format(child_file))
            zipped.write(child_file, icon_name)
            print('zipped({})'.format(icon_name))
        zipped.close()
        print('rmtree({})'.format(icons_path))
        rmtree(icons_path)
        rename(zip_file, icons_path)
        os.chmod(icons_path, 0o0777)

    @classmethod
    def zipIconPath(cls, icons_path=None):
        if not isdir(icons_path): return
        for filePath in [ sep.join([icons_path,item]) for item in listdir(icons_path)]:
            if isdir(filePath):
                Tool.zipIcons(filePath)

    @classmethod
    def buildimage(cls, argv=None):
        '''
        打包out下的system和data，会整合xhl/merge的文件到xhl/out目录下 然后生成system.img和data.img
        :param argv: 打包的参数，如果没有参数会感觉以前编译的参数打包，如果没有以前的参数就根据用户选择打包
        '''
        #./buildimage project screen hardware language flash network customer"
        #.BuildPath=Bin.Project.Screen.Hardware.Language.Flash.Network.Customer
        out_bin=sep.join(['.', 'out', 'host', 'linux-x86','bin'])
        os.environ['PATH']=out_bin+':'+os.environ['PATH']
        sys.path.append(out_bin)
        if isdir(Tool.PRODUCT_DATA) and isdir(Tool.PRODUCT_SYSTEM):
            if argv and len(argv) > 1:
                print('buildimage argv=', str(argv))
                parameters = list()
                parameters.append(argv[0] if len(argv) >=1 else PROJECT)
                parameters.append(argv[1] if len(argv) >=2 else SCREEN)
                parameters.append(argv[2] if len(argv) >=3 else HARDWARE)
                parameters.append(argv[3] if len(argv) >=4 else LANGUAGE)
                parameters.append(argv[4] if len(argv) >=5 else FLASH)
                parameters.append(argv[5] if len(argv) >=6 else NETWORK)
                parameters.append(argv[6] if len(argv) >=7 else CUSTOMER)
                parameters.append(argv[7] if len(argv) >=8 else BATTERY)
                parameters.append(argv[8] if len(argv) >=9 else COMBO)
                BuildPath = 'Bin.'+'.'.join(argv)
            else:
                if not Tool.mAutoBuild and not Tool.readParameters(Tool.INI_FILE) and not Tool.readParameters(Tool.INI_FILE_OLD):
                    Tool.setParameters(saveToFile=False, readFile=Tool.INI_FILE)
                parameters = list()
                for parameter in Tool.ALL_PARAMETER:
                    value = Tool.getParamter(parameter)
                    if parameter != value:
                        parameters.append(value)
                BuildPath = 'Bin.'+'.'.join(parameters)

            if Tool.mAutoBuild:
                if not Tool.isSuccessfully():
                    log_file = sep.join(['out', 'target', 'product', MTK_PROJECT + '_android.log'])
                    printText = Tool.COLOR_START + Tool.COLOR_BG2 + '30m未在文件' + (log_file if isfile(log_file) else Tool.MAKE_LOG) + '检测到编译成功，' + Tool.COLOR_START + '31m所以不能完成打包！' + Tool.COLOR_START + Tool.COLOR_END + '\n'
                    print(printText)
                    sys.exit(0)
                printText = Tool.COLOR_START + Tool.COLOR_BG2 + '30m生成打包' + Tool.COLOR_START + '31m ' + BuildPath + Tool.COLOR_START + Tool.COLOR_END + '\n'
                print(printText)
            else:
                printText = Tool.COLOR_START + Tool.COLOR_BG2 + '30m即将生成打包' + Tool.COLOR_START + '31m ' + BuildPath + Tool.COLOR_START + '30m 确定请按y/Y或者直接回车，取消按n/N然后回车?' + Tool.COLOR_END + '\n'
                choiceText = input(printText).strip()
                if not (choiceText is 'y' or choiceText is 'Y' or choiceText is ''):
                    Tool.setParameters(saveToFile=False, readFile=Tool.INI_FILE, dialog = True)
                    parameters = list()
                    for parameter in Tool.ALL_PARAMETER:
                        value = Tool.getParamter(parameter)
                        if parameter != value:
                            parameters.append(value)
                    BuildPath = 'Bin.' + '.'.join(parameters)
                    printText = Tool.COLOR_START + Tool.COLOR_BG2 + '30m即将生成打包' + Tool.COLOR_START + '31m ' + BuildPath + Tool.COLOR_START + '30m 确定请按y/Y或者直接回车，取消按n/N然后回车?' + Tool.COLOR_END + '\n'
                    choiceText = input(printText).strip()
                    if not (choiceText is 'y' or choiceText is 'Y' or choiceText is ''):
                        sys.exit(0)

            mProject = Tool.getParamter(PROJECT)
            mScreen = Tool.getParamter(SCREEN)
            mFlash = Tool.getParamter(FLASH)
            mLanguage = Tool.getParamter(LANGUAGE)
            mNetwork = Tool.getParamter(NETWORK)
            mCustomer = Tool.getParamter(CUSTOMER)

            #拷贝system和out目录
            if isdir(Tool.XHL_OUT):
                print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m清理xhl下的out目录 。。。' + Tool.COLOR_END)
                os.system('rm -rf ' + Tool.XHL_OUT)
            os.makedirs(Tool.XHL_OUT)

            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m拷贝out下的data目录 。。。' + Tool.COLOR_END)
            os.system('cp -R '+Tool.PRODUCT_DATA+' '+Tool.XHL_OUT)

            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m拷贝out下的system目录 。。。' + Tool.COLOR_END)
            os.system('cp -R '+Tool.PRODUCT_SYSTEM+' '+Tool.XHL_OUT)

            #覆盖打包文件
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m拷贝xhl下的merge目录 。。。' + Tool.COLOR_END)
            # 定制build.prop顺序
            # 1. xhl/merge/common/build.prop
            # 2. xhl/merge/common/xx.xx.xx.xx/build.prop
            # 3. xhl/merge/project_screen/build.prop
            # 4. xhl/merge/project_screen/common/build.prop
            # 5. xhl/merge/project_screen/xx.xx.xx.xx/build.prop

            #定制 xhl/merge/common/build.prop
            dst = Tool.XHL_OUT
            array = list()

            #定制 xhl/merge/xxx.xxx.xxx.xxx/build.prop
            for parameter in Tool.MERGE_PARAMETER[2:]:
                array.append([parameter, Tool.getParamter(parameter)])
            src = sep.join([Tool.MERGE_ROOT_PATH, ])
            Tool.release(src, dst, array,isMergeRoot=True, values_map=MERGE_OVERLAYS_VALUES_MAP)

            #定制 xhl/merge/project_creen/xxx.xxx.xxx.xxx/build.prop
            src = sep.join([Tool.MERGE_ROOT_PATH, '_'.join([Tool.getParamter(PROJECT), Tool.getParamter(SCREEN)])])
            Tool.release(src, dst, array,isMergeRoot=False, values_map=MERGE_OVERLAYS_VALUES_MAP)
            #删除xhl/out里多余的文件
            if isfile(sep.join([Tool.XHL_OUT, 'boot_build.prop'])):
                os.system('rm '+sep.join([Tool.XHL_OUT, 'boot_build.prop']))
            #定制 xhl/merge/project_screen/build.prop
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m修改build.prop 。。。' + Tool.COLOR_END)
            mBuildProp = sep.join([Tool.OUT_SYSTEM,BUILD_PROP])
            Tool.chgvalue(mBuildProp, 'ro.feature.project', mProject)
            Tool.chgvalue(mBuildProp, 'ro.feature.project_all', mProject+'_'+mScreen+'_'+mFlash+'_'+mLanguage+'_'+mNetwork)
            Tool.chgvalue(mBuildProp, 'ro.build.year', datetime.datetime.now().strftime('%Y'))
            Tool.chgvalue(mBuildProp, 'ro.build.month', datetime.datetime.now().strftime('%m'))
            Tool.chgvalue(mBuildProp, 'ro.build.day', datetime.datetime.now().strftime('%d'))
            Tool.chgvalue(mBuildProp, 'ro.xhl.lcd_width', Tool.findValue('LCM_WIDTH'))
            Tool.chgvalue(mBuildProp, 'ro.xhl.lcd_height', Tool.findValue('LCM_HEIGHT'))
            if mLanguage == 'chinese':
                Tool.chgvalue(mBuildProp, 'ro.product.locale', 'zh-CN')
                Tool.chgvalue(mBuildProp, 'ro.product.locale.region', 'CN')
                Tool.chgvalue(mBuildProp, 'ro.product.locale.language', 'zh')
            else:
                Tool.chgvalue(mBuildProp, 'ro.product.locale', 'en-US')
                Tool.chgvalue(mBuildProp, 'ro.product.locale.region', 'US')
                Tool.chgvalue(mBuildProp, 'ro.product.locale.language', 'en')

            #修改对应文件的key=value
            for fileName, valueMap in MERGE_OVERLAYS_VALUES_MAP.items():
                for key, value in valueMap.items():
                    Tool.chgvalue(MERGE_OVERLAYS_FILE_MAP[fileName], key, value)
            #build时间
            Tool.chgvalue(mBuildProp, 'ro.build.date', popen('date').read().splitlines()[0])
            Tool.chgvalue(mBuildProp, 'ro.build.date.utc', popen('date +%s').read().splitlines()[0])
            #将icon压缩到zip中
            Tool.zipIconPath(icons_path=ICONS_PATCH)
            # 将参数添加到环境变量并回调驱动脚本
            MERGE_PAR_Array = Tool.addParameterToPath(add = False)
            MERGE_PAR_Array.append('config=' + MTK_PROJECT_CONFIG)
            if isfile(Tool.MERGE_CALL):
                os.system(Tool.MERGE_CALL + ' ' + ' '.join(MERGE_PAR_Array))

            #定制xhl/merge/project_creen/expand_customer.prop
            Tool.selectCustomer(layerName='.'.join([mScreen, mFlash, mLanguage, mNetwork, mCustomer]))
            if isfile('xhl/out/expand_customer.prop'):
                remove('xhl/out/expand_customer.prop')
            print_and_execute = lambda comm_line : not print(comm_line) and os.system(comm_line)

            outPath=sep.join(['out', 'target', 'product', MTK_PROJECT])
            outSystemImage = sep.join([outPath, 'system.img'])
            outDataImage = sep.join([outPath, 'userdata.img'])
            log_file = sep.join(['out', 'target', 'product', MTK_PROJECT + '_android.log'])
            if not isfile(log_file):
                log_file = Tool.MAKE_LOG
            #MTK_COMBO_NAND_SUPPORT=no|yes
            nand_support = Tool.findValue('MTK_COMBO_NAND_SUPPORT')
            if mFlash.startswith('mcp_nand') or nand_support=='yes':
                mkuserimgDict = Tool.getMakeUbifImageDict(log_file)
                if 'system' in mkuserimgDict:
                    comm_system_mkfs_ubifs = mkuserimgDict['system']
                else:
                    comm_system_mkfs_ubifs = 'mkfs_ubifs -F -r '+Tool.OUT_SYSTEM+' -o '+outPath+'/ubifs.android.img -m 4096 -e 253952 -c 1093 -v'
                print_and_execute(comm_system_mkfs_ubifs)

                if 'system.img' in mkuserimgDict:
                    comm_system_ubinize = mkuserimgDict['system.img']
                else:
                    comm_system_ubinize = 'ubinize -o '+outSystemImage+' -m 4096 -p 262144 -O 4096 -v '+outPath+'/ubi_android.ini'
                print_and_execute(comm_system_ubinize)

                if 'data' in mkuserimgDict:
                    comm_data_mkfs_ubifs = mkuserimgDict['data']
                else:
                    comm_data_mkfs_ubifs = 'mkfs_ubifs -F -r '+Tool.OUT_DATA+' -o '+outPath+'/ubifs.usrdata.img -m 4096 -e 253952 -c 896 -v'
                print_and_execute(comm_data_mkfs_ubifs)

                if 'userdata.img' in mkuserimgDict:
                    comm_data_ubinize = mkuserimgDict['userdata.img']
                else:
                    comm_data_ubinize = 'ubinize -o '+outDataImage+' -m 4096 -p 262144 -O 4096 -v '+outPath+'/ubi_usrdata.ini'
                print_and_execute(comm_data_ubinize)

            elif mFlash.startswith('emmc')  or nand_support=='no':#根据make.log获取打包文件大小来打包
                mkuserimgDict = Tool.getMakeEmmcImageDict(log_file)
                if 'system' in mkuserimgDict:
                    comm_system_mkuserimg = mkuserimgDict['system']
                else:
                    comm_system_mkuserimg = 'mkuserimg.sh -s ' + Tool.OUT_SYSTEM + ' ' + outSystemImage+' ext4 system 1178599424 ' + outPath + '/root/file_contexts'
                print_and_execute(comm_system_mkuserimg)

                if 'data' in mkuserimgDict:
                    comm_data_mkuserimg = mkuserimgDict['data']
                else:
                    comm_data_mkuserimg = 'mkuserimg.sh -s ' + Tool.OUT_DATA + ' ' + outDataImage+' ext4 data 1400897536 ' + outPath + '/root/file_contexts'
                print_and_execute(comm_data_mkuserimg)

            outSigner = sep.join([out_bin, 'verity_signer'])
            if isfile(outSigner):
                dev_system='/dev/block/platform/mtk-msdc.0/11230000.msdc0/by-name/system'
                outVerityImage = sep.join([outPath, 'verity.img'])
                outVerityMetadataImage = sep.join([outPath, 'verity_metadata.img'])
                buildPk8 = sep.join(['build', 'target','product','security','verity.pk8'])
                VERIFY_VALUE=popen(' '.join(['build_verity_tree','-A', 'aee087a5be3b982978c923f566a94613496b417f2af592639bc80d141e34dfe7', outSystemImage, outVerityImage])).read().strip()
                print(VERIFY_VALUE)
                system_size=mkuserimgDict['system_size'] if 'system_size' in mkuserimgDict else '1178599424'
                VERIFY_PARAM=' '.join([system_size, outVerityMetadataImage,VERIFY_VALUE,dev_system,outSigner,buildPk8])
                build_verity_metadata=sep.join(['system','extras','verity','build_verity_metadata.py'])
                comm = ' '.join([build_verity_metadata, VERIFY_PARAM])
                print_and_execute(comm)
                comm = ' '.join(['append2simg', outSystemImage, outVerityMetadataImage])
                print_and_execute(comm)
                comm = ' '.join(['append2simg', outSystemImage, outVerityImage])
                print_and_execute(comm)
                remove(outVerityMetadataImage)
                remove(outVerityImage)
            if isdir(BuildPath):
                rmtree(BuildPath)
            os.makedirs(BuildPath)

            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m最后拷贝bin目录 。。。' + Tool.COLOR_END)

            comm_line = 'cp '+sep.join([outPath, '*'])+' '+BuildPath
            print_and_execute(comm_line)

            if Tool.BEFORE_LOLLIPOP:
                comm_line = 'cp '+sep.join(['mediatek', 'cgen', 'APDB2_MT6572_S01_MAIN2.1_W10.24'])+' '+BuildPath
                print_and_execute(comm_line)

                comm_line = 'cp '+sep.join(['mediatek', 'cgen', 'APDB_MT6572_S01_MAIN2.1_W10.24'])+' '+BuildPath
                print_and_execute(comm_line)
            else:
                comm_line = 'cp '+sep.join([outPath, 'obj', 'CGEN', 'APDB_*'])+' '+BuildPath
                print_and_execute(comm_line)
            #出问题可以dump内核
            vmlinux = sep.join([outPath, 'obj', 'KERNEL_OBJ', 'vmlinux'])
            if isfile(vmlinux):
                comm_line = 'tar -zcvf '+sep.join([BuildPath,'vmlinux.tar.gz'])+' '+vmlinux
                print_and_execute(comm_line)

            Tool.cpMode(BuildPath)

            comm_line = 'rm -rf '+sep.join([BuildPath, 'ubi*'])
            print_and_execute(comm_line)

            comm_line = 'chmod a+rw '+sep.join([BuildPath, '*'])
            print_and_execute(comm_line)

            comm_line = 'cp '+sep.join([Tool.XHL_OUT, '*'])+' '+BuildPath
            print_and_execute(comm_line)

            # 如果是android5.0之前老版本
            comm_line = 'cp  -r '+sep.join([Tool.XHL_PATH, 'script', 'checksum', 'v10' if mFlash.startswith('mcp_nand')  or nand_support=='yes' else 'v11', '*'])+' '+BuildPath
            print_and_execute(comm_line)

            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + 'Finish build '+Tool.COLOR_START + '31m' + BuildPath + Tool.COLOR_END)
        else:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + Tool.COLOR_START + '31m请先编译项目' + Tool.COLOR_END )

    @classmethod
    def getMakeUbifImageDict(cls, file=MAKE_LOG):
        '''
        根据make的log文件获取打包ubif的参数
        :param file: log文件的路径
        '''
        mkuserimgDict = dict()
        if isfile(file):
            log_file = open(file, mode='r', encoding=Tool.checkFileCode(file))
            for line in log_file.readlines():
                # 'out/host/linux-x86/bin/mkfs_ubifs -F -r out/target/product/mbk72_wet_lca/data -o out/target/product/mbk72_wet_lca/ubifs.usrdata.img -m 4096 -e 253952 -c 874 -v'
                # 'out/host/linux-x86/bin/ubinize -o out/target/product/mbk72_wet_lca/userdata.img -m 4096 -p 262144 -O 4096 -v out/target/product/mbk72_wet_lca/ubi_usrdata.ini'
                # 'out/host/linux-x86/bin/mkfs_ubifs -F -r out/target/product/mbk72_wet_lca/system -o out/target/product/mbk72_wet_lca/ubifs.android.img -m 4096 -e 253952 -c 1058 -v'
                # 'out/host/linux-x86/bin/ubinize -o out/target/product/mbk72_wet_lca/obj/PACKAGING/systemimage_intermediates/system.img -m 4096 -p 262144 -O 4096 -v out/target/product/mbk72_wet_lca/ubi_android.ini'
                match = re.match(r'^([^ ]+mkfs_ubifs -F -r )([^ ]+)( .+)$', line.strip())
                if not match:
                    match = re.match(r'^([^ ]+ubinize -o )([^ ]+)( .+)$', line.strip())
                if match:
                    START_OTHER = match.group(1)
                    PACKAGE_PATH = match.group(2)
                    END_OTHER = match.group(3)
                    MOUNT_POINT = PACKAGE_PATH.strip().split(sep)[-1]
                    outPath = sep.join(['out', 'target', 'product', MTK_PROJECT])
                    if MOUNT_POINT == 'data':
                        mkuserimgDict['data'] = START_OTHER + Tool.OUT_DATA + END_OTHER
                    elif MOUNT_POINT == 'userdata.img':
                        outDataImage = sep.join([outPath, 'userdata.img'])
                        mkuserimgDict['userdata.img'] = START_OTHER + outDataImage + END_OTHER
                    elif MOUNT_POINT == 'system':
                        mkuserimgDict['system'] = START_OTHER + Tool.OUT_SYSTEM + END_OTHER
                    elif MOUNT_POINT == 'system.img':
                        outSystemImage = sep.join([outPath, 'system.img'])
                        mkuserimgDict['system.img'] = START_OTHER + outSystemImage + END_OTHER
            log_file.close()
        return mkuserimgDict

    @classmethod
    def getMakeEmmcImageDict(cls, file=MAKE_LOG):
        '''
        根据make的log文件获取打包emmc的参数
        :param file: log文件的路径
        '''
        mkuserimgDict = dict()
        # 'mkuserimg.sh -s out/target/product/zechin82_we_kk/data/app out/target/product/zechin82_we_kk/userdata.img ext4 data 967835648 out/target/product/zechin82_we_kk/root/file_contexts'
        # ' mkuserimg.sh -s out/target/product/zechin82_we_kk/system out/target/product/zechin82_we_kk/obj/PACKAGING/systemimage_intermediates/system.img ext4 system 1073741824 out/target/product/zechin82_we_kk/root/file_contexts'
        if isfile(file):
            log_file = open(file, mode='r', encoding=Tool.checkFileCode(file))
            for line in log_file.readlines():
                match = re.match(r'^Running:  mkuserimg.sh -s ([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) (.+)$', line.strip())
                if match:
                    OUTPUT_FILE = match.group(2)
                    EXT_VARIANT = match.group(3)
                    MOUNT_POINT = match.group(4)
                    SIZE = match.group(5)
                    OTHER = match.group(6)
                    outPath = sep.join(['out', 'target', 'product', MTK_PROJECT])
                    print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + MOUNT_POINT+' size is '+Tool.COLOR_START + '31m' + SIZE + Tool.COLOR_END )
                    if (MOUNT_POINT == 'cache'):
                        mkuserimgDict['cache'] = 'mkuserimg.sh -s ' + ' '.join(match.groups())
                        mkuserimgDict['cache_size'] = SIZE
                    elif (MOUNT_POINT == 'data'):
                        outDataImage = sep.join([outPath, 'userdata.img'])
                        mkuserimgDict['data'] = 'mkuserimg.sh -s ' + ' '.join([Tool.OUT_DATA, outDataImage, EXT_VARIANT, MOUNT_POINT, SIZE, OTHER])
                        mkuserimgDict['data_size'] = SIZE
                    elif (MOUNT_POINT == 'system'):
                        outSystemImage = sep.join([outPath, 'system.img'])
                        mkuserimgDict['system'] = 'mkuserimg.sh -s ' + ' '.join([Tool.OUT_SYSTEM, outSystemImage, EXT_VARIANT, MOUNT_POINT, SIZE, OTHER])
                        mkuserimgDict['system_size'] = SIZE
            log_file.close()
        return mkuserimgDict

    @classmethod
    def copyfiles(cls, argv):
        '''
        根据参数中制定文件集合的文件来拷贝当前项目中的文件，主要用于项目移植提取以前项目修改过的文件
        :param argv: 
        '''
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        out_dir = 'svn_copy'
        temp = '.cache'
        svn_log_file = None
        svn_log_path = None
        if '-p' in argv:
            index_p = argv.index('-p')
            if len(argv) > (index_p + 1) and isfile(sep.join([argv[index_p + 1],'copy_log.txt'])):
                svn_log_path = argv[index_p + 1]
                if svn_log_path.endswith('/'):
                    svn_log_path = svn_log_path[0:-1]
                out_dir='.'
        if '-f' in argv:
            index_f = argv.index('-f')
            if len(argv) > (index_f + 1):
                svn_log_file = argv[index_f + 1]
        if '-o' in argv:
            index_o = argv.index('-o')
            if len(argv) > (index_o + 1):
                out_dir = argv[index_o + 1]
                if out_dir.endswith('/'):
                    out_dir = out_dir[0:-1]
        if not svn_log_file and not svn_log_path:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m使用方法：' + Tool.COLOR_START + Tool.COLOR_BG1 + '31m 命令 -f 拷贝文件列表集合的文件 -o 输出的目录' + Tool.COLOR_END)
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m使用方法：' + Tool.COLOR_START + Tool.COLOR_BG1 + '31m 命令 -p 还原拷贝文件目录(目录中包含copy_log.txt文件) -o 输出的目录' + Tool.COLOR_END)
            exit(1)
        else:
            copys = [lambda file:not print('==>',file), lambda file:copyfile(file, temp) and not os.chmod(temp, os.stat(file).st_mode), lambda file:not os.system(' '.join(['mv',temp,file]))]

        if svn_log_file and isdir(out_dir) and isfile(svn_log_file):
            os.system('rm -rf ' + out_dir)
        cpfile = lambda in_file, out_file: copys[1](in_file) and copys[2](out_file) and copys[0](in_file)
        if not isdir(out_dir):
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m创建目录' + out_dir + Tool.COLOR_END)
            makedirs(out_dir)
        print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m开始拷贝' + Tool.COLOR_END)

        if svn_log_file and isfile(svn_log_file):
            del_files = list()
            dir_files = list()
            modify_files = list()
            all_files = list()
            with open(svn_log_file, mode='r', encoding=Tool.checkFileCode(svn_log_file)) as log_file:
                for line in log_file.readlines():
                    copyFile = line.strip()
                    if isfile(copyFile):
                        inFile = copyFile
                        outFile = sep.join([out_dir, copyFile])
                        if not isdir(dirname(outFile)):
                            makedirs(dirname(outFile))
                        if not cpfile(inFile, outFile):
                            print('err copy ==>', inFile)
                        modify_files.append('file: ' + inFile)
                        if not inFile in all_files:
                            all_files.append(inFile)
                    elif isdir(copyFile):
                        outDir = sep.join([out_dir, copyFile])
                        if not isdir(outDir):
                            makedirs(outDir)
                        for parent, dirs, filenames in os.walk(copyFile):
                            for filename in filenames:
                                inFile = sep.join([parent, filename])
                                outFile = sep.join([out_dir, inFile])
                                if not isdir(dirname(outFile)):
                                    makedirs(dirname(outFile))
                                if not cpfile(inFile, outFile):
                                    print('err copy ==>', inFile)
                                modify_files.append('file: ' + inFile)
                                if not inFile in all_files:
                                    all_files.append(inFile)
                        dir_files.append('dir: ' + copyFile)
                    else:
                        del_files.append('del: ' + copyFile)
                log_file.close()

            #所以的改动保存到log中
            copyLogFile = open(sep.join([out_dir, 'copy_log.txt']), mode='w')
            for file in del_files:
                copyLogFile.write(file+'\n')
            for file in dir_files:
                copyLogFile.write(file+'\n')
            for file in modify_files:
                copyLogFile.write(file+'\n')
            copyLogFile.flush()
            copyLogFile.close()
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m拷贝结束，已拷贝到目录' + out_dir + Tool.COLOR_END)
            return all_files
        else:
            err = list()
            rmDirs = list()
            modify_path = list()
            getParent = lambda file: dirname(file) if isdir(dirname(file)) else getParent(dirname(file))
            with open(sep.join([svn_log_path, 'copy_log.txt']), mode='r') as log_file:
                for line in log_file.readlines():
                    match = re.match('[\w]+: (.+)',line)
                    if match:
                        rootDir = match.group(1).split(sep)[0]
                        if not rootDir in modify_path:
                            modify_path.append(rootDir)
                    match = re.match('file: (.+)',line)
                    if match:
                        file = match.group(1)
                        file_from=sep.join([svn_log_path, file])
                        file_to=sep.join([out_dir, file])
                        if not isdir(dirname(file_to)):
                            makedirs(dirname(file_to))
                        if isfile(file_from):
                            print_and_execute(' '.join(['cp', '-r', file_from, file_to]))
                        else:
                            err.append('not isfile '+file_from)
                        continue
                    match = re.match('dir: (.+)',line)
                    if match:
                        dir = sep.join([out_dir, match.group(1)])
                        file_from=sep.join([svn_log_path, dir])
                        file_to=sep.join([out_dir, dir])
                        if not isdir(dir):
                            print_and_execute(' '.join(['mkdir',dir]))
                        #print_and_execute(' '.join(['cp', '-r', file_from, file_to]))
                        continue
                    match = re.match('del: (.+)',line)
                    if match:
                        del_file = sep.join([out_dir, match.group(1)])
                        if isfile(del_file) or isdir(del_file):
                            if isdir(del_file) and not del_file in rmDirs:
                                rmDirs.append(del_file)
                            print_and_execute(' '.join(['rm','-rf',del_file]))
                        parent = getParent(del_file)
                        if len(listdir(parent)) == 0:
                            print_and_execute(' '.join(['rm','-rf',parent]))
                            if not parent in rmDirs:
                                rmDirs.append(parent)
                        continue
                    if len(line)>0:
                        err.append(line)
            if len(err):
                print(getStrStype1('未能成功解析文件')+getStrStype2('\n'.join(sorted(err))))
            if len(rmDirs):
                print(getStrStype1('删除目录')+'\n'+getStrStype2('\n'.join(sorted(rmDirs))))
            if len(modify_path):
                print(getStrStype1('修改目录')+'\n'+getStrStype2(' '.join(sorted(modify_path))))
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m拷贝结束，已拷贝到目录' + out_dir + Tool.COLOR_END)


    @classmethod
    def svn_new(cls):
        '''
        删除本地代码，然后根据本地svn地址拉去新的源码进行编译
        '''
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        lines = popen('svn info | grep "URL: svn:"').read().splitlines()
        svnaddr = lines[0] if lines and len(lines) else None
        dirName = None
        if svnaddr and len(svnaddr)>0:
            match = re.match(r'^URL: (.+)$', svnaddr)
            if match:
                svnaddr = match.group(1)
        while not svnaddr or len(svnaddr)==0 or not re.match(r'^svn:.*', svnaddr):
            svnaddr = input('请输入svn地址 例如：svn://192.168.1.66/MTK_ZN/6735_51/branches/sec6580_m\n')
            dirName = svnaddr.split(sep)[-1] if len(svnaddr.split(sep)[-1])>0 else svnaddr.split(sep)[-2]
        dirName = dirName if dirName else popen('pwd').read().splitlines()[0].split(sep)[-1]
        oldCwd = os.getcwd()
        Tool.checkDriveList(True)
        if not Tool.setAutoNew(argv) and not Tool.readParameters():
            Tool.setParameters(saveToFile=True)
        Tool.checkSelect()
        if isfile(Tool.INI_FILE):
            move(Tool.INI_FILE, '../.xhl.ini')
        if isfile(Tool.INI_FILE_OLD):
            move(Tool.INI_FILE_OLD, '../.xhl_old.ini')
        if isfile(Tool.CURSTOMER_INI_FILE):
            move(Tool.CURSTOMER_INI_FILE, '../.xhl_curstomer.ini')
        os.chdir(dirname(oldCwd))
        print_and_execute('rm -rf '+dirName)
        print_and_execute(' '.join(['svn co', svnaddr, dirName]))
        os.chdir(sep.join([os.getcwd(), dirName]))
        if isfile('../.xhl.ini'):
            move('../.xhl.ini', Tool.INI_FILE)
        if isfile('../.xhl_old.ini'):
            move('../.xhl_old.ini', Tool.INI_FILE_OLD)
        if isfile('../.xhl_curstomer.ini'):
            move('../.xhl_curstomer.ini', Tool.CURSTOMER_INI_FILE)
        Tool.copyDriverFiles()
        Tool.mm(['new',])
        Tool.buildimage()

    @classmethod
    def svn_db_restore(cls, path='.svn/wc.db'):
        def get_table(path, tablename):
            import sqlite3
            conn = sqlite3.connect(path)
            c = conn.cursor()
            c.execute("SELECT * FROM {}".format(tablename))
            columns = [d[0] for d in c.description]
            rows = []
            for row in c:
                rows.append(row)
            return columns, rows
        def restore(db_file):
            tables = ['NODES', 'PRISTINE']
            commands = list()
            hasSqlComm = False
            for item in os.environ['PATH'].split(':'):
                if isfile(sep.join([item,'sqlite3'])):
                    print(sep.join([item,'sqlite3']))
                    hasSqlComm = True
                    break
            if not hasSqlComm:
                LIB_PATH = sep.join([dirname(abspath(__file__)),'sqlite3','obj','lib'])
                os.system('chomd 777 '+LIB_PATH)
                commands.append('export LD_LIBRARY_PATH='+LIB_PATH+(':$LD_LIBRARY_PATH' if 'LD_LIBRARY_PATH' in os.environ else ''))
                commands.append('echo LD_IBRARY_PATH=$LD_IBRARY_PATH')
                BIN_PATH = sep.join([dirname(abspath(__file__)),'sqlite3','bin'])
                os.system('chomd 777 '+BIN_PATH)
                commands.append('export PATH='+BIN_PATH+':$PATH')
                commands.append('echo PATH=$PATH')
            command ='cp -r '+db_file+' '+db_file+'.bak'
            commands.append('echo start comm : '+command)
            commands.append('cp -r '+db_file+' '+db_file+'.bak')
            command = ' '.join(['sqlite3',db_file,'\"pragma integrity_check\"'])
            commands.append('echo start comm : '+command)
            commands.append(command)
            for table in tables:
                command = ' '.join(['sqlite3',db_file,'\"reindex', table,'\"'])
                commands.append('echo start comm : '+command)
                commands.append(command)
            commands.append('rm '+db_file+'.bak')
            os.system(';'.join(commands))

        #print(get_table(path,'nodes'))
        #print(get_table(path,'pristine'))
        restore(path)
        print('这个问题帮你解决了嘛？')

    @classmethod
    def svnrevert(cls, revert_path=None, rm_xhl=False):
        '''
        清除本地修改的文件但是out和xhl目录例外
        svn revert -R .
        rm -rvf `svn st --no-ignore | awk "{print $2}"`
        svn up
        '''
        if not revert_path:
            revert_path = '.'
        if isfile(Tool.INI_FILE):
            move(Tool.INI_FILE, '../.xhl.ini')
        if isfile(Tool.INI_FILE_OLD):
            move(Tool.INI_FILE_OLD, '../.xhl_old.ini')
        if isfile(Tool.CURSTOMER_INI_FILE):
            move(Tool.CURSTOMER_INI_FILE, '../.xhl_curstomer.ini')

        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        print_and_execute('svn revert -R '+revert_path)
        lines = popen('svn st --no-ignore ' + revert_path).read().splitlines()
        for line in [line for line in lines if line[:1] == '?']:
            add_path = line[1:].strip()
            if not (add_path.startswith('out') or (not rm_xhl and add_path.startswith(sep.join(['xhl','script']))) or len(add_path.split(sep))==1):
                print_and_execute('rm -rvf '+add_path)
        print_and_execute('svn up '+revert_path)

        if isfile('../.xhl.ini'):
            move('../.xhl.ini', Tool.INI_FILE)
        if isfile('../.xhl_old.ini'):
            move('../.xhl_old.ini', Tool.INI_FILE_OLD)
        if isfile('../.xhl_curstomer.ini'):
            move('../.xhl_curstomer.ini', Tool.CURSTOMER_INI_FILE)
    @classmethod
    def svncommit(cls, argv):
        '''
        svn提交修改d文件 -p指定文件路径 -m制定提交的信息 -i文件提交需要用户确认
        :param argv: 
        :return: 
        '''
        src_path = None
        interactive = False
        content = list()
        err = list()
        if '-p' in argv:
            index_p = argv.index('-p')+1
            while index_p < len(argv) and argv[index_p] != '-m':
                file_path = argv[index_p]
                if not (isfile(file_path) or isdir(file_path)):
                    err.append(file_path)
                content.append(argv[index_p])
                index_p = index_p+1
            src_path = ' '.join(content)
            print(src_path)
        if len(err)>0:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '31m不存在目录或者文件：' + Tool.COLOR_START + Tool.COLOR_BG1 + '\n30m' +' '.join(err)+ Tool.COLOR_START + Tool.COLOR_BG2 + Tool.COLOR_END+'\n')
            src_path = None
        if not src_path:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m使用方法：' + Tool.COLOR_START + Tool.COLOR_BG1 + '31m 命令 -p 路径 [-m 附加消息] [-i]' + Tool.COLOR_START + Tool.COLOR_BG2 + '30m -m 可选， -i 可选择， -i 与用户交互'+Tool.COLOR_END)
            exit(1)
        message = 'modify '+src_path
        content = list()
        content = list()
        if '-m' in argv:
            index_m = argv.index('-m')+1
            while index_m < len(argv) and argv[index_m] != '-p':
                content.append(argv[index_m])
                index_m = index_m+1
            message = ' '.join(content)

        if '-i' in argv:
            interactive = True

        lines = popen('svn st --no-ignore '+src_path).read().splitlines()
        if len(lines) == 0 or len(lines[0]) == 0:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m使用方法：' + Tool.COLOR_START + Tool.COLOR_BG1 + '31m 没有什么可以操作的' + Tool.COLOR_END)
            exit(0)

        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        choice_str = lambda action, file_path:Tool.COLOR_START + Tool.COLOR_BG2 + '30m是否'+action+'：' + Tool.COLOR_START + Tool.COLOR_BG1 + '31m '+file_path  + Tool.COLOR_START + Tool.COLOR_BG2+ '30m(y/n)' + Tool.COLOR_END+'\n'

        for line in lines:
            comm_line = None
            if line[:1] == '?' or line[:1] == 'I':
                comm_line = 'svn add '+line[1:].strip()
                choice_line =choice_str('添加', line[1:].strip())
            elif line[:1] == '!':
                comm_line = 'svn del '+line[1:].strip()
                choice_line =choice_str('修改', line[1:].strip())

            if comm_line and interactive:
                choice = input(choice_line)
                if len(choice) == 0 or choice == 'Y' or choice == 'y':
                    print_and_execute(comm_line)
            elif comm_line:
                print_and_execute(comm_line)

        print_and_execute(' '.join(['svn ci -m', '\"'+message+'\"', src_path]))

    @classmethod
    def buildBootImage(cls,argv=[]):
        '''
        打包boot.img
        '''
        os.environ['PATH'] = sep.join(['.', 'out', 'host', 'linux-x86', 'bin']) + ':' + os.environ['PATH']
        if not isfile(sep.join(['.', 'out', 'host', 'linux-x86', 'bin', 'mkbootimg'])):
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m请先./mm_new一个工程' + Tool.COLOR_END)
            exit(0)
        mBuildProp = sep.join(['.', 'out', 'target', 'product', MTK_PROJECT, 'root', 'default.prop'])
        if not isfile(mBuildProp):
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m请先./mm bootimage' + Tool.COLOR_END)
            exit(0)
        print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m请先开始打包bootimage ...' + Tool.COLOR_END)
        #覆盖root下面的default.prop 从Project_Screen/boot_build.prop中提取
        Tool.checkDriveList(False)
        if not Tool.readParameters(Tool.INI_FILE) and not Tool.readParameters(Tool.INI_FILE_OLD):
            Tool.setParameters(saveToFile=False, readFile=Tool.INI_FILE)
        mProject = Tool.getParamter(PROJECT)
        mScreen = Tool.getParamter(SCREEN)
        projectProp = sep.join([Tool.MERGE_ROOT_PATH, mProject + '_' + mScreen, 'boot_build.prop'])
        if isfile(projectProp):
            projectPropFile = open(projectProp, 'r', encoding=Tool.checkFileCode(projectProp))
            for line in projectPropFile.readlines():
                match = re.match(r'([\w\.\+]*)[ |=|:]+(.*)', line)
                if match:
                    Tool.chgvalue(mBuildProp, match.group(1), match.group(2))

        getProjectPath = lambda name : sep.join(['.', 'out', 'target', 'product', MTK_PROJECT, name])
        getExeFile = lambda name : sep.join(['.', 'out', 'host', 'linux-x86', 'bin', name])
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))

        MTK_HEADER_SUPPORT = Tool.findValue('MTK_HEADER_SUPPORT') != 'no'
        TARGET_ROOT_OUT = getProjectPath('root')
        TARGET_OUT = getProjectPath('system')
        MKBOOTIMG = getExeFile('mkbootimg')
        MAKIMAGE = getExeFile('mkimage')
        MKBOOTFS = getExeFile('mkbootfs')
        MINIGZIP = getExeFile('minigzip')
        KERNEL = getProjectPath('kernel')
        custom_build_verno = getProjectPath('custom_build_verno')

        #生成ramdisk.img路径
        INSTALLED_RAMDISK_TARGET = sep.join(['xhl','out','ramdisk.img'])
        INSTALLED_RAMDISK_TEMP = INSTALLED_RAMDISK_TARGET+'_raw'
        BOOT_IMAGE_TARGET = sep.join(['xhl','out','boot.img'])
        not_find_files = list()
        if not isfile(KERNEL):
            not_find_files.append(kernel)
        if not isfile(MKBOOTFS):
            not_find_files.append(MKBOOTFS)
        if not isfile(MINIGZIP):
            not_find_files.append(MINIGZIP)
        if not isfile(MAKIMAGE) and MTK_HEADER_SUPPORT:
            not_find_files.append(MAKIMAGE)
        if not isdir(TARGET_ROOT_OUT):
            not_find_files.append(TARGET_ROOT_OUT)

        if len(not_find_files)>0:
            getStrStype1('未找到文件或文件夹 '+' '.join(not_find_files))
            exit(-1)
        if not 'mk' in argv and not isfile(custom_build_verno):
            getStrStype1('未找到文件'+custom_build_verno)
            exit(-1)
        if 'mk' in argv:
            print_and_execute(' '.join([__file__,'mm',getProjectPath('ramdisk.img')]))
            print_and_execute(' '.join([__file__,'mm',getProjectPath('boot.img')]))
            print_and_execute(' '.join(['cp','-r',getProjectPath('boot.img'),BOOT_IMAGE_TARGET]))
        else:
            '''
            # the ramdisk
            INTERNAL_RAMDISK_FILES := $(filter $(TARGET_ROOT_OUT)/%, \
            $(ALL_PREBUILT) \
            $(ALL_COPIED_HEADERS) \
            $(ALL_GENERATED_SOURCES) \
            $(ALL_DEFAULT_INSTALLED_MODULES))
            '''
            if MTK_HEADER_SUPPORT:
                '''$(MKBOOTFS) -d $(TARGET_OUT) $(TARGET_ROOT_OUT) | $(MINIGZIP) > $@_raw'''
                print_and_execute(' '.join([MKBOOTFS, '-d', TARGET_OUT, TARGET_ROOT_OUT, '|', MINIGZIP, INSTALLED_RAMDISK_TEMP]))
                '''$(HOST_OUT_EXECUTABLES)/mkimage $@_raw ROOTFS 0xffffffff > $@'''
                print_and_execute(' '.join([MAKIMAGE, INSTALLED_RAMDISK_TEMP, 'ROOTFS', '0xffffffff', '>', INSTALLED_RAMDISK_TARGET]))
                if isfile(INSTALLED_RAMDISK_TEMP):
                    os.system(' '.join(['rm ', INSTALLED_RAMDISK_TEMP]))
            else:
                '''$(MKBOOTFS) -d $(TARGET_OUT) $(TARGET_ROOT_OUT) | $(MINIGZIP) > $@'''
                print_and_execute(' '.join([MKBOOTFS, '-d', TARGET_OUT, TARGET_ROOT_OUT, '|', MINIGZIP, '>', INSTALLED_RAMDISK_TARGET]))

            kernel=KERNEL
            ramdisk=INSTALLED_RAMDISK_TARGET
            cmdline='bootopt=64S3,32S1,32S1'
            base='0x80000000'
            ramdisk_offset='0x04000000'
            kernel_offset='0x00008000'
            tags_offset='0xE000000'
            board=open(custom_build_verno, mode='r').readline()[0:15]
            output=BOOT_IMAGE_TARGET
            com= list()
            com.append(MKBOOTIMG)
            com.append('--kernel')
            com.append(kernel)
            com.append('--ramdisk')
            com.append(ramdisk)
            com.append('--cmdline')
            com.append(cmdline)
            com.append('--base')
            com.append(base)
            com.append('--ramdisk_offset')
            com.append(ramdisk_offset)
            com.append('--kernel_offset')
            com.append(kernel_offset)
            com.append('--tags_offset')
            com.append(tags_offset)
            com.append('--board')
            com.append(board)
            com.append('--kernel_offset')
            com.append(kernel_offset)
            com.append('--ramdisk_offset')
            com.append(ramdisk_offset)
            com.append('--tags_offset')
            com.append(tags_offset)
            com.append('--output')
            com.append(output)

            print_and_execute(' '.join(com))
        if isfile(INSTALLED_RAMDISK_TARGET):
            os.system(' '.join(['rm ', INSTALLED_RAMDISK_TARGET]))

        if isfile(BOOT_IMAGE_TARGET):
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30mFinish build '+BOOT_IMAGE_TARGET + Tool.COLOR_END + '\n' + popen('ls -alh '+BOOT_IMAGE_TARGET).read())
        else:
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '31mFinish err' + BOOT_IMAGE_TARGET + Tool.COLOR_END)

    @classmethod
    def diff(cls, argv=None):
        #定义lambda
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        #new files
        src_dir = './src_dir'
        #old files
        dst_dir = './dst_dir'
        #diff files
        modify_dir = './diff_dir'
        #add files
        #add_dir = './add_dir'
        #del files
        #del_dir = './del_dir'
        #相对旧文件夹删除的文件
        del_files = list()
        #相对旧文件夹添加的文件
        add_files = list()
        #相对于旧文件夹修改的文件
        modify_files = list()
        print_file = None
        #获取新文件路径
        if argv and '-n' in argv:
            index_s = argv.index('-n')+1
            if index_s < len(argv):
                src_dir = argv[index_s]
        #获取旧文件路径
        if argv and '-o' in argv:
            index_d = argv.index('-o')+1
            if index_d < len(argv):
                dst_dir = argv[index_d]
        #获取存放差异文件的路径
        if argv and '-m' in argv:
            index_m = argv.index('-m')+1
            if index_m < len(argv):
                modify_dir = argv[index_m]
        if not isdir(src_dir) or not isdir(dst_dir):
            print(getStrStype2('未找到新文件目录'+src_dir+' 旧文件目录'+dst_dir)+'\n')
            print(getStrStype2('格式:')+getStrStype1('tool diff [-n src] [-o dst] [-m diff] [-p log]')+getStrStype2('(-n 指定新文件目录 -o 指定旧文件目录 -m 差异文件存放目录 -p 保存差异信息文件路径)'))
            exit(0)

        if not src_dir.endswith(sep):
            src_dir = src_dir+sep
        if not dst_dir.endswith(sep):
            dst_dir = dst_dir+sep
        if not modify_dir.endswith(sep):
            modify_dir = modify_dir+sep

        #日志输出文件
        if argv and '-p' in argv:
            index_p = argv.index('-p')+1
            if index_p < len(argv):
                print_file = argv[index_p]
            if print_file == None:
                print_file = modify_dir+'diff_log.txt'
        is_action = print_file == None
        #是否执行文件覆盖和添加
        if is_action:
            if isdir(modify_dir):
                rmtree(modify_dir)
            makedirs(modify_dir)
        src_len = len(src_dir)
        dst_len = len(dst_dir)
        print('src_dir={} dst_dir={} modify_dir={}'.format(src_dir,dst_dir,modify_dir))
        print(getStrStype2('开始......')+'\n')
        print(getStrStype2('查找删除文件'))
        #查找旧文件夹删除的文件
        for parent, dirnames, filenames in os.walk(dst_dir):
            break
            if '.svn' in parent or '.git' in parent:
                continue
            for filename in filenames:
                file_path = ((parent if parent.endswith(sep) else parent+sep)+filename)[dst_len:]
                src_path = src_dir+file_path
                dst_path = dst_dir+file_path
                if isfile(dst_path) and not isfile(src_path):
                    print('rm ==> '+filename)
                    del_files.append(file_path)
                    if is_action:
                        remove(dst_path)
                    if len(listdir(dirname(dst_path)))==0:
                        rmtree(dirname(dst_path))
                        del_files.append(dirname(dst_path))
        #查找新文件夹中添加和修改的文件
        print(getStrStype2('查找添加和修改的文件'))
        for parent, dirnames, filenames in os.walk(src_dir):
            if '.svn' in parent or '.git' in parent:
                continue
            for dir_name in dirnames:
                break
                file_path = ((parent if parent.endswith(sep) else parent+sep)+dir_name)[src_len:]
                src_path = src_dir+file_path
                dst_path = dst_dir+file_path
                if isdir(src_path) and not isdir(dst_path):
                    print('add ==> '+file_path)
                    add_files.append(file_path)
                    if is_action:
                        if not isdir(dirname(dst_path)):
                            makedirs(dirname(dst_path))
                        os.system('cp -r {} {}'.format(src_path, dst_path))

            for filename in filenames:
                file_path = ((parent if parent.endswith(sep) else parent+sep)+filename)[src_len:]
                src_path = src_dir+file_path
                dst_path = dst_dir+file_path
                if isfile(src_path) and not isfile(dst_path):
                    print('add ==> '+file_path)
                    add_files.append(file_path)
                    if is_action:
                        if not isdir(dirname(dst_path)):
                            makedirs(dirname(dst_path))
                        os.system('cp -r {} {}'.format(src_path, dst_path))
                elif not path.islink(src_path) and isfile(src_path) and len(popen('diff "'+src_path+'" "'+dst_path+'"').read()) != 0 :
                    modify_files.append(file_path)
                    print('modify ==> '+file_path)
                    if is_action:
                        modify_path = modify_dir+file_path
                        if not isdir(dirname(modify_path)):
                            makedirs(dirname(modify_path))
                        os.system('cp -r {} {}'.format(src_path, modify_path))
        #保存修改信息
        out_file = modify_dir+'diff_log.txt' if is_action else print_file
        with open(out_file, mode='w', encoding='utf-8') as fileOut:
            fileOut.writelines('del files:\n'+'\n'.join(del_files)+'\n')
            fileOut.writelines('add files:\n'+'\n'.join(add_files)+'\n')
            fileOut.writelines('modify files:\n'+'\n'.join(modify_files)+'\n')
            fileOut.flush()
            fileOut.close()
        print(getStrStype2('打工完成 log文件--->{}'.format(out_file)))

    @classmethod
    def patch(cls, svn_ci=True):
        '''
        打包补丁 根据提示完成打补丁功能
        :param svn_ci: 每打一个补丁是否讲补丁提交到svn服务器上
        '''
        #操作的第几步
        handle_num = 0
        os.system('stty erase ^H')
        #补丁数
        patch_count = 0
        #使用补丁数
        use_patch_count = 0
        #mtk的patch压缩包存放目录
        pathch_path = sep.join(['xhl','patch', 'patchs_tar_gz'])
        if not isdir(pathch_path):
            makedirs(pathch_path)

        #修改的文件和patch里的文件冲突文件保存目录
        over_modify_path = sep.join(['xhl', 'patch', 'modify_diff_mtk_patch'])

        #打完补丁后检测补丁不同意根目录的文件放在这个目录
        leave_mtk_patch = sep.join(['xhl', 'patch', 'leave_mtk_patch'])

        #以前修改过的文件保存目录
        modify_path = sep.join(['xhl', 'patch', 'modify'])
        os.system('rm -rf '+modify_path)
        makedirs(modify_path)

        #patch临时解压工作目录
        temp_patch = sep.join(['xhl', 'patch', 'temp_mtk_patch'])
        os.system('rm -rf '+temp_patch)
        makedirs(temp_patch)

        #mtk的patch解压后处理完成都放到这个目录
        mtk_patch = sep.join(['xhl', 'patch', 'mtk_patch'])
        os.system('rm -rf '+mtk_patch)
        makedirs(mtk_patch)

        xhl_patch_list_text = sep.join(['xhl', 'patch', 'patch_list.txt'])
        svn_log = sep.join(['xhl', 'patch', 'svn_log.txt'])

        #定义lambda
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)

        printStrStype2('打补丁前做以下准备')
        Tool.auto_patch = False
        handle_num = handle_num+1
        choice = input(getStrStype1(str(handle_num)+'.是否自动打补丁(Y/y)或回车？，其它任意键不使用自动打补丁：'))
        if choice == 'Y' or choice == 'y':
            Tool.auto_patch = True

        print('auto_patch:' + str(Tool.auto_patch))

        Tool.auto_over_diff_patch = False
        handle_num = handle_num+1
        choice = input(getStrStype1(str(handle_num)+'.是否补丁自动覆盖以前修改过的文件(Y/y)或回车？，其它任意键不会自动覆盖会等待你的修改：'))
        if choice == 'Y' or choice == 'y':
            Tool.auto_over_diff_patch = True

        print('auto_over_diff_patch:' + str(Tool.auto_over_diff_patch))

        global_svn = popen('grep "global-ignores =" ~/.subversion/config -rHn').read().splitlines()[0]
        if len(global_svn)>0:
            items = global_svn.split(':')
            #/home/xl/.subversion/config:95:global-ignores = *.o *.lo *.la *.al .libs *.a *.pyc *.pyo __pycache__
            if len(items)==3:
                global_svn_filename = items[0]
                global_svn_line = items[1]
                global_svn_content = items[2]
                match = re.match('.*=(.*)', global_svn_content)
                if match:
                    choice = input(getStrStype2('svn提交过滤文件'+match.group(1)+' 是否要修改？(Y/y)，回车或其它任意键不修改：'))
                    if choice == 'Y' or choice == 'y':
                        os.system('vim '+global_svn_filename+' +'+global_svn_line)

        #代码新版本
        handle_num = handle_num+1
        choice = input(getStrStype1(str(handle_num)+'.是否是全新版本而且没有任何操作(Y/y)或回车？不是选择(N/n)直接退出'))
        if choice == 'N' or choice == 'N':
            sys.exit(0)
        #导出修改过的文件
        if not isfile(svn_log):
            os.system('touch '+svn_log)
        handle_num = handle_num+1
        printStrStype1(str(handle_num)+'.导出以前修改过的文件')
        printStrStype2('    1).通过Windown版本的svn查看并点击所有自己修改过的log记录，选择下方所有的文件')
        printStrStype2('    2).将所选择的文件保持到工作目录'+svn_log+'中')
        printStrStype2('    3).将'+svn_log+'文件中的所有文件路径更正为当前路径\n')
        input(getStrStype2('    做好以上工作后请按Y/y或直接回车键确认：'))
        if not isfile(svn_log):
            choice = input(getStrStype2('你没有修改过任何文件，所以没有log记录？(Y/y)'))
            if choice != 'Y' and choice != 'y':
                sys.exit(0)
        else:
            handle_num = handle_num+1
            printStrStype1(str(handle_num)+'.现在将'+svn_log+'中的文件保存到'+modify_path+'目录中')
            Tool.copyfiles(list(['-f', svn_log, '-o', modify_path]))

        printStrStype1('----------------------------现在开始打补丁----------------------------')
        handle_num = handle_num+1
        input(getStrStype1(str(handle_num)+'.请讲补丁压缩包(补丁包为tar.gz文件)放入'+pathch_path+'目录中后按回车键。'))
        if not isdir(pathch_path) or listdir(pathch_path)==0:
            printStrStype1('    没有发现补丁，我退出啦。。。')
            sys.exit(0)
        #搜索xhl/patchs目录下的patch文件
        patch_files = [file for file in listdir(pathch_path) if re.match(r'.*_P(\d+_?\d*)\).tar.gz', file)]
        patch_dict = dict()
        for file in patch_files:
            match = re.match(r'.*_P(\d+_?\d*)\).tar.gz', file)
            if match:
                patch_dict[float(match.group(1).replace('_','.'))] = file
        print()
        #对patch_files里的文件名进行排序
        patch_files.clear()
        for key in sorted(patch_dict.keys()):
            patch_files.append(patch_dict[key])

        for patch_file in patch_files:
            patch_file_index = patch_files.index(patch_file)
            patch_file = '  '+str(patch_file_index+1)+' ). '+patch_file
            print(getStrStype1(patch_file) if patch_file_index%2==0 else getStrStype2(patch_file))
        print()
        input(getStrStype1('    找到了以上'+str(len(patch_files))+'个补丁包(补丁包为tar.gz文件) 继续请按任意键'))
        #解压每个patch文件，根据patch_list.txt文件说明自动打patch
        mPatchType='Patch Type:'
        mCRID='CR ID:'
        mSeverity='Severity:'
        mDescription='Description:'
        mAssociatedFiles='Associated Files:'
        mDeleteFiles='Delete Files:'
        mOtherCaseRe=r'[a-z|A-Z][\w| ]+:[ ]*'
        mtk_patch_dict = dict()
        start_doing_patch_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #定义上次函数
        def commit(svn_ci, patch_count, prefix, mCrId, middle, patch_root_path, otherDic):
            message = '"'+prefix+' '+mCrId+'\n'+ middle+'"'
            print('补丁描述：', getStrStype2(message))
            mAFiles = list()
            if 'Associated' in otherDic.keys():
                mAFiles = otherDic['Associated']
            mDFiles = list()
            if 'Delete' in otherDic.keys():
                mDFiles = otherDic['Delete']
            mOFiles = list()
            if 'Over' in otherDic.keys():
                mOFiles = otherDic['Over']

            #检查是否和以前patch有冲突,并提升
            mOMFiles = list()
            for key, values in mtk_patch_dict.items():
                for mFile in [mFile for mFile in mAFiles if mFile in values and not key.startswith(prefix) and not mFile.endswith(sep+PROJECT_CONFIG)]:
                    mOMFiles.append(key+' --> '+mFile)
            if len(mOMFiles) > 0:
                print('和以前的补丁有覆盖文件,如果需要解决使用对比工具对比目录'+temp_patch+'和目录'+mtk_patch+'\n文件补丁号和文件名如下:')
                printStrStype2('\n'.join(mOMFiles))

            # 解决冲突文件
            if len(mOFiles) > 0:
                for over_item_file in mOFiles:
                    cp_from_file = sep.join([modify_path, over_item_file])
                    cp_to_file = sep.join([over_modify_path, over_item_file])
                    cp_to_dir = dirname(cp_to_file)
                    if not isdir(cp_to_dir):
                        makedirs(cp_to_dir)

                    if isfile(cp_from_file) and not isfile(cp_to_file):
                        print_and_execute(' '.join(['cp', '-R', cp_from_file, cp_to_file]))
                    elif not isfile(cp_from_file):
                        print(Tool.COLOR_START + '45;33m' +'---err----不存在----:' + cp_from_file+ Tool.COLOR_END)
                if Tool.auto_over_diff_patch:
                    printStrStype2('和以前修改文件有冲突,如果需要解决使用对比工具对比目录' + modify_path + '和目录' + temp_patch + ' \n' + getStrStype1('\n'.join(mOFiles)))
                else:
                    choice = input('和以前修改文件有冲突,如果需要解决使用对比工具对比目录' + modify_path + '和目录' + temp_patch + ' 解决文件冲突后按回车键继续， 如果切换到自动请按（A/a）:\n' + getStrStype1('\n'.join(mOFiles)))
                    if choice == 'A' or choice == 'a':
                        Tool.auto_over_diff_patch = True
            # 拷贝patch到源文件并上传
            if Tool.auto_patch:
                choice = 'Y'
            else:
                choice = input(getStrStype2('*****************************************************************\n不使用此补丁请按(N/n), 使用此补丁请按(Y/y)或者直接回车？ 如果切换到自动打补丁请按（A/a）。'))
                if choice == 'A' or choice == 'a':
                    Tool.auto_patch = True
                    choice = 'Y'

            if not choice or choice == 'Y' or choice == 'y':
                commit_paths = list()
                cp_from_paths = list()
                #修改或添加的文件
                for patch_file in mAFiles:
                    #拷贝patch文件
                    cp_from_path = dirname(sep.join([patch_root_path, patch_file]))
                    if not cp_from_path in cp_from_paths:
                        cp_from_paths.append(cp_from_path)
                        cp_to_path = dirname(patch_file)
                        if not isdir(cp_to_path):
                            makedirs(cp_to_path)
                        #添加说明文件里面没有添加补丁文件文件
                        len_mtk_patch = len(patch_root_path) + 1
                        for parent, dirnames, filenames in os.walk(cp_from_path):
                            for filename in filenames:
                                file_patch_path = sep.join([parent, filename])
                                new_file = file_patch_path[len_mtk_patch:]
                                if not isfile(new_file) and not new_file in mAFiles:
                                    print('add file (not in patch_file):'+new_file)
                                    mAFiles.append(new_file)
                        print_and_execute(' '.join(['cp', '-R', sep.join([cp_from_path, '*']), cp_to_path]))

                for patch_file in mAFiles:
                    parent_patch = patch_file.split(sep)[0]
                    if not parent_patch in commit_paths:
                        commit_paths.append(parent_patch)

                #删除的文件和从版本库删除
                for patch_file in mDFiles:
                    parent_patch = dirname(patch_file)
                    if not parent_patch in commit_paths:
                        commit_paths.append(parent_patch)
                    print_and_execute('rm -rf ' + patch_file)
                    if svn_ci:
                        print_and_execute('svn del ' + patch_file)

                if svn_ci:
                    printStrStype2('开始上传补丁...')
                    # 对提交目录精简，去除重复的
                    commit_paths = sorted(commit_paths)
                    current_path = None
                    new_commit_paths = list()
                    for commit_path in commit_paths:
                        if not current_path:
                            current_path = commit_path
                            new_commit_paths.append(current_path)
                        elif not commit_path.startswith(current_path):
                            new_commit_paths.append(current_path)
                            current_path = commit_path
                    if not current_path in new_commit_paths:
                        new_commit_paths.append(current_path)
                    commit_paths = list()
                    for commit_path in new_commit_paths:
                        if not commit_path in commit_paths:
                            commit_paths.append(commit_path)

                    #添加到版本库
                    for item_path in commit_paths:
                        print('svn st --no-ignore '+item_path)
                        lines = popen('svn st --no-ignore '+item_path).read().splitlines()
                        if len(lines) == 0 or len(lines[0]) == 0:
                            continue

                        for line in[line for line in lines if line[:1] == '?' or line[:1] == 'I']:
                            #如果路径在patch文件中提到就提交到svn库
                            svn_add_path = line[1:].strip()
                            svn_add_paths = [patch_file for patch_file in mAFiles if patch_file.startswith(svn_add_path)]
                            if len(svn_add_paths) > 0:
                                print_and_execute('svn add ' + svn_add_path)

                    #提交
                    print_and_execute('svn ci -m '+message+' '+' '.join(commit_paths))
                print(Tool.COLOR_START + '45;33m' + '---------------------------| ------成功使用'+str(patch_count)+'个补丁------ |---------------------------' + Tool.COLOR_END)
            else:
                printStrStype1('已跳过补丁'+prefix+' '+mCrId)
            print()

        #遍历patch_list.txt中的文件内容
        xhl_patch_list_file = open(xhl_patch_list_text, mode='a')
        for file in patch_files:
            #patch前缀
            message_prefix = re.match(r'.*_P(\d+_?\d*)\).tar.gz', file).group(1)
            while len(message_prefix) < 4:
                message_prefix = '0'+message_prefix
            message_prefix = 'P'+message_prefix
            if xhl_patch_list_file:
                xhl_patch_list_file.write('-----------------------------------------'+message_prefix+'-----------------------------------------' + '\n\n\n')
            if message_prefix == 'P001':
                os.system('echo 第一个补丁时间'+datetime.datetime.now().strftime('%Y-%m-%d')+' > '+patch_list_text)
            if isdir(temp_patch):
                os.system('rm -rf '+temp_patch)
            #解压文件
            tar = tarfile.open(sep.join([pathch_path,file]))
            for name in tar.getnames():
                tar.extract(name, path=temp_patch)
            #查找补丁和说明文件
            patch_list_txt=None
            patch_list_root=None
            for item in listdir(temp_patch):
                child_file = sep.join([temp_patch, item])
                if isdir(child_file):
                    patch_list_root = child_file
                if isfile(child_file):
                    patch_list_txt = child_file
            if not patch_list_txt:
                printStrStype1('没有找到patch说明文件patch_list.txt')
                continue
            if not patch_list_root:
                printStrStype1('没有找到patch文件目录alps')
                continue

            #当前的动作
            mAction=''
            #说明文档主体
            message_middle=''
            #patch号
            mCrId = ''
            #修改的文件集合
            mAssociatedFileList=list()
            #删除的文件
            mDeleteFileList=list()
            #补丁和以前修改文件发生冲突的文件
            mOverFileList=list()
            mType = ''

            #解析patch_list.txt文件
            patch_list_file = open(patch_list_txt, mode='r')
            for line in patch_list_file.readlines():
                if xhl_patch_list_file:
                    xhl_patch_list_file.write(line+'\n')
                content = line.strip()
                if len(message_middle) > 0:
                    message_middle = message_middle+content.replace('"', '#')+'\n'
                if content.startswith(mPatchType):
                    #发现是PatchType有可能已经便利了一个补丁所以判断是否处理完一个补丁，如果是补丁就提交
                    if (len(mAssociatedFileList) > 0 or len(mAssociatedFileList) > 0 or len(mAssociatedFileList) > 0):
                        use_patch_count = use_patch_count+1
                        commit(svn_ci ,use_patch_count, message_prefix, mCrId, message_middle, patch_list_root,{'Associated':mAssociatedFileList, 'Delete':mDeleteFileList, 'Over':mOverFileList })
                    mAction=mPatchType
                    message_middle = ''
                    mType = ''
                    mCrId = ''
                    mAssociatedFileList=list()
                    mDeleteFileList=list()
                    mOverFileList=list()
                    match = re.match(mPatchType+'(.*)', content)
                    if match and len(match.group(1).strip())>0:
                        mType = match.group(1).strip()
                elif content.startswith(mCRID):
                    mAction=mCRID
                    patch_count = patch_count + 1
                    match = re.match(mCRID+'(.*)', content)
                    if match and len(match.group(1).strip())>0:
                        mCrId = match.group(1).strip()
                        print(Tool.COLOR_START + '45;33m' + '---------------------------| ' + message_prefix + '-' + mCrId + ' 第' + str( patch_count) + '个补丁 |---------------------------' + Tool.COLOR_END)
                        printStrStype1('Path类型：' + mType)
                        printStrStype1('Path编号：' + mCrId)
                elif content.startswith(mSeverity):
                    mAction=mSeverity
                    match = re.match(mSeverity+'(.*)', content)
                    if match and len(match.group(1).strip())>0:
                        printStrStype1('Path核查：'+match.group(1).strip())
                elif content.startswith(mDescription):
                    mAction=mDescription
                    message_middle = '补丁信息:\n'
                elif content.startswith(mDeleteFiles):
                    mAction=mDeleteFiles
                    match = re.match(mDeleteFiles+'(.*)', content)
                    if match and len(match.group(1).strip())>0:
                        del_file_path = match.group(1).strip()
                        print(Tool.COLOR_START + '40;37m 删除文件' + del_file_path + Tool.COLOR_END)
                        mDeleteFileList.append(del_file_path)
                        # 删除mtk_patch目录下的文件
                        mtk_patch_path = sep.join([mtk_patch, del_file_path])
                        if exists(mtk_patch_path):
                            print(Tool.COLOR_START + '40;37m 删除文件' + mtk_patch_path + Tool.COLOR_END)
                            os.system('rm -rf ' + mtk_patch_path)
                elif content.startswith(mAssociatedFiles):
                    mAction=mAssociatedFiles
                    match = re.match(mAssociatedFiles+'(.*)', content)
                    if match and len(match.group(1).strip())>0:
                        content = match.group(1).strip()
                        if len(content) > 0:
                            #将文件名存入mkt_patch字典中
                            mtk_patch_key = message_prefix+' '+mCrId
                            if not mtk_patch_key in mtk_patch_dict.keys():
                                mtk_patch_dict[mtk_patch_key] = list()
                            mtk_patch_dict[mtk_patch_key].append(content)

                            #将文件名存入patch集合中
                            patch_item_file = sep.join([patch_list_root, content])
                            if isfile(patch_item_file):
                                modify_item_file = sep.join([modify_path, content])
                                #检查是否和以前修改文件有冲突
                                if isfile(modify_item_file):
                                    if os.system('diff '+patch_item_file+' '+modify_item_file) != '0':
                                        mAssociatedFileList.append(content)
                                        mOverFileList.append(content)
                                    else:
                                        print(Tool.COLOR_START + '40;37m' + '和以前修改文件'+content+'相同' +  Tool.COLOR_END)
                                else:
                                    mAssociatedFileList.append(content)
                            elif not Tool.auto_jump_warn:
                                choice = input(getStrStype1('提示：'+content+'   按回车继续,以后不需要提示请输入(A/a)回车'))
                                if choice == 'A' or choice == 'a':
                                    Tool.auto_jump_warn = True
                elif re.match(mOtherCaseRe, line):
                    mAction=content
                else:
                    if mAction==mPatchType and len(content)>0:
                        mType = content
                    if mAction==mCRID and len(content)>0:
                        mCrId= content
                        print(Tool.COLOR_START + '45;33m' + '---------------------------| '+message_prefix+'-'+mCrId+' 第'+str(patch_count)+'个补丁 |---------------------------' + Tool.COLOR_END)
                        printStrStype1('Path类型：'+mType)
                        printStrStype1('Path编号：' + mCrId)
                    if mAction==mSeverity and len(content)>0:
                        printStrStype1('Path核查：'+content)
                    if mAction==mDescription:
                        pass
                    if mAction==mDeleteFiles:
                        if len(content) > 0:
                            match = re.match('delete (.*)', content)
                            if match:
                                del_file_path = match.group(1).strip()
                                print(Tool.COLOR_START + '40;37m 删除文件' + del_file_path + Tool.COLOR_END)
                                mDeleteFileList.append(del_file_path)
                                #删除mtk_patch目录下的文件
                                mtk_patch_path = sep.join([mtk_patch, del_file_path])
                                if exists(mtk_patch_path):
                                    print(Tool.COLOR_START + '40;37m 删除文件' + mtk_patch_path + Tool.COLOR_END)
                                    os.system('rm -rf '+mtk_patch_path)
                    if mAction==mAssociatedFiles:
                        if len(content) > 0:
                            #将文件名存入mkt_patch字典中
                            mtk_patch_key = message_prefix+' '+mCrId
                            if not mtk_patch_key in mtk_patch_dict.keys():
                                mtk_patch_dict[mtk_patch_key] = list()
                            mtk_patch_dict[mtk_patch_key].append(content)

                            #将文件名存入patch集合中
                            patch_item_file = sep.join([patch_list_root, content])
                            if isfile(patch_item_file):
                                modify_item_file = sep.join([modify_path, content])
                                #检查是否和以前修改文件有冲突
                                if isfile(modify_item_file):
                                    if os.system('diff '+patch_item_file+' '+modify_item_file) != '0':
                                        mAssociatedFileList.append(content)
                                        mOverFileList.append(content)
                                    else:
                                        print(Tool.COLOR_START + '40;37m' + '和以前修改文件'+content+'相同' +  Tool.COLOR_END)
                                else:
                                    mAssociatedFileList.append(content)
                            elif not Tool.auto_jump_warn:
                                choice = input(getStrStype1('提示：'+content+'   按回车继续,以后不需要提示请输入(A/a)回车'))
                                if choice == 'A' or choice == 'a':
                                    Tool.auto_jump_warn = True
                    if mAction.startswith('Add') or mAction.startswith('add'):
                        #如果是文件名存入patch集合中
                        patch_item_file = sep.join([patch_list_root, content])
                        if isfile(patch_item_file):
                            modify_item_file = sep.join([modify_path, content])
                            #将文件名存入mkt_patch字典中
                            mtk_patch_key = message_prefix+' '+mCrId
                            if not mtk_patch_key in mtk_patch_dict.keys():
                                mtk_patch_dict[mtk_patch_key] = list()
                            mtk_patch_dict[mtk_patch_key].append(content)
                            if isfile(modify_item_file) and os.system('diff '+patch_item_file+' '+modify_item_file) != '0':
                                mAssociatedFileList.append(content)
                                mOverFileList.append(content)
                            else:
                                mAssociatedFileList.append(content)

            #文件遍历完后检查是否有文件中没有添加而patch又有的文件
            len_mtk_patch = len(patch_list_root)+1
            for parent, dirnames, filenames in os.walk(patch_list_root):
                for filename in filenames:
                    file_patch_path = sep.join([parent, filename])
                    file_path = file_patch_path[len_mtk_patch:]
                    if not file_path in mAssociatedFileList and (not isfile(file_path) or os.system('diff '+file_patch_path+' '+file_path) != '0'):
                        mAssociatedFileList.append(file_path)
            #文件遍历完后将最后添加的内容提交上去
            if (len(mAssociatedFileList) > 0 or len(mAssociatedFileList) > 0 or len(mAssociatedFileList) > 0):
                use_patch_count = use_patch_count + 1
                commit(svn_ci, use_patch_count, message_prefix, mCrId, message_middle, patch_list_root, {'Associated': mAssociatedFileList, 'Delete': mDeleteFileList, 'Over': mOverFileList})
            patch_list_file.close()

            #将temp_mtk_path里的文件移到mtk_path目录中
            print_and_execute(' '.join(['cp', '-R', sep.join([patch_list_root, '*']), mtk_patch]))

        # patch临时解压工作目录
        os.system('rm -rf ' + temp_patch)

        print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m补丁共计：' + str(patch_count) + '个 '+Tool.COLOR_START + Tool.COLOR_BG2 +'31m使用补丁共计'+str(use_patch_count)+'个' + Tool.COLOR_END)

        if svn_ci:
            handle_num = handle_num + 1
            input(getStrStype1(str(handle_num)+'.回车后开始检测补丁文件是否已经打完...'))

            len_mtk_patch = len(mtk_patch)+1
            for parent, dirnames, filenames in os.walk(mtk_patch):
                for filename in filenames:
                    file_patch_path = sep.join([parent, filename])
                    file_path = file_patch_path[len_mtk_patch:]
                    file_copy_from = file_patch_path
                    file_copy_to = sep.join([leave_mtk_patch,file_path])
                    action_cp = False
                    if not isfile(file_path):
                        action_cp = True
                    if not action_cp and os.system('diff "'+file_copy_from+'" "'+file_path+'"') != 0:
                        action_cp = True
                    if action_cp:
                        if not isdir(dirname(file_copy_to)):
                            makedirs(dirname(file_copy_to))
                        os.system('cp -R "'+file_copy_from+'" "'+file_copy_to+'"')
            print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m检测完毕...' + Tool.COLOR_END)

        end_doing_patch_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print()
        printStrStype1(start_doing_patch_time+'开始   ' + end_doing_patch_time+'结束')
        print()

        #检测根目录还没有svn提交的文件
        if svn_ci:
            handle_num = handle_num + 1
            printStrStype1(str(handle_num)+'.检测未提交的文件')
            other_nothings = [re.match(r'^.[ ]+([^ ]*)', item).group(1) for item in popen('svn st --no-ignore ./').read().splitlines() if not re.match(r'^.[ ]+'+sep.join(['xhl', 'patch'])+'.*', item)]
            if len(other_nothings) > 0:
                print(Tool.COLOR_START + Tool.COLOR_BG2 + '30m这些文件没有处理:\n' + Tool.COLOR_START + Tool.COLOR_BG2 + '31m' + '\n'.join( other_nothings) + Tool.COLOR_END)
                input(getStrStype2('修复后请回车'))
                print()

        handle_num = handle_num + 1
        printStrStype1(str(handle_num)+'.检测未使用的补丁文件')
        if isdir(leave_mtk_patch) and len(listdir(leave_mtk_patch))>0:
            printStrStype1('    发现未使用的补丁文件，现在已将它们导入到目录'+leave_mtk_patch)
            input(getStrStype2('    使用对比工具对比 ') + getStrStype1('当前工作目录') + getStrStype2(' 和文件夹 ') + getStrStype1(leave_mtk_patch) + getStrStype2(' ，检测右侧独有文件，查看补丁是否打完， 检查修改提交后按回车键继续！'))

        if isdir(over_modify_path) and len(listdir(over_modify_path)) > 0:
            handle_num = handle_num + 1
            printStrStype1(str(handle_num)+'.打的补丁文件和以前修改的文件有冲突')
            input(getStrStype2('    使用对比工具对比文件夹') + getStrStype1(over_modify_path) + getStrStype2('和')+getStrStype1('根目录')+getStrStype2('检查修改根目录中冲突的文件， 检查修改提交后按回车键继续！'))

        #打完补丁后检测补丁不同意根目录的文件放在这个目录
        del_path = lambda choice, file_path: print_and_execute(' '.join(['rm', '-rf', file_path])) if choice == 'Y' or choice == 'y' else print()

        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除'+leave_mtk_patch+'未使用补丁文件目录？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, leave_mtk_patch)

        #删除补丁压缩包目录
        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除'+pathch_path+'补丁压缩包目录？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, pathch_path)

        #删除修改的文件和patch里的文件冲突文件保存目录
        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除'+over_modify_path+'修改的文件和patch里的文件冲突文件保存目录？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, over_modify_path)

        # 以前修改过的文件保存目录
        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除' + modify_path + '导出修改的文件的目录？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, modify_path)

        # mtk的patch解压后处理完成都放到这个目录
        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除' + mtk_patch + ' mkt所有补丁目录(每次补丁打完后都存放到这个目录)？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, mtk_patch)

        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除' + xhl_patch_list_text + '文件，所以的补丁记录(建议提交到svn版本库)？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, xhl_patch_list_text)

        handle_num = handle_num + 1
        choice = input(getStrStype1(str(handle_num)+'.是否删除' + svn_log + '文件？(Y/y)，回车或其它任意键不删除：'))
        del_path(choice, svn_log)

    @classmethod
    def findFileFromEndSwith(cls, find_path, endswith):
        '''
        查找指定路径下制定文件名后缀的文件
        :param find_path: 查找的路径
        :param endswith: 文件的后缀名
        :return: 返回文件集合
        '''
        find_list=list()
        for parent, dirnames, filenames in os.walk(find_path):
            for filename in (sep.join([parent, filename]) for filename in filenames if filename.endswith(endswith)):
                find_list.append(filename)
        return find_list

    @classmethod
    def apktool(cls):
        '''
        相关apk的工具集 具体功能参照打印提示
        '''
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        out_bin = sep.join(['out', 'host', 'linux-x86','bin'])
        tool_path = sep.join([dirname(abspath(__file__)), 'apktool'])
        if not isdir(tool_path):
            printStrStype1('apktool工具目录不存在')
            sys.exit(0)
        elif not isdir(out_bin):
            printStrStype1('编译目录不存在')
        os.environ['PATH'] =  tool_path + ':' +out_bin + ':' + os.environ['PATH']
        exec_sh = lambda sh_file, args: not print(sh_file + ' ' + ' '.join(args)) and os.system(sh_file + ' ' + ' '.join(args))

        action_list = list()
        class Action:
            def __init__(self, short_name, name, info, action):
                self.short_name = short_name
                self.name = name
                self.info = info
                self.action= action

        dex_recompute_checksum_info = '''
dex-recompute-checksum -- recompute crc and sha1 of dex.
usage: dex-recompute-checksum [options] dex
options:
     -f,--force                   force overwrite
     -o,--output <out-dex-file>   output .dex file, default is [dex-name]-rechecksum.dex'''
        dex_recompute_checksum = sep.join([tool_path, 'dex-recompute-checksum.sh'])
        action_list.append(Action('checksum', getStrStype1('Dex recompute checksum')+getStrStype2(' -- recompute crc and sha1 of dex.'), dex_recompute_checksum_info, dex_recompute_checksum))

        baksmali_info='''
baksmali -- disassembles and/or dumps a dex file
usage: baksmali [options] <dex>
options:
     -b,--no-debug-info            [not impl] don't write out debug info (.local, .param, .line, etc.)
     -f,--force                    force overwrite
     -l,--use-locals               output the .locals directive with the number of n
                                   on-parameter registers, rather than the .register
     -o,--output <out>             output dir of .smali files, default is $current_dir/[jar-name]-out/
     -p,--no-parameter-registers   use the v<n> syntax instead of the p<n> syntax for registers mapped to 
                                   method parameters'''
        baksmali = sep.join([tool_path, 'baksmali.sh'])
        action_list.append(Action('baksmali', getStrStype1('Baksmali')+getStrStype2(' -- disassembles and/or dumps a dex file'), baksmali_info, baksmali))

        dex2jar_info = '''
dex2jar -- convert dex to jar
usage: dex2jar [options] <file0> [file1 ... fileN]
options:
     -d,--debug-info              translate debug info
     -e,--exception-file <file>   detail exception file, default is $current_dir/[file-name]-error.zip
     -f,--force                   force overwrite
     -n,--not-handle-exception    not handle any exception throwed by dex2jar
     -nc,--no-code
     -o,--output <out-jar-file>   output .jar file, default is $current_dir/[file-name]-dex2jar.jar
     -os,--optmize-synchronized   optmize-synchronized
     -p,--print-ir                print ir to Syste.out
     -r,--reuse-reg               reuse regiter while generate java .class file
     -s                           same with --topological-sort/-ts
     -ts,--topological-sort       sort block by topological, that will generate morereadable code, 
                              default enabled'''
        dex2jar = sep.join([tool_path, 'dex2jar.sh'])
        action_list.append(Action('dex2jar', getStrStype1('Dex2jar')+getStrStype2(' -- convert dex to jar'), dex2jar_info, dex2jar))

        dex2smali_info = '''
baksmali -- disassembles and/or dumps a dex file
usage: baksmali [options] <dex>
options:
     -b,--no-debug-info            [not impl] don't write out debug info (.local, .param, .line, etc.)
     -f,--force                    force overwrite
     -l,--use-locals               output the .locals directive with the number of n
                                   on-parameter registers, rather than the .register
     -o,--output <out>             output dir of .smali files, default is $current_dir/[jar-name]-out/
     -p,--no-parameter-registers   use the v<n> syntax instead of the p<n> syntax for registers mapped 
                               to method parameters'''
        dex2smali = sep.join([tool_path, 'dex2smali.sh'])
        action_list.append(Action('dex2smali', getStrStype1('Dex2smali')+getStrStype2(' -- disassembles and/or dumps a dex file'), dex2smali_info, dex2smali))

        jar2dex_info='''
jar2dex -- Convert jar to dex by invoking dx.
usage: jar2dex [options] <dir>
options:
     -f,--force                   force overwrite
     -o,--output <out-dex-file>   output .dex file, default is $current_dir/[jar-name]-jar2dex.dex'''
        jar2dex = sep.join([tool_path, 'jar2dex.sh'])
        action_list.append(Action('jar2dex', getStrStype1('Jar2dex')+getStrStype2(' -- Convert jar to dex by invoking dx.'), jar2dex_info, jar2dex))

        jar2jasmin_info='''
jar2jasmin -- Disassemble .class in jar file to jasmin file
usage: jar2jasmin [options] <jar>
options:
     -d,--debug              disassemble debug info
     -e,--encoding <enc>     encoding for .j files, default is UTF-8
     -f,--force              force overwrite
     -h,--help               Print this help message
     -o,--output <out-dir>   output dir of .j files, default is $current_dir/[jar-name]-jar2jasmin/'''
        jar2jasmin = sep.join([tool_path, 'jar2jasmin.sh'])
        action_list.append(Action('jar2jasmin', getStrStype1('Jar2jasmin')+getStrStype2(' -- Disassemble .class in jar file to jasmin file'), jar2jasmin_info, jar2jasmin))

        jasmin2jar_info='''
jasmin2jar -- Assemble .j files to .class file
usage: jasmin2jar [options] <jar>
options:
     -cv,--class-version <arg>       default .class version, [1~9], default 6 for JA
                                     VA6
     -d,--dump                       dump to stdout
     -e,--encoding <enc>             encoding for .j files, default is UTF-8
     -f,--force                      force overwrite
     -g,--autogenerate-linenumbers   autogenerate-linenumbers
     -o,--output <out-jar-file>      output .jar file, default is $current_dir/[jar-name]-jasmin2jar.jar'''
        jasmin2jar = sep.join([tool_path, 'jasmin2jar.sh'])
        action_list.append(Action('jasmin2jar', getStrStype1('Jasmin2jar')+getStrStype2(' -- Assemble .j files to .class file'), jasmin2jar_info, jasmin2jar))

        smali_info = '''
smali -- assembles a set of smali files into a dex file
usage: smali [options] [--] [<smali-file>|folder]*
options:
     --                             read smali from stdin
     -a,--api-level <API_LEVEL>     [not impl] The numeric api-level of the file to generate, e.g. 14 for 
                                    ICS. If not specified, it defaults to 14 (ICS).
     -o,--output <FILE>             the name of the dex file that will be written. The default is out.dex
     -v,--version                   prints the version then exits
     -x,--allow-odex-instructions   [not impl] allow odex instructions to be compiled into the dex file. 
                                    Only a few instructions are supported - the ones that can exist in a 
                                    dead code path and not cause dalvik to reject the clas'''
        smali = sep.join([tool_path, 'smali.sh'])
        action_list.append(Action('smali', getStrStype1('Smali')+getStrStype2(' -- assembles a set of smali files into a dex file'), smali_info, smali))


        std_apk_info='''
std-zip -- clean up apk to standard zip
usage: std-zip [options] <zip>
options:
    -o,--output <out>   The output file'''
        std_apk = sep.join([tool_path, 'std-apk.sh'])
        action_list.append(Action('std_apk', getStrStype1('Std-apk')+getStrStype2('-- clean up apk to standard zip'),std_apk_info, std_apk))

        oat2dex_info='''
oat2dex -- get your fantasy
usage: oat2dex options [<file>]
options:
     boot <boot.oat>                    Get dex from boot.oat
     <oat-file> <boot-class-folder>     Get dex from  app oat
     odex <oat-file>                    Get raw odex from oat
     smali <oat/odex file>              Get raw odex smali
     devfw                              Deodex framework'''
        oat2dex = sep.join([tool_path, 'oat2dex.sh'])
        action_list.append(Action('oat2dex', getStrStype1('Oat2dex')+getStrStype2(' -- get your fantasy'),oat2dex_info, oat2dex))
        merge_info='''
        合并所以的odex
        请讲android的system分区的所有文件拷贝到xhl/system_from_img目录中
        需要拷贝的主要文件和目录有build.prop，framework，priv-app，app以及其它含有apk的目录
        合并的德文郡放在xhl/system_to_img目录
        '''
        action_list.append(Action('odex_merge', getStrStype1('Xhl odex merge') + getStrStype2(' -- 合并所以的odex'), oat2dex_info, ''))

        action_list.append(Action('quit_out', getStrStype1('Quit out') + getStrStype2(' -- 退出'), '', ''))

        getPirntText = lambda name, index:''.join([Tool.COLOR_START, cls.COLOR_BG1 if index%2==0 else Tool.COLOR_BG2, '31m' if index%2==0 else '30m', name, ''])

        printText=''
        for item in action_list:
            index = action_list.index(item)+1
            index_str = ('0' if index < 10 else '') + str(index)
            printText = printText+getStrStype2(index_str+') ')+getPirntText(item.name, index)+'\n'

        os.system('stty erase ^H')

        #将zip文件夹转化为apk文件格式
        zipalign_file = sep.join(['.', 'out', 'host', 'linux-x86','bin','zipalign'])
        zipalign_file = zipalign_file if isfile(zipalign_file) else path.join(tool_path, 'bin', 'zipalign')
        zipalign = lambda from_apk, to_apk:  os.system(zipalign_file+ ' -v 4 ' + from_apk + ' ' + to_apk)
        #向apk中添加文件输出到指定路径
        def addFileToApk(from_zip, to_zip, filename, arcname):
            if not isdir(dirname(to_zip)):
                makedirs(dirname(to_zip))
            if zipfile.is_zipfile(from_zip):
                copyfile(from_zip, 'temp.apk')
                zipped = zipfile.ZipFile('temp.apk', mode='a')
                if arcname in zipped.namelist():
                    match= re.match(r'^([^\.|^\d]+)([\d]*)\.(.*)', arcname)
                    if match:
                        point = ('1' if len(match.group(2))==0 else str(int(match.group(2)+1)))+'.'
                        arcname = match.group(1)+point+match.group(3)
                    else:
                        arcname = str(len(arcname))+arcname
                zipped.write(filename, arcname)
                zipped.close()
                zipalign('temp.apk', to_zip)
                remove('temp.apk')
            else:
                copyfile(from_zip, to_zip)

        error_str=''
        while(True):
            print(printText)
            if len(error_str)>0:
                print(error_str)
                error_str=''
            choice = input(getStrStype2('请选择功能(1-'+str(len(action_list))+'):')+'\n')
            if choice.isdigit() and int(choice) <= len(action_list):
                index = int(choice)-1
                item = action_list[index]
                short_name = item.short_name
                name = item.name
                info = item.info
                action= item.action
                if 'quit_out' == short_name:
                    break
                elif 'odex_merge' != short_name:
                    option = input(getStrStype2(info)+'\n请输入参数,返回请输入(N/n):')
                    if option == 'N' or option == 'n':
                        continue
                    else:
                        args = option.split(' ')
                        exec_sh(action, args)
                else:
                    system_from_img = os.path.join(Tool.XHL_PATH,'system_from_img')
                    if not isdir(system_from_img):
                        makedirs(system_from_img)
                    option = input('请将system里的所有文件拷贝到'+system_from_img+'\n准备好后请按(Y/y)或者直接回车:')
                    getValues = lambda key, filename: [re.match(key + '[ |:|=]+(.*)', item).group(1).strip() for item in popen('grep ' + key + ' ' + filename).read().splitlines() if re.match(key + '[ |:|=]+(.*)', item)]
                    print_execute = lambda comm : not print(comm) and os.system(comm)
                    system_to_img = os.path.join(Tool.XHL_PATH,'system_to_img')
                    if not isdir(system_to_img):
                        makedirs(system_to_img)
                    if len(option) == 0 or option == 'Y' or option == 'y':
                        build_prop = path.join(system_from_img,BUILD_PROP)
                        from_framework_path = path.join(system_from_img,'framework')
                        to_framework_path = path.join(system_to_img,'framework')

                        if not isfile(build_prop):
                            print('没有找到文件'+build_prop)
                        #查找sdk版本
                        key_sdk = 'ro.build.version.sdk'
                        value_sdk = getValues(key_sdk, build_prop) if isfile(build_prop) else list()
                        if len(value_sdk)>0:
                            value_sdk = value_sdk[0]
                        else:
                            printStrStype1('没有在build.prop文件中找到'+key_sdk+'现在设置SDK版本'+key_sdk+'=23')
                            value_sdk = '23'
                        key_release='ro.build.version.release'
                        value_release = getValues(key_release, build_prop) if isfile(build_prop) else list()
                        if len(value_release)>0:
                            value_release = value_release[0]
                        else:
                            printStrStype1('没有在build.prop文件中找到'+key_release+'现在设置Android版本'+key_release+'=6.0')
                            value_release = '6.0'

                        printStrStype1('当前sdk版本'+value_sdk+'  Android版本'+value_release)
                        #合并framework里面的odex
                        if not isdir(from_framework_path):
                            printStrStype1('没有framework目录')
                        else:
                            #转framework里的ota与dex
                            oldCwd = os.getcwd()
                            #切换工作空间到system_to_img
                            if not isdir(to_framework_path):
                                makedirs(to_framework_path)
                            os.chdir(from_framework_path)
                            #所有的oat转odex
                            # Get dex from boot.oat: boot <boot.oat>
                            for parent, dirnames, filenames in os.walk(from_framework_path):
                                for filename in (sep.join([parent, filename]) for filename in filenames if filename.endswith('.oat')):
                                    exec_sh(oat2dex, ['boot', filename])
                            #odex <oat-file> Get raw odex from oat
                            for parent, dirnames, filenames in os.walk(system_from_img):
                                for filename in (sep.join([parent, filename]) for filename in filenames if filename.endswith('.odex')):
                                    exec_sh(oat2dex, ['odex', filename])
                            #合并jar
                            for parent, dirnames, filenames in os.walk(from_framework_path):
                                for filename in (sep.join([parent, filename]) for filename in filenames if filename.endswith('.jar') or filename.endswith('.apk')):
                                    to_framework_zip = path.join(to_framework_path, basename(filename))
                                    if filename.endswith('.apk'):
                                        print_execute('cp -r '+filename+' '+to_framework_zip)
                                    else:
                                        #获取文件名
                                        name = basename(filename)
                                        #获取dex的名字
                                        dex_name=name[0:name.rfind('.')]+'.dex'
                                        #查找当前目录有没有dex
                                        dexfiles = Tool.findFileFromEndSwith(os.getcwd(), dex_name)
                                        #查找framework目录有没有dex
                                        if len(dexfiles) == 0:
                                            dexfiles = Tool.findFileFromEndSwith(from_framework_path, dex_name)
                                        #将dex添加到jar文件中
                                        if len(dexfiles)>0:
                                            dexfile = dexfiles[0]
                                            addFileToApk(filename,to_framework_zip,dexfile, 'classes.dex')
                                        #保留apk和jar删除dex
                                        for dexfile in dexfiles:
                                            print_execute('rm -rf '+dexfile)
                            remove_paths = list()
                            for parent, dirnames, filenames in os.walk(from_framework_path):
                                if parend.endswith('dex') and len(listdir(parent)) and not parent in remove_paths:
                                    remove_paths.append(parent)
                            for remove_path in remove_paths:
                                os.system('rm -rf '+remove_path)

                            #合并apk odex
                            os.chdir(system_to_img)
                            if not isdir('workspace_apk'):
                                makedirs('workspace_apk')
                            current_cwd = path.join(os.getcwd(), 'workspace_apk')
                            os.chdir(current_cwd)
                            system_from_img_len = len(system_from_img)
                            for parent, dirnames, filenames in os.walk(system_from_img):
                                for from_app_zip in (sep.join([parent, filename]) for filename in filenames if not parent.startswith(from_framework_path) and filename.endswith('.apk')):
                                    to_app_zip = path.join(system_to_img, from_app_zip[system_from_img_len+1:])
                                    #清理
                                    os.system('rm -rf *')
                                    #查找odex
                                    odexfiles = Tool.findFileFromEndSwith(dirname(from_app_zip), '.odex')
                                    if len(odexfiles)>0:
                                        for odexfile in odexfiles:
                                            exec_sh(oat2dex, ['odex', odexfile])
                                    #查找dex加入到
                                    dexfiles = Tool.findFileFromEndSwith(os.getcwd(), '.dex')
                                    if len(dexfiles)>0:
                                        for dexfile in dexfiles:
                                            addFileToApk(from_app_zip, to_app_zip, dexfile, 'classes.dex')
                                            remove(dexfile)

                            os.chdir(oldCwd)
                            os.system('rm -rf '+current_cwd)
            else:
                error_str=getStrStype1('请输入正确的数字')

    @classmethod
    def chgvalueFromUser(cls):
        '''
        根据提示完成制定目录下制定文件中的key=value修改
        '''
        os.system('stty erase ^H')
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        weak_name = None
        key = None
        value = None
        while weak_name == None or key == None or value == None:
            input_words = input(getStrStype2('请输入 ')+getStrStype1('文件名 key value')+getStrStype2('(可以只输入文件名的一部分)\n\t例如：修改customer.prop里面的DefaultVersion值为8.0可以输入')
                              +getStrStype1('customer DefaultVersion 8.0')+'\n').strip().split(' ')
            if len(input_words)==3:
                weak_name = input_words[0]
                key = input_words[1]
                value = input_words[2]
                break
            else:
                print(getStrStype1('########################输入不规范???????????'))
                continue

        list_files = list()
        list_dict = dict()
        def findFile(patch_name, key, list_files = list(), list_dict = dict()):
            for parent, dirnames, filenames in os.walk(patch_name):
                for filename in (filename for filename in filenames if weak_name in filename):
                    filepath = os.path.sep.join([parent, filename])
                    for line in popen('grep ' + key + ' ' + filepath).read().splitlines():
                        match = re.match(r'' + key + '([ |:|=]+)(.*)', line)
                        if match:
                            if not filepath in list_files:
                                list_files.append(filepath)
                                list_dict[filepath] = list()
                            list_dict[filepath].append(match.group(2))

        findFile(sep.join(['xhl', 'driver']), key, list_files, list_dict)
        findFile(sep.join(['xhl', 'merge']), key, list_files, list_dict)
        if len(list_files) == 0:
            print(getStrStype2('没有找到文件，没有什么可做的'))
            return
        print_text = ''
        for find_file in list_files:
            index = list_files.index(find_file)
            print_text = print_text +str(index+1)+') '+getStrStype2(find_file)+'\n'
            for value_str in list_dict[find_file]:
                print_text = print_text+' '+getStrStype1(key+'='+value_str)+' '
            print_text = print_text + '\n'
        #用户选择
        while True:
            print(print_text)
            select_strs = input(getStrStype2('请输入要修改文件的序号')+'\n').split(' ')
            select = list()
            has_err = False
            for item in select_strs:
                if item.isdigit() and int(item) <= len(list_files):
                    select = item
                else:
                    has_err = True
                    print(getStrStype1(item+' 输入不规范'))

            if has_err:
                continue
            print(getStrStype2('修改的文件列表：'))
            for item in select:
                print(getStrStype2(list_files[int(item)-1]))
            input_str = input(getStrStype2('重新选择(N/n),确定选择(Y/y)?'))
            if input_str == 'Y' or input_str == 'y':
                for item in select:
                    Tool.chgvalue(list_files[int(item)-1], key, value)
            else:
                continue
            input_str = input(getStrStype2('不提交修改到SVN(N/n),提交修改到SVN(Y/y)?'))
            if input_str == 'Y' or input_str == 'y':
                os.system('svn ci -m "修改文件'+' '.join(list_files)+' key='+key+'value='+value+'" '+' '.join(list_files))
            input_str = input(getStrStype2('退出(Q/q),继续修改(Y/y)?'))
            if input_str == 'Q' or input_str == 'q':
                print(getStrStype2('修改完成'))
                return
            else:
                Tool.chgvalueFromUser()

    @classmethod
    def buildLogo(cls, logo_path, bmp_to_raw='', zpipe='', mkimage='', img_hdr_logo_cfg=''):
        '''
        快速生成logo.bin到xhl/logo中 ，如果有修改bmp文件，可以直接放在xhl/logo替换
        :param logo_path: logo_path的路径
        :param bmp_to_raw: bmp_to_raw的路径
        :param zpipe: zpipe的路径
        :param mkimage: mkimage的路径
        :param img_hdr_logo_cfg: img_hdr_logo_cfg的路径
        '''
        os.system('stty erase ^H')
        #构建高亮字符串函数
        def getPrintText(bg_color, name, array):
            printText=''.join([cls.COLOR_START, bg_color ,'30m',name,':  \n'])
            for i in range(1, len(array)+1):
                printText = ''.join([printText,  cls.COLOR_START, '31m ' , str(i), '--', array[i - 1],'\n' if i%4==0 else '    '])
            printText = ''.join([printText, cls.COLOR_END])
            return printText
        mklogo_tool_path = sep.join([dirname(abspath(__file__)),'mklogo','tool'])
        os.environ['PATH'] = mklogo_tool_path+ ':' + os.environ['PATH']
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        printStrStype2('logo路径：'+logo_path)
        rules_file = sep.join([logo_path, 'rules.mk'])
        if not isfile(rules_file):
            printStrStype1('没有找到规则文件'+rules_file)
        logo_dirs = sorted([path for path in listdir(logo_path) if isdir(sep.join([logo_path, path]))])
        screen_size = None
        while(not screen_size):
            choice = input(getPrintText(cls.COLOR_BG1, '选择屏幕大小(输入数字)', logo_dirs)+'\n')
            if choice in logo_dirs:
                screen_size = choice
            elif(choice.isdigit() and int(choice) <= len(logo_dirs)):
                screen_size = logo_dirs[int(choice)-1]
            else:
                printStrStype1('输入错误\n')

        work_path = sep.join(['xhl', 'logo'])
        if not isdir(work_path):
            os.system('mkdir ' + work_path)

        bmps = [bmp for bmp in listdir(work_path) if bmp.endswith('bmp')]
        current_logo_path = sep.join([logo_path, screen_size])
        rules =open(rules_file, mode='r')
        raws = list()
        bitmaps = list()
        err_files = list()
        put_uboot_raw = False
        put_kernel_raw = False
        for line in rules.readlines():
            if '_uboot.raw' in line:
                put_uboot_raw = True
            if '_kernel.raw' in line:
                put_kernel_raw = True
            if put_uboot_raw and put_kernel_raw and len(line.strip())>0 and not '.raw' in line:
                break
            if put_uboot_raw and '.raw' in line:
                #$(BOOT_LOGO_DIR)/$(BASE_LOGO)/$(BASE_LOGO)_bat_10_07.raw \
                line = line.strip()
                line = line[line.rindex(')')+1:]    #_bat_10_07.raw
                word = line[0:line.index('.raw')]   #_bat_10_07
                if screen_size+word+'.bmp' in bmps:         #hd640_bat_10_07.bmp
                    bitmaps.append(sep.join([work_path, screen_size+word+'.bmp']))
                elif word[1:]+'.bmp' in bmps:         #bat_10_07.bmp
                    bitmaps.append(sep.join([work_path, word[1:]+'.bmp']))
                else:
                    bmp1 = sep.join([current_logo_path, screen_size+word+'.bmp'])
                    bmp2 = sep.join([current_logo_path, screen_size+word+'.BMP'])
                    if isfile(bmp1):
                        bitmaps.append(bmp1)
                    elif isfile(bmp2):
                        bitmaps.append(bmp2)
                    else:
                        err_files.append(bmp1)
        if len(err_files) > 0:
            for err in err_files:
                printStrStype1(err)
            if 'y' != input(getStrStype1('以上文件为找到 如果继续请按y:')+'\n'):
                exit(1)

        for bitmap in bitmaps:
            index = bitmaps.index(bitmap)
            raw = sep.join([work_path, 'temp'+str(index)+'.raw'])
            raws.append(raw)
            if isfile(bmp_to_raw) and os.access(bmp_to_raw, os.X_OK):
                print_and_execute(' '.join([bmp_to_raw, raw, bitmap]))
            else:
                print_and_execute(' '.join(['bmp_to_raw', raw, bitmap]))
        screen_size_raw = sep.join([work_path, screen_size+'.raw'])
        if isfile(zpipe) and os.access(zpipe, os.X_OK):
            print_and_execute(' '.join([zpipe, '-l', '9', screen_size_raw, ' '.join(raws)]))
        else:
            print_and_execute(' '.join(['zpipe', '-l', '9', screen_size_raw, ' '.join(raws)]))
        print_and_execute(' '.join(['rm', '-rf', ' '.join(raws)]))
        if not isfile(img_hdr_logo_cfg):
            img_hdr_logo_cfg = sep.join([mklogo_tool_path, 'img_hdr_logo.cfg'])
        logo_bin = sep.join([work_path, screen_size+'_logo.bin'])
        if isfile(mkimage) and os.access(mkimage, os.X_OK):
            print_and_execute(' '.join([mkimage, screen_size_raw, img_hdr_logo_cfg, '>', logo_bin]))
        else:
            print_and_execute(' '.join(['mkimage', screen_size_raw, img_hdr_logo_cfg, '>', logo_bin]))
        print_and_execute('rm -rf '+screen_size_raw)
        if isfile(logo_bin) and getsize(logo_bin)>0:
            printStrStype2('file '+logo_bin+' ok')
            printStrStype2('conversion finished')
        else:
            printStrStype1('file '+logo_bin+' err')
            printStrStype1('conversion finished')

    @classmethod
    def stringToInt(cls, param='0'):
        '''string转换为10进制正数，转换失败返回-1
        :param param: 需要转换的字符串
        :return: 返回的10进制正数
        '''
        param = param.lower()
        if re.match('^0o[0-7]+$', param):
            return int(param[2:], 8)
        if re.match('^-0o[0-7]+$', param):
            return (-1*int(param[3:], 8))%(0xffffffff+1)
        elif re.match('^0x[\d|a-f]+$', param):
            return int(param[2:], 16)
        elif re.match('^-0x[\d|a-f]+$', param):
            return (-1*int(param[3:], 16))%(0xffffffff+1)
        elif re.match('^[\d]+$', param):
            return int(param)
        elif re.match('^-[\d]+$', param):
            return (-1*int(param[1:]))%(0xffffffff+1)
        else:
            return -1;

    @classmethod
    def computerFlag(cls):
        '''
        反编译时候使用该方法获取flag对应的名称
        '''
        getStrStype1 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG1 + '31m' + strings + Tool.COLOR_END
        printStrStype1 = lambda strings: print(getStrStype1(strings))
        getStrStype2 = lambda strings: Tool.COLOR_START + Tool.COLOR_BG2 + '30m' + strings + Tool.COLOR_END
        printStrStype2 = lambda strings: print(getStrStype2(strings))
        example = '''使用方法[type value]\n\t[参数编号 参数]  (参数支持正负八进制，正负十进制，正负十六进制) \n例如:\n\tfor example (e.g.1)  
            0 0x228 #解析WindowManager.LayoutParams的Flag=0x228
            -->0x8 | 0x20 | 0x200 = 0x228(552)
            -->WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS'''
        print(getStrStype1(example))

        computeMethods = {
            0:cls.computeLayoutParams,               #LayoutParams = 0
            1:cls.computeLayoutParamsPrivate, #LayoutParamsPrivate = 1
            2: cls.computeLayoutParamsType,      #LayoutParamsType = 2
            3:cls.computeGravity,                         #Gravity = 3
            4:cls.computeIntentDefault,             #IntentDefault = 4
            5:cls.computeIntentReceiver,           #IntentReceiver = 5
            6:cls.computeAccessFlags,                 #AccessFlags = 6
            7:cls.computeSystemUiVisibility,   #SystemUiVisibility = 7
            8:cls.computeSystemBarVisibility,  #SystemUiVisibility = 8
        }

        cleassNamess = {
            0: 'WindowManager.LayoutParams(Flag)',                   # LayoutParams = 0
            1: 'WindowManager.LayoutParams(PrivateFlag)',     # LayoutParamsPrivate = 1
            2: 'WindowManager.LayoutParams(Type)',               # LayoutParamsType = 2
            3: 'Gravity',                                                 # Gravity = 3
            4: 'Intent(IntentDefault)',                             # IntentDefault = 4
            5: 'Intent(IntentReceiver)',                           # IntentReceiver = 5
            6: 'AccessFlags',                                         # AccessFlags = 6
            7: 'View(SystemUiVisibility)',                     # SystemUiVisibility = 7
            8: 'View(SystemBarVisibility)',                    # SystemUiVisibility = 8
        }
        COUNT = len(cleassNamess)

        paramsStr = '参数编号:\n'
        for key,value in cleassNamess.items():
            paramsStr += '\t'+str(key)+') '+value+'\n'
        paramsStr += '\t'+str(COUNT)+') Quit'
        os.system('stty erase ^H')
        hint=''

        while(True):
            match = re.match('^([\d]+)[ ]+([\d|\-|a-f|x|o]+)$',(input(getStrStype2(paramsStr)+(('\n'+getStrStype1(hint)) if hint else '')+'\n请输入[type value]:')).strip())
            hint = -1
            if match:
                select = int(match.group(1))
                param = cls.stringToInt(match.group(2))
                if int(select) < COUNT and param >= 0:
                    flags = computeMethods[select](param)
                    hint = cleassNamess[select]+'计算Flag=' + match.group(2)+'('+hex(param) + '):\n' + flags
                elif int(select) == COUNT:
                    printStrStype1('退出')
                    exit(0)

            if hint == -1:
                hint=getStrStype1('输入的参数有误，使用方法[参数编号 参数]')

    @classmethod
    def getFieldStr(cls, param=0, flags=dict(), className=None):
        '''计算param在flags中的key有哪些
        :param param: 需要解析的flag的或值
        :param flags: 类中所有的flag
        :param className: 类名，最终打印使用
        '''
        fields = [key for (key, value) in flags.items() if key & param == key]
        or_num = 0
        for field in fields:
            or_num |= field
        field_str = '  ' + ('|\n  ' if className else ' | ').join(map(lambda x: '.'.join([className, flags[x]]) if className else flags[x], fields))
        if or_num == param:
            field_int = str(param) + ' = ' + hex(param) + ' = ' + '|'.join(map(lambda x: hex(x), fields))
            return field_int + '\n' + field_str
        elif len(fields)>0:
            field_int = str(param) + ' = ' + hex(param) + ' != ' + '|'.join(map(lambda x: hex(x), fields))
            return 'err!未找到合适的参数,只能提供如下信息\n' + field_int + '\nerr 提供参数能够兼容下面参数:' + field_str+'\nerr!未找到合适的参数,只能提供如上信息\n'
        else:
            return 'err!未找到合适的参数'

    @classmethod
    def computeLayoutParams(cls, param=0):
        '''解析LayoutParams的flag
        :param param: 需要解析的flag数值
        '''
        flags = {
            0x00000001:'FLAG_ALLOW_LOCK_WHILE_SCREEN_ON',
            0x00000002:'FLAG_DIM_BEHIND',
            0x00000008:'FLAG_NOT_FOCUSABLE',
            0x00000010:'FLAG_NOT_TOUCHABLE',
            0x00000020:'FLAG_NOT_TOUCH_MODAL',
            0x00000040:'FLAG_TOUCHABLE_WHEN_WAKING',
            0x00000080:'FLAG_KEEP_SCREEN_ON',
            0x00000100:'FLAG_LAYOUT_IN_SCREEN',
            0x00000200:'FLAG_LAYOUT_NO_LIMITS',
            0x00000400:'FLAG_FULLSCREEN',
            0x00000800:'FLAG_FORCE_NOT_FULLSCREEN',
            0x00001000:'FLAG_DITHER',
            0x00002000:'FLAG_SECURE',
            0x00004000:'FLAG_SCALED',
            0x00008000:'FLAG_IGNORE_CHEEK_PRESSES',
            0x00010000:'FLAG_LAYOUT_INSET_DECOR',
            0x00020000:'FLAG_ALT_FOCUSABLE_IM',
            0x00040000:'FLAG_WATCH_OUTSIDE_TOUCH',
            0x00080000:'FLAG_SHOW_WHEN_LOCKED',
            0x00100000:'FLAG_SHOW_WALLPAPER',
            0x00200000:'FLAG_TURN_SCREEN_ON',
            0x00400000:'FLAG_DISMISS_KEYGUARD',
            0x00800000:'FLAG_SPLIT_TOUCH',
            0x01000000:'FLAG_HARDWARE_ACCELERATED',
            0x02000000:'FLAG_LAYOUT_IN_OVERSCAN',
            0x04000000:'FLAG_TRANSLUCENT_STATUS',
            0x08000000:'FLAG_TRANSLUCENT_NAVIGATION',
            0x10000000:'FLAG_LOCAL_FOCUS_MODE',
            0x20000000:'FLAG_SLIPPERY',
            0x40000000:'FLAG_LAYOUT_ATTACHED_IN_DECOR',
            0x80000000:'FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS',
        }
        className='WindowManager.LayoutParams'
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeLayoutParamsPrivate(cls, param=0):
        '''解析LayoutParams的private_flag
        :param param: 需要解析的flag数值
        '''
        flags = {
            0x00000001:'PRIVATE_FLAG_FAKE_HARDWARE_ACCELERATED',
            0x00000002:'PRIVATE_FLAG_FORCE_HARDWARE_ACCELERATED',
            0x00000004:'PRIVATE_FLAG_WANTS_OFFSET_NOTIFICATIONS',
            0x00000010:'PRIVATE_FLAG_SHOW_FOR_ALL_USERS',
            0x00000040:'PRIVATE_FLAG_NO_MOVE_ANIMATION',
            0x00000080:'PRIVATE_FLAG_COMPATIBLE_WINDOW',
            0x00000100:'PRIVATE_FLAG_SYSTEM_ERROR',
            0x00000200:'PRIVATE_FLAG_INHERIT_TRANSLUCENT_DECOR',
            0x00000400:'PRIVATE_FLAG_KEYGUARD',
            0x00000800:'PRIVATE_FLAG_DISABLE_WALLPAPER_TOUCH_EVENTS',
            0x00001000:'PRIVATE_FLAG_FORCE_STATUS_BAR_VISIBLE_TRANSPARENT',
            0x00002000:'PRIVATE_FLAG_PRESERVE_GEOMETRY',
            0x00004000:'PRIVATE_FLAG_FORCE_DECOR_VIEW_VISIBILITY',
            0x00008000:'PRIVATE_FLAG_WILL_NOT_REPLACE_ON_RELAUNCH',
            0x00010000:'PRIVATE_FLAG_LAYOUT_CHILD_WINDOW_IN_PARENT_FRAME',
            0x00020000:'PRIVATE_FLAG_FORCE_DRAW_STATUS_BAR_BACKGROUND',
            0x00040000:'PRIVATE_FLAG_SUSTAINED_PERFORMANCE_MODE',
            0x00080000:'PRIVATE_FLAG_HIDE_NON_SYSTEM_OVERLAY_WINDOWS',
            0x00100000:'PRIVATE_FLAG_IS_ROUNDED_CORNERS_OVERLAY',
            0x00200000:'PRIVATE_FLAG_ACQUIRES_SLEEP_TOKEN',
        }
        className='WindowManager.LayoutParams'
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeLayoutParamsType(cls, param=0):
        '''解析LayoutParams的type
        :param param: 需要解析的flag数值
        '''
        FIRST_APPLICATION_WINDOW = 1
        LAST_APPLICATION_WINDOW = 99
        FIRST_SUB_WINDOW = 1000
        LAST_SUB_WINDOW = 1999
        FIRST_SYSTEM_WINDOW = 2000
        LAST_SYSTEM_WINDOW = 2999
        flags = {
            FIRST_APPLICATION_WINDOW:'TYPE_BASE_APPLICATION',
            FIRST_APPLICATION_WINDOW+1:'TYPE_APPLICATION',
            FIRST_APPLICATION_WINDOW+2:'TYPE_APPLICATION_STARTING',
            FIRST_APPLICATION_WINDOW+3:'TYPE_DRAWN_APPLICATION',
            FIRST_SUB_WINDOW:'TYPE_APPLICATION_PANEL',
            FIRST_SUB_WINDOW + 1:'TYPE_APPLICATION_MEDIA',
            FIRST_SUB_WINDOW + 2:'TYPE_APPLICATION_SUB_PANEL',
            FIRST_SUB_WINDOW + 3:'TYPE_APPLICATION_ATTACHED_DIALOG',
            FIRST_SUB_WINDOW + 4:'TYPE_APPLICATION_MEDIA_OVERLAY',
            FIRST_SUB_WINDOW + 5:'TYPE_APPLICATION_ABOVE_SUB_PANEL',
            FIRST_SYSTEM_WINDOW:'TYPE_STATUS_BAR',
            FIRST_SYSTEM_WINDOW+1:'TYPE_SEARCH_BAR',
            FIRST_SYSTEM_WINDOW+2:'TYPE_PHONE',
            FIRST_SYSTEM_WINDOW+3:'TYPE_SYSTEM_ALERT',
            FIRST_SYSTEM_WINDOW+4:'TYPE_KEYGUARD',
            FIRST_SYSTEM_WINDOW+5:'TYPE_TOAST',
            FIRST_SYSTEM_WINDOW+6:'TYPE_SYSTEM_OVERLAY',
            FIRST_SYSTEM_WINDOW+7:'TYPE_PRIORITY_PHONE',
            FIRST_SYSTEM_WINDOW+8:'TYPE_SYSTEM_DIALOG',
            FIRST_SYSTEM_WINDOW+9:'TYPE_KEYGUARD_DIALOG',
            FIRST_SYSTEM_WINDOW+10:'TYPE_SYSTEM_ERROR',
            FIRST_SYSTEM_WINDOW+11:'TYPE_INPUT_METHOD',
            FIRST_SYSTEM_WINDOW+12:'TYPE_INPUT_METHOD_DIALOG',
            FIRST_SYSTEM_WINDOW+13:'TYPE_WALLPAPER',
            FIRST_SYSTEM_WINDOW+14:'TYPE_STATUS_BAR_PANEL',
            FIRST_SYSTEM_WINDOW+15:'TYPE_SECURE_SYSTEM_OVERLAY',
            FIRST_SYSTEM_WINDOW+16:'TYPE_DRAG',
            FIRST_SYSTEM_WINDOW+17:'TYPE_STATUS_BAR_SUB_PANEL',
            FIRST_SYSTEM_WINDOW+18:'TYPE_POINTER',
            FIRST_SYSTEM_WINDOW+19:'TYPE_NAVIGATION_BAR',
            FIRST_SYSTEM_WINDOW+20:'TYPE_VOLUME_OVERLAY',
            FIRST_SYSTEM_WINDOW+21:'TYPE_BOOT_PROGRESS',
            FIRST_SYSTEM_WINDOW+22:'TYPE_INPUT_CONSUMER',
            FIRST_SYSTEM_WINDOW+23:'TYPE_DREAM',
            FIRST_SYSTEM_WINDOW+24:'TYPE_NAVIGATION_BAR_PANEL',
            FIRST_SYSTEM_WINDOW+26:'TYPE_DISPLAY_OVERLAY',
            FIRST_SYSTEM_WINDOW+30:'TYPE_PRIVATE_PRESENTATION',
            FIRST_SYSTEM_WINDOW+31:'TYPE_VOICE_INTERACTION',
            FIRST_SYSTEM_WINDOW+32:'TYPE_ACCESSIBILITY_OVERLAY',
            FIRST_SYSTEM_WINDOW+33:'TYPE_VOICE_INTERACTION_STARTING',
            FIRST_SYSTEM_WINDOW+34:'TYPE_DOCK_DIVIDER',
            FIRST_SYSTEM_WINDOW+35:'TYPE_QS_DIALOG',
            FIRST_SYSTEM_WINDOW+36:'TYPE_SCREENSHOT',
            FIRST_SYSTEM_WINDOW+37:'TYPE_PRESENTATION',
            FIRST_SYSTEM_WINDOW+38:'TYPE_APPLICATION_OVERLAY',
            FIRST_SYSTEM_WINDOW+38:'TYPE_APPLICATION_OVERLAY',
        }
        className='WindowManager.LayoutParams'
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeGravity(cls, param=0):
        '''解析Gravity
        :param param: 需要解析的flag数值
        '''
        NO_GRAVITY = 0x0000
        AXIS_SPECIFIED = 0x0001
        AXIS_PULL_BEFORE = 0x0002
        AXIS_PULL_AFTER = 0x0004
        AXIS_CLIP = 0x0008
        AXIS_X_SHIFT = 0
        AXIS_Y_SHIFT = 4
        CENTER_VERTICAL = AXIS_SPECIFIED << AXIS_Y_SHIFT
        CENTER_HORIZONTAL = AXIS_SPECIFIED << AXIS_X_SHIFT
        flags = {
            (AXIS_PULL_BEFORE | AXIS_SPECIFIED) << AXIS_Y_SHIFT:'TOP',
            (AXIS_PULL_AFTER | AXIS_SPECIFIED) << AXIS_Y_SHIFT:'BOTTOM',
            (AXIS_PULL_BEFORE | AXIS_SPECIFIED) << AXIS_X_SHIFT:'LEFT',
            (AXIS_PULL_AFTER | AXIS_SPECIFIED) << AXIS_X_SHIFT:'RIGHT',
            CENTER_VERTICAL:'CENTER_VERTICAL',
            CENTER_HORIZONTAL:'CENTER_HORIZONTAL',
            CENTER_VERTICAL | CENTER_HORIZONTAL:'CENTER',
        }
        className='Gravity'
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeIntentDefault(cls, param=0):
        '''解析Intent的flag
        :param param: 需要解析的flag数值
        '''
        flags={
            0x00000001:'FLAG_GRANT_READ_URI_PERMISSION',
            0x00000002:'FLAG_GRANT_WRITE_URI_PERMISSION',
            0x00000004:'FLAG_FROM_BACKGROUND',
            0x00000008:'FLAG_DEBUG_LOG_RESOLUTION',
            0x00000010:'FLAG_EXCLUDE_STOPPED_PACKAGES',
            0x00000020:'FLAG_INCLUDE_STOPPED_PACKAGES',
            0x00000040:'FLAG_GRANT_PERSISTABLE_URI_PERMISSION',
            0x00000080:'FLAG_GRANT_PREFIX_URI_PERMISSION',
            0x00000100:'FLAG_DEBUG_TRIAGED_MISSING',
            0x00000200:'FLAG_IGNORE_EPHEMERAL',
            0x00001000:'FLAG_ACTIVITY_LAUNCH_ADJACENT',
            0x00002000:'FLAG_ACTIVITY_RETAIN_IN_RECENTS',
            0X00004000:'FLAG_ACTIVITY_TASK_ON_HOME',
            0X00008000:'FLAG_ACTIVITY_CLEAR_TASK',
            0X00010000:'FLAG_ACTIVITY_NO_ANIMATION',
            0X00020000:'FLAG_ACTIVITY_REORDER_TO_FRONT',
            0x00040000:'FLAG_ACTIVITY_NO_USER_ACTION',
            0x00080000:'FLAG_ACTIVITY_CLEAR_WHEN_TASK_RESET',
            #0x00080000:'FLAG_ACTIVITY_NEW_DOCUMENT',
            0x00100000:'FLAG_ACTIVITY_LAUNCHED_FROM_HISTORY',
            0x00200000:'FLAG_ACTIVITY_RESET_TASK_IF_NEEDED',
            0x00400000:'FLAG_ACTIVITY_BROUGHT_TO_FRONT',
            0x00800000:'FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS',
            0x01000000:'FLAG_ACTIVITY_PREVIOUS_IS_TOP',
            0x02000000:'FLAG_ACTIVITY_FORWARD_RESULT',
            0x04000000:'FLAG_ACTIVITY_CLEAR_TOP',
            0x08000000:'FLAG_ACTIVITY_MULTIPLE_TASK',
            0x40000000:'FLAG_ACTIVITY_NO_HISTORY',
            0x20000000:'FLAG_ACTIVITY_SINGLE_TOP',
            0x10000000:'FLAG_ACTIVITY_NEW_TASK',
        }
        className='Intent'
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeIntentReceiver(cls, param=0):
        '''解析Intent 中Receiver的flag
        :param param: 需要解析的flag数值
        '''
        flags = {
            0x00200000:'FLAG_RECEIVER_VISIBLE_TO_INSTANT_APPS',
            0x00400000:'FLAG_RECEIVER_FROM_SHELL',
            0x00800000:'FLAG_RECEIVER_EXCLUDE_BACKGROUND',
            0x01000000:'FLAG_RECEIVER_INCLUDE_BACKGROUND',
            0x02000000:'FLAG_RECEIVER_BOOT_UPGRADE',
            0x04000000:'FLAG_RECEIVER_REGISTERED_ONLY_BEFORE_BOOT',
            0x08000000:'FLAG_RECEIVER_NO_ABORT',
            0x10000000:'FLAG_RECEIVER_FOREGROUND',
            0x40000000:'FLAG_RECEIVER_REGISTERED_ONLY',
            0x20000000:'FLAG_RECEIVER_REPLACE_PENDING',
        }
        className='Intent'
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeAccessFlags(cls, param=0):
        '''解析AccessFlags
        :param param: 需要解析的flag数值
        '''
        flags = {
            0x00000001:'public',
            0x00000002:'private',
            0x00000004:'protected',
            0x00000008:'static',
            0x00000010:'final',
            0x00000020:'synchronized',
            0x00000040:'volatile',
            0x00000080:'transient',
            0x00000100:'native',
            0x00000200:'interface',
            0x00000400:'abstract',
            0x00000800:'strictfp',
            0x00001000:'synthetic',
            0x00002000:'annotated',
            0x00004000:'menu',
            0x00010000:'constructor',
            0x00020000:'declared-synchronized',
        }
        className=None
        return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeSystemUiVisibility(cls, param=0):
        '''解析ystemUiVisibility
        :param param: 需要解析的flag数值
        '''
        SYSTEM_UI_FLAG_VISIBLE = 0x00000000
        flags = {
            0x00000001:'SYSTEM_UI_FLAG_LOW_PROFILE',
            0x00000002:'SYSTEM_UI_FLAG_HIDE_NAVIGATION',
            0x00000004:'SYSTEM_UI_FLAG_FULLSCREEN',
            0x00000010:'SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR',
            0x00000100:'SYSTEM_UI_FLAG_LAYOUT_STABLE',
            0x00000200:'SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION',
            0x00000400:'SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN',
            0x00000800:'SYSTEM_UI_FLAG_IMMERSIVE',
            0x00001000:'SYSTEM_UI_FLAG_IMMERSIVE_STICKY',
            0x00002000:'SYSTEM_UI_FLAG_LIGHT_STATUS_BAR',
            0x00004000:'SYSTEM_UI_RESERVED_LEGACY1',
            0x00010000:'SYSTEM_UI_RESERVED_LEGACY2',
        }
        className='View'
        if param == SYSTEM_UI_FLAG_VISIBLE:
            return '.'.join([className,'SYSTEM_UI_FLAG_VISIBLE'])
        else :
            return cls.getFieldStr(param, flags, className)

    @classmethod
    def computeSystemBarVisibility(cls, param=0):
        '''解析SystemBarVisibility
        :param param: 需要解析的flag数值
        '''
        STATUS_BAR_VISIBLE = 0x00000000
        flags = {
            0x00000001:'STATUS_BAR_HIDDEN',
            0x00000008:'STATUS_BAR_TRANSPARENT',
            0x00008000:'NAVIGATION_BAR_TRANSPARENT',
            0x00010000:'STATUS_BAR_DISABLE_EXPAND',
            0x00020000:'STATUS_BAR_DISABLE_NOTIFICATION_ICONS',
            0x00040000:'STATUS_BAR_DISABLE_NOTIFICATION_ALERTS',
            0x00080000:'STATUS_BAR_DISABLE_NOTIFICATION_TICKER',
            0x00100000:'STATUS_BAR_DISABLE_SYSTEM_INFO',
            0x00200000:'STATUS_BAR_DISABLE_HOME',
            0x00400000:'STATUS_BAR_DISABLE_BACK',
            0x00800000:'STATUS_BAR_DISABLE_CLOCK',
            0x01000000:'STATUS_BAR_DISABLE_RECENT',
            0x02000000:'STATUS_BAR_DISABLE_SEARCH',
            0x04000000:'STATUS_BAR_TRANSIENT',
            0x08000000:'NAVIGATION_BAR_TRANSIENT',
            0x10000000:'STATUS_BAR_UNHIDE',
            0x20000000:'NAVIGATION_BAR_UNHIDE',
            0x40000000:'STATUS_BAR_TRANSLUCENT',
            0x80000000:'NAVIGATION_BAR_TRANSLUCENT',
        }
        className='View'
        if param == STATUS_BAR_VISIBLE:
            return '.'.join([className,'STATUS_BAR_VISIBLE'])
        else :
            return cls.getFieldStr(param, flags, className)

    '''
    <?xml version="1.0" encoding="utf-8"?>
    <resources>
        <public type="attr" name="title" id="0x7f010000" />
        <public type="drawable" name="best_shot_hl" id="0x7f02001d" />
        <public type="mipmap" name="ic_launcher_camera" id="0x7f030000" />
        <public type="layout" name="bokeh_camera_preview_layout" id="0x7f040002" />
        <public type="anim" name="activity_close_out_anim_0" id="0x7f050000" />
        <public type="xml" name="camera_preferences" id="0x7f060000" />
        <public type="raw" name="goofy_face" id="0x7f070004" />
        <public type="array" name="camera_id_entryvalues" id="0x7f080000" />
        <public type="style" name="SettingItemSubTitle" id="0x7f090005" />
        <public type="color" name="popup_background" id="0x7f0a0001" />
        <public type="dimen" name="screen_on_margin_right" id="0x7f0b0000" />
        <public type="bool" name="config_simulation_focus" id="0x7f0c0000" />
        <public type="string" name="gy_accessibility_switch_to_vdetect" id="0x7f0d0000" />
        <public type="id" name="camera_root" id="0x7f0e0007" />
    </resources>
    '''
    @classmethod
    def parsePulbicFiles(cls, srcs=['public.xml']):
        '''解析public.xml文件数组
        :param srcs: 所有的public.xml的集合
        :return: 解析出来的字典
        '''
        import xml.dom.minidom as xmldom
        ids = dict()
        for file in srcs:
            if not isfile(file):
                return
            #得到文档对象
            domObj = xmldom.parse(file)
            #得到元素对象
            element = domObj.documentElement
            publicNodes = element.getElementsByTagName('public')
            for item in [item for item in publicNodes if item.hasAttribute('type') and item.hasAttribute('name') and item.hasAttribute('id')]:
                name = '.'.join(['R', item.getAttribute('type'), item.getAttribute('name')])
                id = item.getAttribute('id')
                ids[id] = name
                ids[cls.stringToInt(id)] = name

        return ids

    @classmethod
    def checkFileCode(cls, filename):
        '''检查该文件的字符编码 避免读取字符串报错
        :param filename: 文件路径
        :return: 字符编码格式
        '''
        import codecs
        for encode in ['utf-8','gb2312','gb18030','gbk','ISO-8859-2','Error']:
            try:
                f = codecs.open(filename, mode='r', encoding=encode)
                u = f.read()
                f.close()
                return encode
            except:
                if encode=='Error':
                    return None

    @classmethod
    def replaceLine(cls, line, ids):
        '''替换一行中的id，如果一行中有多个id会使用递归调用
        :param line: java中的一行
        :param ids: 含有10进制和16进制的id：R.type.id的字典
        '''
        pattern = '.*[^\d|^-]([-]?[\d]{9,10}|[-]?0[x|X][\d|a-f|A-F]{7,8})[^\d]?.*'
        match = re.match(pattern, line)
        if match and cls.stringToInt(match.group(1)) in ids:
            id_str = match.group(1)
            id_int = cls.stringToInt(id_str)
            print('\t'+id_str+'==>'+ids[id_int])
            if 'rid_count' in ids.keys():
                ids['rid_count'] += 1;
            else:
                ids['rid_count'] = 1;
            return cls.replaceLine(line.replace(id_str,ids[id_int]), ids)
        return line

    @classmethod
    def showAppList(cls):
        xhl_mm = 'xhl/script/xhl_mm.ini'
        items = list()
        if isfile('xhl/script/xhl_mm.ini'):
            with open(xhl_mm, encoding=Tool.checkFileCode(xhl_mm)) as mmFile:
                for line in mmFile.readlines():
                    math =  re.match('([1-9|_|-|a-z|A-Z]+) ?= ?.*',line)
                    if math:
                        items.append(math.group(1).lower())
        for file in listdir('.'):
            if file != '.' or file != '..':
                items.append(file)
        print(' '.join(items))

    @classmethod
    def select(cls):
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        os.system('stty erase ^H')
        def chgvalue(key,value):
            file = abspath(__file__)
            encoding = Tool.checkFileCode(file)
            lines = list()
            for line in open(file, mode='r', encoding=encoding).readlines():
                math = re.match('^([ ]*'+key+'[ ]?=[ ]?)([^ ]+.*)', line)
                if math:
                    line = math.group(1)+value+'\n'
                    printStrStype1('改变：'+line.strip())
                lines.append(line)
            with open(file, mode='w', encoding=encoding) as tool:
                tool.writelines(lines)

        printStrStype2('修改脚本默认选项')
        print(getStrStype1('1.') + getStrStype2('mm 生成的install.bat脚本为自动push'))
        print(getStrStype1('2.') + getStrStype2('mm 生成的install.bat脚本为手动push'))
        print(getStrStype1('3.') + getStrStype2('ProjectConfig.mk MTK_BUILD_ROOT=yes'))
        print(getStrStype1('4.') + getStrStype2('ProjectConfig.mk MTK_BUILD_ROOT=no'))
        print(getStrStype1('5.') + getStrStype2('环境变量 xhl_eng=yes'))
        print(getStrStype1('6.') + getStrStype2('环境变量 xhl_eng=no'))

        select = input(getStrStype1('请选择:')+'\n')
        if '1' == select:
            chgvalue('AUTO_PUSH','True')
        elif '2' == select:
            chgvalue('AUTO_PUSH','False')
        elif '3' == select:
            chgvalue('MTK_BUILD_ROOT','\'yes\'')
        elif '4' == select:
            chgvalue('MTK_BUILD_ROOT','\'no\'')
        elif '5' == select:
            chgvalue('XHL_ENG','True')
        elif '6' == select:
            chgvalue('XHL_ENG','False')

    @classmethod
    def replaceId(cls, src='app'):
        ''' 使用工具反编译后所有的id为16紧致或者十进制 ，将这些id替换为R.type.id
        :param src: 带有public.xml和.java的文件的目录
        '''
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        os.system('stty erase ^H')
        if not isdir(src):
            src = input(getStrStype2('请输入app根目录或者放在工作目录的app文件下!\napp路径:'))
        if not isdir(src):
            printStrStype1('未找到目录' + src)
            exit(0)
        publicFiles=list()
        javaFiles=list()
        for parent, dirnames, filenames in os.walk(src):
            for file in [sep.join([parent, filename]) for filename in filenames if filename=='public.xml' or filename.endswith('.java')]:
                if file.endswith('.java'):
                    javaFiles.append(file)
                else:
                    publicFiles.append(file)
        if len(publicFiles)==0:
            printStrStype1('未找到(public.xml)文件')
            exit(0)
        #获取public.xml id对应的R
        ids = cls.parsePulbicFiles(publicFiles)

        for file in javaFiles:
            printStrStype2(file)
            #读取文件
            lines = list()
            encode = cls.checkFileCode(file)
            if encode:
                with open(file, mode='r', encoding=encode) as javaFile:
                    lines = javaFile.readlines()
                    javaFile.close()
            else:
                os.system('cat '+file+' > .java.temp')
                with open('.java.temp', mode='r', encoding=encode) as javaFile:
                    lines = javaFile.readlines()
                    javaFile.close()
                    remove('.java.temp')

            newLines = list()
            for line in lines:
                newLines.append(cls.replaceLine(line, ids))
            #替换id为R值
            with open('.temp', mode='w') as tempFile:
                tempFile.writelines(newLines)
                tempFile.close()
                os.system('cp .temp '+file)

        if 'rid_count' in ids.keys():
            printStrStype1('共计替换'+str(ids['rid_count'])+'个')

    @classmethod
    def git_help(cls, args=list()):
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        if args and args[0]=='help' and len(args)>1:
            os.system('git --help '+' '.join(args[1:]))
        else:
            help_str = '''
usage: git [--version] [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p|--paginate|--no-pager] [--no-replace-objects] [--bare]
           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
           [-c name=value] [--help]
           <command> [<args>]

最常用的 git 命令有：
   add        添加文件内容至索引
   bisect     通过二分查找定位引入 bug 的变更
   branch     列出、创建或删除分支
   checkout   检出一个分支或路径到工作区
   clone      克隆一个版本库到一个新目录
   commit     记录变更到版本库
   diff       显示提交之间、提交和工作区之间等的差异
   fetch      从另外一个版本库下载对象和引用
   grep       输出和模式匹配的行
   init       创建一个空的 Git 版本库或重新初始化一个已存在的版本库
   log        显示提交日志
   merge      合并两个或更多开发历史
   mv         移动或重命名一个文件、目录或符号链接
   pull       获取并整合另外的版本库或一个本地分支
   push       更新远程引用和相关的对象
   rebase     本地提交转移至更新后的上游分支中
   reset      重置当前HEAD到指定状态
   rm         从工作区和索引中删除文件
   show       显示各种类型的对象
   status     显示工作区状态
   tag        创建、列出、删除或校验一个GPG签名的 tag 对象
命令 'git help -a' 和 'git help -g' 显示可用的子命令和一些指南。参见
'git help <command>' 或 'git help <guide>' 来查看给定的子命令帮助或指南。

常用操作命令
     git config --global user.name "Your Name"              全局配置user.name
     git config --global user.email "email@example.com"     全局配置user.email
     git init     Git初始化管理的仓库
     git add      告诉Git，把文件添加到仓库(git add readme.txt）不使用add无法将修改提交
     git commit   告诉Git，把文件提交到仓库 (git commit -m "add 3 files.")
     git status   命令可以让我们时刻掌握仓库当前的状态
     git log --pretty=oneline 命令显示从最近到最远的提交日志(显示为单行)
     git log --graph   命令可以看到分支合并图
     git reset --hard HEAD    显示当前的版本号（哈希值）
     git reset --hard 3628164 回退版本到3628164开头的版本
     git reflog   用来记录你的每一次命令（忘记版本号时候可以来使用）
     git diff HEAD -- readme.txt 查看文件修改
     git branch   命令查看当前工作所在分支
     git branch -d dev 删除dev分支
     git branch -D dev 强行删除dev分支
     git checkout -- readme.txt 你改乱了工作区某个文件的内容，想直接丢弃工作区的修改
     git checkout -b dev 创建dev分支（命令加上 -b 参数表示创建并切换）
     git merge dev 合并分支dev到当前版本上（会将分支的版本log也添加上）
     git merge --no-ff -m "merge with no-ff" dev 合并分支dev到当前版本上
     git stash 把当前工作现场“储藏”起来，等以后恢复现场后继续工作
     git stash list 查看“储藏”起来的现场
     git stash apply 恢复现场
     git stash drop 删除现场
     git stash pop 恢复+删除现场
     add的文件在工作区的修改全部撤销
        1)git reset HEAD readme.txt
        2)git checkout -- readme.txt (命令中的 -- 很重要，没有 -- ，就变成了“切换到另一个分支”的命令)
     文件就从版本库中被删除了
        1)git rm readme.txt
        2)git commit -m "remove readme.txt"
     文件就从版本库中被删除后恢复
        1)git reset bf55454(回复到删除之前版本)
        2)git checkout -- readme.txt(还原文件readme.txt)
        3)git reset HEAD
        4)git add readme.txt
        5)git commit -m "reset readme.txt"
     创建 SSH KEY
        1)ssh-keygen -t rsa -C "303106251@qq.com"
            ~/.ssh目录下回生成id_rsa(私匙)和id_rsa.pub钥匙对
     git remote 要查看远程库的信息（git remote -v 显示更详细的信息）
     git remote add origin git@server-name:path/repo-name.git  添加本地库learngit到远程库origin
        例如 git remote add origin git@github.com:michaelliao/learngit.git
        git@server-name:path为github网站名可以改为物理地址+路径
     git push -u origin master （远程为空时候使用-u不会把本地分支传上去）将master上传到origin
     git push origin master 将master主分支上传到origin
     git clone git@github.com:michaelliao/gitskills.git 克隆远程库
        '''
            printStrStype2(help_str)

    @classmethod
    def git(cls, args=list()):
        print(args)
        if not args or args[0]=='help':
            Tool.git_help(args)
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print_and_execute = lambda comm_line: not print(comm_line) and os.system(comm_line)
        os.system('stty erase ^H')
        user_name = popen('git config user.name').read()
        user_email = popen('git config user.email').read()
        if not user_name:
            printStrStype1('git config --global user.name "Your Name"')
        if not user_email:
            printStrStype1('git config --global user.email "email@example.com"')
        if not user_name or not user_email:
            print('exit(0)')

    @classmethod
    def printHelp(cls, comm='tool'):
        '''
        打印帮助文档
        :param comm: 工具命令的名称
        '''
        getStrStype1 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG1 + '31m' +strings+ Tool.COLOR_END
        printStrStype1 = lambda strings : print(getStrStype1(strings))
        getStrStype2 = lambda strings : Tool.COLOR_START + Tool.COLOR_BG2 + '30m' +strings+ Tool.COLOR_END
        printStrStype2 = lambda strings : print(getStrStype2(strings))
        print(getStrStype2('make常用命令:\n(1)make -jx x表示cpu核心数\n(2)make snod 重新生成镜像\n(3)make cts编译CTS套机\n'
                           '(4)make clean-Mms清理Mms模块\n(5)make clean清理所有生成文件\n'
                           '(6)make installclean清楚out目录下版文件夹内容，基本上相当于make clean, '
                           '通常如果更改了一些数据文件(例如去掉)最好执行以下make installclean，否则残留文件会打包进去\n'
                           '(7)mm/mmm/mm -B 编译模块\n(8)make sdk生成sdk\n(9)make bootimage\n(10)make systemimage')+'\n')

        def checkModules(file, all_modules):
            if isfile(file):
                with open(file, mode='r', encoding=Tool.checkFileCode(file)) as tempFile:
                    for line in tempFile.readlines():
                        match = re.match('\.PHONY: ([\w]+)', line)
                        if match and not match.group(1) in all_modules:
                            all_modules.append(match.group(1))
        all_modules = list()
        checkModules(sep.join(['build','core','main.mk']),all_modules)
        checkModules(sep.join(['build','core','Makefile']),all_modules)
        if len(all_modules)>0:
            print(getStrStype1('make 编译模块包括')+'\n'+getStrStype2(' '.join(all_modules))+'\n')
        print(getStrStype2('1.')+getStrStype1(comm+' new [o|O]')+getStrStype2(' o或者O可选 不删除out目录'))
        printStrStype2('    选择项目并编译整并打包')
        print(getStrStype2('2.')+getStrStype1(comm+' svn_new'))
        printStrStype2('    删除本地项目然后全新下载代码编译')
        print(getStrStype2('3.')+getStrStype1(comm+' svn_mm'))
        printStrStype2('    恢复修改并更新目录然后mm')
        print(getStrStype2('4.')+getStrStype1(comm+' new_driver'))
        printStrStype2('    更改了屏和字库可以使用此方式快速new')
        print(getStrStype2('5.')+getStrStype1(comm+' mm'))
        printStrStype2('    快速编译整个项目并打包')
        print(getStrStype2('6.')+getStrStype1(comm+' mm mm 模块路径'))
        printStrStype2('    编译单个模块')
        print(getStrStype2('7.')+getStrStype1(comm+' mmm 模块路径'))
        printStrStype2('    编译单个模块,与mm相同但是编译前不touch编译模块目录下png文件')
        print(getStrStype2('8.')+getStrStype1(comm+' buildimage [-e]')+getStrStype2(' -e 可选， 扩展打包'))
        printStrStype2('    打包image生成到根目录Bin开头的文件夹中, 扩展build.prop')
        print(getStrStype2('9.')+getStrStype1(comm+' build_boot [mk]')+getStrStype2(' mk 可选（最终使用mk来生成bootimage）'))
        printStrStype2('    打包bootimage')
        print(getStrStype2('10.')+getStrStype1(comm+' driver'))
        printStrStype2('    驱动编译')
        print(getStrStype2('11.')+getStrStype1(comm+' driver_r'))
        printStrStype2('    快速驱动编译')
        print(getStrStype2('12.')+getStrStype1(comm+' svn_ci -p 路径 [-m 附加消息] [-i]')+getStrStype2(' -m 可选， -i 可选择，与用户交互'))
        printStrStype2('    提交代码')
        print(getStrStype2('13.')+getStrStype1(comm+' svn_restore' ))
        printStrStype2('    解决svn数据库错误(database disk image is malformed)')
        print(getStrStype2('14.')+getStrStype1(comm+' svn_revert 路径' ))
        printStrStype2('    还原现场')
        print(getStrStype2('15.')+getStrStype1(comm+' cp -f 拷贝文件列表集合的文件 [-o 输出的目录]')+getStrStype2(' -o 可选择,它默认目录在svn_copy')
                                +'\n   '+getStrStype1(comm + ' cp -p 还原拷贝文件目录(目录中包含copy_log.txt文件) [-o 输出的目录]') + getStrStype2(' -o 可选择,它默认目录在./'))
        printStrStype2('    拷贝文件')
        print(getStrStype2('16.')+getStrStype1(comm+' patch [-x]')+getStrStype2(' -x 可选择，只解压不打补丁'))
        printStrStype2('    打补丁功能')
        print(getStrStype2('17.')+getStrStype1(comm+' chgvalue'))
        printStrStype2('    修改xhl/merge中指定文件内容key=value功能')
        print(getStrStype2('18.')+getStrStype1(comm+' apktool'))
        printStrStype2('    apk工具')
        print(getStrStype2('19.')+getStrStype1(comm+' logo'))
        printStrStype2('    制作logo.bin 如果要修改图片请将图片放入到xhl/logo目录(例如uboot.bmp或者xxx_uboot.bmp xxx表示选择的那个分辨率，xxx的图片优先)')
        print(getStrStype2('20.')+getStrStype1(comm+' cflag'))
        printStrStype2('    反编译smail时候转换flag值')
        print(getStrStype2('21.')+getStrStype1(comm+' rid path ')+getStrStype2('(path是app路径，会在该路径下查找所有的public.xml然后替换java中的资源id)'))
        printStrStype2('    反编译后java文件快速替换id为R.type.id')
        print(getStrStype2('22.')+getStrStype1(comm+' select'))
        printStrStype2('    列出参数选项，修改脚本默认选项')
        print(getStrStype2('23.')+getStrStype1(comm+' diff [-n src] [-o dst] [-m diff] [-p log]')+getStrStype2('（-n 指定新文件目录 -o 指定旧文件目录 -m 差异文件存放目录 -p 保存差异信息文件路径）'))
        print(getStrStype2('    对比两个文件目录差异 使用-p参数之执行对比查找输出差异到log文件中，如果不使用-p参数会将old文件目录中没有的文件添加，修改的文件放入到diff文件中'))
        print(getStrStype2('    默认src目录./src_dir 默认dst目录./dst_dir 默认diff目录./diff_dir 默认log文件diff_log.txt'))

        print(getStrStype2('\n\n    当前tool版本:')+getStrStype1('v'+xlan_tool_version)+getStrStype2('\n'))

if __name__ == '__main__':
    if len(argv) >1 and isdir(argv[1]):
        argv[0]='mm'
    else:
        del argv[0]

    if '--help' in argv or len(argv) == 0:
        Tool.printHelp()
    elif argv[0] == 'mm':
        if len(argv) > 1:
            module_path = Tool.getMmPath(argv[1])
            if module_path and isdir(module_path):
                argv[1] = module_path
        if not (len(argv) >1 and isdir(argv[1])):
            del argv[0]
        Tool.checkDriveList(False)
        Tool.mm(argv)
        if len(argv) == 0:
            Tool.buildimage()
    elif argv[0] == 'mmm':
        argv[0] = 'mm'
        Tool.checkDriveList(False)
        Tool.mm(argv, touchOut=False)
    elif argv[0] == 'buildimage':
        del argv[0]
        if '-e' in argv:
            Tool.SUPPORT_CUSTOMER = True
            del argv[argv.index('-e')]
        Tool.checkDriveList(False)
        Tool.buildimage(argv)
    elif argv[0] == 'build_boot':
        del argv[0]
        Tool.buildBootImage(argv)
    elif argv[0] == 'apktool':
        Tool.apktool()
    elif argv[0] == 'chgvalue':
        Tool.chgvalueFromUser()
    elif argv[0] == 'diff':
        Tool.diff(argv)
    elif argv[0] == 'patch':
        Tool.patch(False if '-x' in argv else True)
    elif argv[0] == 'cp':
        Tool.copyfiles(argv)
    elif argv[0] == 'svn_ci':
        Tool.svncommit(argv)
    elif argv[0] == 'svn_restore':
        del argv[0]
        Tool.svn_db_restore()
    elif argv[0] == 'svn_revert':
        del argv[0]
        Tool.svnrevert(argv[0] if len(argv)>0 else None)
    elif argv[0] == 'driver':
        del argv[0]
        Tool.checkDriveList(False)
        if Tool.BEFORE_LOLLIPOP:
            Tool.mm(['n', 'pl', 'lk', 'k'])
            Tool.mm(['bootimage',])
        else:
            Tool.mm(['clean-lk',])
            Tool.mm(['clean-kernel',])
            Tool.mm(['clean-preloader',])
            Tool.mm()
    elif argv[0] == 'driver_r':
        del argv[0]
        Tool.checkDriveList(False)
        if Tool.BEFORE_LOLLIPOP:
            Tool.mm(['r', 'lk', 'k'])
            Tool.mm(['bootimage',])
        else:
            Tool.mm(['clean-lk',])
            Tool.mm(['clean-kernel',])
            Tool.mm(['clean-preloader',])
            Tool.mm()
    elif argv[0] == 'svn_mm':
        Tool.checkDriveList(False)
        if not Tool.setAutoNew(argv) and not Tool.readParameters():
            Tool.setParameters()
        else:
            Tool.mAutoNew = True
        if len(argv) > 1:
            module_path = Tool.getMmPath(argv[1])
            if module_path and isdir(module_path):
                argv[1] = module_path
            if isdir(argv[1]):
                Tool.svnrevert(argv[1], rm_xhl = True)
        else:
            Tool.svnrevert('.', rm_xhl = True)
        Tool.checkSelect()
        Tool.copyDriverFiles()
        if not (len(argv) >1 and isdir(argv[1])):
            del argv[0]
        else:
            argv[0] = 'mm'
        Tool.mm(argv)
        if len(argv) == 0:
            Tool.buildimage()
    elif argv[0] == 'svn_new':
        del argv[0]
        Tool.svn_new()
    elif argv[0] == 'new_driver':
        del argv[0]
        Tool.checkDriveList(True)
        if not Tool.setAutoNew(argv) and not Tool.readParameters():
            Tool.setParameters()
        Tool.checkSelect()
        Tool.copyDriverFiles()
        if isdir(Tool.PRODUCT_DATA) and isdir(Tool.PRODUCT_SYSTEM):
            # 如果是android5.0之前老版本
            if Tool.BEFORE_LOLLIPOP:
                Tool.mm(['r', 'lk', 'k'])
                Tool.mm(['bootimage',])
            else:
                Tool.mm(['clean-lk',])
                Tool.mm(['clean-kernel',])
                Tool.mm(['clean-preloader',])
                Tool.mm()
        else:
            Tool.mm(['new',], keepOut = True)
        Tool.buildimage()
    elif argv[0] == 'new':
        keepOut = 'o' in argv or 'O' in argv
        Tool.checkDriveList(True)
        if not Tool.setAutoNew(argv) and not Tool.readParameters():
            Tool.setParameters()
        Tool.checkSelect()
        Tool.copyDriverFiles()
        Tool.mm(['new',], keepOut = keepOut)
        Tool.buildimage()
    elif argv[0] == 'logo':
        # 如果是android5.0之前老版本
        if Tool.BEFORE_LOLLIPOP:
            logo_path = sep.join(['mediatek','custom','common','lk','logo'])
            bmp_to_raw = sep.join([logo_path,'tool','bmp_to_raw'])
            zpipe = sep.join([logo_path,'tool','zpipe'])
            mkimage = sep.join(['mediatek','build','tools','images','mkimage'])
            img_hdr_logo_cfg = ''
            Tool.buildLogo(logo_path, bmp_to_raw, zpipe, mkimage, img_hdr_logo_cfg)
        else:
            logo_path = sep.join(['vendor','mediatek','proprietary','bootable','bootloader','lk','dev','logo'])
            bmp_to_raw = sep.join([logo_path,'tool','bmp_to_raw'])
            zpipe = sep.join([logo_path,'tool','zpipe'])
            mkimage = sep.join(['vendor','mediatek','proprietary','bootable','bootloader','lk','scripts','mkimage'])
            img_hdr_logo_cfg = sep.join([logo_path,'img_hdr_logo.cfg'])
            Tool.buildLogo(logo_path, bmp_to_raw, zpipe, mkimage,img_hdr_logo_cfg)
    elif argv[0] == 'cflag':
        Tool.computerFlag()
    elif argv[0] == 'rid':
        del argv[0]
        if len(argv) == 0 or not isdir(argv[0]):
            Tool.replaceId()
        else:
            Tool.replaceId(argv[0])
    elif argv[0] == 'select':
        Tool.select()
    elif argv[0] == 'all':
        Tool.showAppList()
    elif argv[0] == 'git':
        Tool.git(argv[1:])
    else:
        module_path = Tool.getMmPath(argv[0]) if len(argv) > 0 else ''
        if module_path and isdir(module_path):
            Tool.checkDriveList(False)
            Tool.mm(['mm', module_path])
        else:
            Tool.printHelp()
