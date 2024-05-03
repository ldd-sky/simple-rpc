package org.school.work.loadbalancer;

import org.school.work.model.ServiceMetaInfo;

import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * <p>Description: 随机负载均衡器</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class RandomLoadBalancer implements LoadBalancer{
    private final Random random = new Random();

    @Override
    public ServiceMetaInfo select(Map<String, Object> requestParams, List<ServiceMetaInfo> serviceMetaInfoList) {
        int size = serviceMetaInfoList.size();
        if(size == 0){
            return null;
        }
        if (size == 1){
            return serviceMetaInfoList.get(0);
        }
        return serviceMetaInfoList.get(random.nextInt(size));
    }
}