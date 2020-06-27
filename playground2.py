from matplotlib import pyplot as plt
import numpy as np
days = [0, 1, 2, 3, 4, 5, 6]
money_spent = [10, 12, 12, 10, 14, 22, 24]
money_spent_2 = [11, 14, 15, 15, 22, 21, 12]


plt.plot(days, money_spent)
plt.plot(days, money_spent_2)
# 화면에 그래프를 보여줍니다
plt.show()