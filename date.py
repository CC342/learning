import datetime
import cnlunar
from cnlunar.holidays import legalHolidaysDic, legalLunarHolidaysDic, otherHolidaysList, otherLunarHolidaysList

# 获取今天的日期
today = datetime.datetime.today()

# 获取今天日期的农历信息
a = cnlunar.Lunar(today)

# 判断是否是法定节假日
def check_legal_holiday(date):
    # 判断阳历节假日
    if (date.month, date.day) in legalHolidaysDic:
        return legalHolidaysDic[(date.month, date.day)]
    
    # 判断农历节假日
    lunar_month_day = (a.lunarMonth, a.lunarDay)
    if lunar_month_day in legalLunarHolidaysDic:
        return legalLunarHolidaysDic[lunar_month_day]
    
    # 判断其他节假日
    for month_day_dict in otherHolidaysList:
        if date.month in month_day_dict and date.day == month_day_dict[date.month]:
            return month_day_dict[date.month]
    
    return None  # 没有节假日

# 判断是否是其他农历节假日
def check_other_lunar_holiday(date):
    lunar_month_day = (a.lunarMonth, a.lunarDay)
    for month_day_dict in otherLunarHolidaysList:
        if lunar_month_day in month_day_dict:
            return month_day_dict[lunar_month_day]
    return None  # 没有其他农历节假日

# 获取今天的节假日信息
legal_holiday = check_legal_holiday(today)
other_lunar_holiday = check_other_lunar_holiday(today)

# 获取农历信息
dic = {
    '日期': today.strftime('%Y-%m-%d'),  # 只显示日期部分
    '农历': '%s %s[%s]年 %s%s' % (a.lunarYearCn, a.year8Char, a.chineseYearZodiac, a.lunarMonthCn, a.lunarDayCn),
}

# 只在有节气时添加节气信息
if a.todaySolarTerms and a.todaySolarTerms != "无":
    dic['节气'] = a.todaySolarTerms

# 只在有节假日时添加相关信息
if legal_holiday:
    dic['法定节假日'] = legal_holiday
if other_lunar_holiday:
    dic['其他农历节假日'] = other_lunar_holiday

# 打印农历、节气和节假日信息
for key, value in dic.items():
    print(key, ':', value)

