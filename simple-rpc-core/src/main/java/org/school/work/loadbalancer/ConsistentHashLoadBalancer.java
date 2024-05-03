package org.school.work.loadbalancer;

import org.school.work.model.ServiceMetaInfo;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * <p>Description: 一致性哈希负载均衡器</p >
 * <p>Copyright: Copyright (c)2024</p >
 * <P>Created Date: 2024年05月03日</P>
 *
 * @author LiuYuHan
 * @version 1.0
 */
public class ConsistentHashLoadBalancer implements LoadBalancer{
    // 一致性Hash环，存放虚拟阶段
    private final TreeMap<Integer, ServiceMetaInfo> virtualNodes = new TreeMap<>();
    // 虚拟节点数
    private static final int VIRTUAL_NODE_NUM = 100;

    @Override
    public ServiceMetaInfo select(Map<String, Object> requestParams, List<ServiceMetaInfo> serviceMetaInfoList) {
        if (serviceMetaInfoList.isEmpty()){
            return null;
        }

        // 构建虚拟节点环
        for (ServiceMetaInfo serviceMetaInfo : serviceMetaInfoList){
            for (int i=0; i<VIRTUAL_NODE_NUM; i++){
                int hash = getHash(serviceMetaInfo.getServiceAddress() + "#" + i);
                virtualNodes.put(hash, serviceMetaInfo);
            }
        }

        // 获取调用请求的hash值
        int hash = getHash(requestParams);

        // 选择最接近且大于调用请求hash值的虚拟节点
        Map.Entry<Integer, ServiceMetaInfo> entry = virtualNodes.ceilingEntry(hash);
        if (entry == null){
            // 如果没有大于等于调用请求hash值的虚拟节点，则返回首部的节点
            entry = virtualNodes.firstEntry();
        }
        return entry.getValue();
    }

    /**
     * Hash算法，可修改
     */
    private int getHash(Object key){
        return key.hashCode();
    }
}