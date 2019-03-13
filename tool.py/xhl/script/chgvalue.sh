#!/bin/bash
#use1:  ./chgvalue.sh file name value1 value2 value3
#use2:  ./chgvalue.sh file name = value1 value2 value3
#use3:  ./chgvalue.sh file name := value1 value2 value3
#use4:  ./chgvalue.sh file name += value1 value2 value3

F="$1"
N="$2"
S="$3"
SS=$S

shift
shift

if [ "${S}" == "=" ]
then
shift
elif [ "${S}" == ":=" ]
then
SS=" := "
shift
elif [ "${S}" == "+=" ]
then
SS=" += "
shift
else
S="="
SS=$S
fi

V="$*"

CMD="grep -c ^${N}\s*${S} ${F}"
if [ $($CMD) -eq 0 ]
then
echo $CMD
echo "${N}${SS}${V}" >>  ${F}
else
FV=`echo "${V}" | sed "s/\//\\\\\\\\\//g"`
echo "$N=$FV"
sed "s/^${N}\s*${S}\s*.*/${N}${SS}${FV}/" ${F} > ${F}.temp
if [ `wc -c < ${F}.temp` -gt 1 ]
then
mv -f ${F}.temp ${F} 
fi
fi
exit 0;

