from test import test_result_bi
from train import train


def main():
    train()
    print('xxx')
    test_result_bi('D:\\cmq\\PII-II model\\csdn-renren_test.csv',100,1000)


if __name__ == "__main__":
    main()

