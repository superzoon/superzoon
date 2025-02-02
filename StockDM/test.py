import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 示例 losses 数组，你可以将其替换
def 你好(name: str = 'world'):
    print('{}, time={}'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
if __name__ == '__main__':
    import pandas as pd

    # 创建示例DataFrame
    df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    df2 = pd.DataFrame({'A': [7, 8, 9], 'B': [10, 11, 12]})

    # 按行拼接DataFrame
    result = pd.concat([df1, df2], axis=0)

    # 打印拼接后的结果
    print(result)

    for i in range(5):
        print(i)