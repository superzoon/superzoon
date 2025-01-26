import pandas as pd
if __name__ == '__main__':

    # 创建示例 DataFrame
    df1 = pd.DataFrame({
        'Name': ['Alice', 'Bob'],
        'Age': [25, 30]
    })

    df2 = pd.DataFrame({
        'Name': ['Charlie', 'David'],
        'Age': [35, 40]
    })

    # 使用 concat 函数按行拼接
    result = pd.concat([df1, df2], ignore_index=True)

    print(result)