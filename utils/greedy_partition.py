import random

from env import USERS_IN_REGION, ENV
import h3
import heapq


# 日后怎么删除这些users
def load_users_in_region(current_users):
    for current_user in current_users:
        lat, lon = current_user.start_latitude, current_user.start_longitude
        USERS_IN_REGION[h3.geo_to_h3(lat, lon)].add(current_user)


def find_nearby_hexagons(hex_index, k=1, min_lat=None, max_lat=None, min_lng=None, max_lng=None, seen=None):
    nearby_hexagons = h3.k_ring(hex_index, k)
    filtered_hexagons = set()

    for h3_index in nearby_hexagons:
        lat, lng = h3.h3_to_geo(h3_index)
        if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
            if h3_index not in seen:
                filtered_hexagons.add(h3_index)

    return filtered_hexagons


def heuristic_partition(current_users):
    load_users_in_region(current_users)
    pq = []
    regions = []
    seen = set()

    for key, set_s in USERS_IN_REGION.items():
        heapq.heappush(pq, (len(set_s), key))

    while pq:
        temp_cnt, temp_idx, = heapq.heappop(pq)
        if temp_idx in seen:
            continue

        if temp_cnt > 50:
            seen.add(temp_idx)
            regions.append([temp_idx])
            continue
        else:
            cnt = temp_cnt
            idxes = [temp_idx]
            while cnt < 50:
                k = 1
                idx_set = find_nearby_hexagons(temp_idx, k, ENV['min_lat'], ENV['max_lat'], ENV['min_lng'],
                                               ENV['max_lng'], seen=seen)
                temp_pq = [(len(USERS_IN_REGION[idx]), idx) for idx in idx_set]
                if temp_pq:
                    heapq.heapify(temp_pq)
                    while temp_pq and cnt + temp_pq[0][0] < 50:
                        temp_cnt, temp_idx = heapq.heappop(temp_pq)
                        cnt += temp_cnt
                        idxes.append(temp_idx)
                    k += 1
                else:
                    break
        regions.append(idxes)
    return regions
