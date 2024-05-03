package org.school.work.loadbalancer;

import org.school.work.model.ServiceMetaInfo;

import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * <p>Description: 轮询负载均衡器</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class RoundRobinLoadBalancer implements LoadBalancer{
    // 当前轮询的下标
    private final AtomicInteger currentIndex = new AtomicInteger(0);

    @Override
    public ServiceMetaInfo select(Map<String, Object> requestParams, List<ServiceMetaInfo> serviceMetaInfoList) {
        if(serviceMetaInfoList.isEmpty()){
            return null;
        }
        // 只有一个服务，不需要轮询
        int size = serviceMetaInfoList.size();
        if(size == 1){
            return serviceMetaInfoList.get(0);
        }
        // 取模算法轮询
        int index = currentIndex.getAndIncrement() % size;
        return serviceMetaInfoList.get(index);
    }
}