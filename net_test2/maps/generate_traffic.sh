/usr/share/sumo/tools/randomTrips.py -n /home/przemek/Desktop/sumo/traffic-lights-ai/net_test2/maps/map.net.xml -o /home/przemek/Desktop/sumo/traffic-lights-ai/net_test2/maps/flows.xml --begin 0 --end 1 --period 1 --flows 3000
jtrrouter --flow-files=flows.xml --net-file=map.net.xml --output-file=map.rou.xml --begin 0 --end 10000 --accept-all-destinations
