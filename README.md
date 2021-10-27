# SingleAutonomous
Autonomous flying of a single Crazyflie with the Multi-ranger.

# Examples
## distance_measure
A quite simple demo to read the distance measured by the multi-ranger, and output the log into the files for further analysis. 
The result shows that the sensor on the multi-ranger is accurate enough for basic autonomous flying, the error is less than 2cm within 3m.
What's more, the fluctuation is stable and the sensor is very sensetive for the obstacles entering the FoV.

## static_barrier
The example is from the Bitcraze official, a simple application to allow the Crazyflie stay away from the hand (obstacle) and fly toward the opposite direction.

## point_cloud
The example is also form the Bitcraze official, an applicaiton to draw the 3-D point cloud with the Flow Deck. The point cloud is the basics of SLAM.

## lidar_array
We know that the output 