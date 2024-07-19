\ Model vehicle_dispatch
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  4.782041840450196 x[0,0] + 1.912816736179807 x[0,1] + 7.651266944720586 y[0,0,1] + 4.782041840450196 y[0,1,0] + 7741.834135817172 z[0,0] + 7743.22563317293 z[0,1]
Subject To
 empty_car_assignment[0]: y[0,0,1] + y[0,1,0] - 2 b[0] = 0
 empty_car_one_user[0]: x[0,0] + x[0,1] <= 1
 car_one_sharing[0]: z[0,0] + z[0,1] <= 1
 user_one_vehicle[0]: x[0,0] + y[0,0,1] + y[0,1,0] + z[0,0] = 1
 user_one_vehicle[1]: x[0,1] + y[0,0,1] + y[0,1,0] + z[0,1] = 1
 car_at_least_one_user[0]: x[0,0] + x[0,1] + y[0,0,1] + y[0,1,0] - b[0]
   >= 0
 linearization1[0,0,1]: - x[0,0] + y[0,0,1] <= 0
 linearization1[0,1,0]: - x[0,1] + y[0,1,0] <= 0
 linearization2[0,0,1]: - x[0,1] + y[0,0,1] <= 0
 linearization2[0,1,0]: - x[0,0] + y[0,1,0] <= 0
 linearization3[0,0,1]: - x[0,0] - x[0,1] + y[0,0,1] >= -1
 linearization3[0,1,0]: - x[0,0] - x[0,1] + y[0,1,0] >= -1
Bounds
Binaries
 x[0,0] x[0,1] y[0,0,0] y[0,0,1] y[0,1,0] y[0,1,1] z[0,0] z[0,1] b[0]
End
