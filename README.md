### procedure

1. initialize all of vehicles on the city, generate the requests based on the record from 滴滴 and init the map of chengdu.
2. in every timestamp (like 2 seconds), update vehicle's request and current situation (like, current position, if accecpt request, if accecpt car sharing, etc.).



初始化成都地图和路网，出租车的位置，根据历史的订单的记录来模拟。

每间隔delta （如10秒） 时间，收集下当前车辆行驶情况，和10秒内的订单，进行车辆分配。订单分配完成之后，车辆就开始运行10秒。



车最多只坐2个人

拼车行为如下：

1. 两个人同时在10秒钟打车，并且决定拼单，那么车先接A，再接B，再送A，再送B。
2. 一个愿意拼车A的人正在车上，车已经启动，突然又收到一个拼车订单B，于是从现在位置出发，去接B，送A，再送B
3. 一个人从开始坐到结束，没有拼车。

可以决策的部分是：

1. 在间隔时间内产生的订单，哪个车去接哪个人？是否与别人拼车？谁和谁拼车？

求两个目的地之间的距离采用调用API，使用dijkstra算法，复杂度较高。想尽可能少的调用。