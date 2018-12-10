from test import test_result_pkl
from train import train


def main():
    train('dataset\\taobao-12306_train.pkl')
    print('xxx')
    test_result_pkl('dataset\\taobao-12306_test.pkl',100,1000)


if __name__ == "__main__":
    main()

